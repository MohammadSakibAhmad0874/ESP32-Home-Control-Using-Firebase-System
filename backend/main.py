"""
HomeControl — Self-Hosted Backend
FastAPI app with JWT auth, PostgreSQL, WebSocket real-time sync for ESP32,
Smart Schedules, and Power Usage tracking.
"""
import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import (
    Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect,
    status, Query
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from auth import create_access_token, hash_password, verify_password, decode_token
from database import get_db, init_db, AsyncSessionLocal
from models import Device, Relay, User, Schedule, PowerLog, PreRegisteredDevice

# ── WebSocket connection manager ─────────────────────────────────────────────

class ConnectionManager:
    """Manages WebSocket connections for both the ESP32 device and browser dashboards."""

    def __init__(self):
        # device_id → ESP32 WebSocket (one per device)
        self.esp_connections: Dict[str, WebSocket] = {}
        # device_id → set of browser dashboard WebSockets
        self.dashboard_connections: Dict[str, set] = {}

    async def connect_esp(self, device_id: str, ws: WebSocket):
        await ws.accept()
        self.esp_connections[device_id] = ws

    async def connect_dashboard(self, device_id: str, ws: WebSocket):
        await ws.accept()
        if device_id not in self.dashboard_connections:
            self.dashboard_connections[device_id] = set()
        self.dashboard_connections[device_id].add(ws)

    def disconnect_esp(self, device_id: str):
        self.esp_connections.pop(device_id, None)

    def disconnect_dashboard(self, device_id: str, ws: WebSocket):
        if device_id in self.dashboard_connections:
            self.dashboard_connections[device_id].discard(ws)

    async def send_to_esp(self, device_id: str, data: dict) -> bool:
        """Send relay command to ESP32. Returns True if sent."""
        ws = self.esp_connections.get(device_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
                return True
            except Exception:
                self.disconnect_esp(device_id)
        return False

    async def broadcast_to_dashboards(self, device_id: str, data: dict):
        """Push state update to all browser tabs watching this device."""
        sockets = self.dashboard_connections.get(device_id, set()).copy()
        dead = set()
        for ws in sockets:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.dashboard_connections[device_id].discard(ws)


manager = ConnectionManager()

# ── Schedule Executor Background Task ────────────────────────────────────────

# Track already-fired schedules this minute to avoid double-firing
_fired_this_minute: set = set()

DAY_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}


async def schedule_executor():
    """
    Runs every 30 seconds. Checks all enabled schedules and fires relay
    commands if the current time matches. Uses a 'fired this minute' set
    to avoid double-triggering.
    """
    last_minute = ""
    while True:
        await asyncio.sleep(30)
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = DAY_MAP[now.weekday()]

            # Reset fired set at the top of a new minute
            if current_time != last_minute:
                _fired_this_minute.clear()
                last_minute = current_time

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Schedule).where(Schedule.enabled == True)  # noqa: E712
                )
                schedules = result.scalars().all()

                for sched in schedules:
                    # Check time match
                    if sched.time != current_time:
                        continue

                    # Check day match
                    days_list = [d.strip() for d in sched.days.split(",")]
                    if "all" not in days_list and current_day not in days_list:
                        continue

                    # Avoid double-firing in the same minute
                    fire_key = f"{sched.id}:{current_time}"
                    if fire_key in _fired_this_minute:
                        continue
                    _fired_this_minute.add(fire_key)

                    # Fire the relay
                    new_state = (sched.action == "on")
                    device_id = sched.device_id
                    relay_key = sched.relay_key

                    # Update DB
                    relay_result = await db.execute(
                        select(Relay).where(
                            Relay.device_id == device_id,
                            Relay.relay_key == relay_key
                        )
                    )
                    relay = relay_result.scalar_one_or_none()
                    if relay:
                        old_state = relay.state
                        relay.state = new_state

                        # Log power change
                        db.add(PowerLog(
                            device_id=device_id,
                            relay_key=relay_key,
                            state=new_state,
                            timestamp=int(time.time()),
                        ))
                        await db.commit()

                    # Push to ESP32 over WebSocket
                    await manager.send_to_esp(device_id, {
                        "type": "relay_cmd",
                        relay_key: new_state
                    })

                    # Push to dashboards
                    await manager.broadcast_to_dashboards(device_id, {
                        "type": "relay_update",
                        "relay_key": relay_key,
                        "state": new_state,
                        "source": f"schedule:{sched.label or sched.id[:8]}"
                    })

        except Exception as e:
            print(f"[ScheduleExecutor] Error: {e}")


# ── App lifecycle ─────────────────────────────────────────────────────────────

# ── Pre-registered device IDs to auto-seed on startup ────────────────────────
PRE_REGISTERED_SEEDS = [
    # Admin device
    {"device_id": "ADMIN01",   "label": "Admin Device",   "num_switches": 4},
    # Registered user devices
    {"device_id": "AMAN780",   "label": "Aman Device",    "num_switches": 4},
    {"device_id": "NIKHIL567", "label": "Nikhil Device",  "num_switches": 4},
    {"device_id": "MICK345",   "label": "Mick Device",    "num_switches": 4},
]

async def seed_pre_registered_devices():
    """Sync the database pre_registered_devices table to match PRE_REGISTERED_SEEDS.
    - Inserts new seed entries that don't exist yet.
    - Deletes old unclaimed entries that are no longer in the seed list.
    """
    async with AsyncSessionLocal() as db:
        seed_ids = {entry["device_id"] for entry in PRE_REGISTERED_SEEDS}

        # ── Remove old unclaimed devices no longer in the seed list ────────
        all_pre = await db.execute(select(PreRegisteredDevice))
        for pre in all_pre.scalars().all():
            if pre.device_id not in seed_ids and not pre.is_claimed:
                await db.delete(pre)
                print(f"[Startup] Removed old pre-registered device: {pre.device_id}")

        # ── Insert new seed entries if they don't exist yet ────────────────
        for entry in PRE_REGISTERED_SEEDS:
            existing = await db.execute(
                select(PreRegisteredDevice).where(
                    PreRegisteredDevice.device_id == entry["device_id"]
                )
            )
            if not existing.scalar_one_or_none():
                db.add(PreRegisteredDevice(
                    device_id=entry["device_id"],
                    label=entry["label"],
                    num_switches=entry["num_switches"],
                    is_claimed=False,
                    created_at=int(time.time()),
                ))
                print(f"[Startup] Seeded new pre-registered device: {entry['device_id']}")

        await db.commit()
        print("[Startup] Pre-registered device seeds synced.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_pre_registered_devices()
    # Start the background schedule executor
    task = asyncio.create_task(schedule_executor())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="HomeControl API", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ── Auth helpers ──────────────────────────────────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    device_id: str
    email: str
    password: str
    num_switches: int = 4
    switch_names: list[str] = []

class ClaimDeviceRequest(BaseModel):
    """Used by users to claim a pre-registered device ID and set their password."""
    name: str
    device_id: str
    email: str
    password: str
    num_switches: Optional[int] = None   # If None, use the pre-registered default
    switch_names: list[str] = []

class SeedDeviceRequest(BaseModel):
    """Admin: add a new pre-registered device ID."""
    device_id: str
    label: str = ""
    num_switches: int = 4

class LoginRequest(BaseModel):
    device_id: str
    password: str

class AdminLoginRequest(BaseModel):
    """Admin login by email + password (no device_id needed)."""
    email: str
    password: str

class RelayToggleRequest(BaseModel):
    state: bool

class RelayRenameRequest(BaseModel):
    name: str

class WattageUpdateRequest(BaseModel):
    wattage: float  # Watts

class ScheduleCreateRequest(BaseModel):
    relay_key: str
    action: str      # "on" or "off"
    time: str        # "HH:MM"
    days: str        # "Mon,Tue" or "all"
    enabled: bool = True
    label: str = ""

class ScheduleUpdateRequest(BaseModel):
    relay_key: Optional[str] = None
    action: Optional[str] = None
    time: Optional[str] = None
    days: Optional[str] = None
    enabled: Optional[bool] = None
    label: Optional[str] = None

# ── Auth endpoints ────────────────────────────────────────────────────────────

# ── Public: Check if a device ID is available to claim ───────────────────────
@app.get("/api/devices/check/{device_id}")
async def check_device_id(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Public endpoint. Returns the status of a pre-registered device ID.
    Used by the web "Claim" form to validate the device ID before showing the full form.
    """
    device_id = device_id.upper().strip()
    result = await db.execute(
        select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
    )
    pre = result.scalar_one_or_none()
    if not pre:
        raise HTTPException(404, "Device ID not found. Please check the ID or contact support.")
    if pre.is_claimed:
        raise HTTPException(409, "This Device ID has already been registered. Please login instead.")
    return {
        "device_id": pre.device_id,
        "label": pre.label,
        "num_switches": pre.num_switches,
        "is_claimed": pre.is_claimed,
    }


# ── Public: Claim a pre-registered device ─────────────────────────────────────
@app.post("/api/auth/claim")
async def claim_device(req: ClaimDeviceRequest, db: AsyncSession = Depends(get_db)):
    """
    User claims a pre-registered device ID, sets their own password.
    This replaces the old open registration flow.
    """
    device_id = req.device_id.upper().strip()
    if not device_id:
        raise HTTPException(400, "Device ID is required")
    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    # Check it is a pre-registered, unclaimed device
    pre_result = await db.execute(
        select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
    )
    pre = pre_result.scalar_one_or_none()
    if not pre:
        raise HTTPException(400, "Device ID not found. It must be pre-registered by the admin.")
    if pre.is_claimed:
        raise HTTPException(400, "This Device ID is already claimed. Please login instead.")

    # Check no Device record exists yet (double-safety)
    existing_dev = await db.execute(select(Device).where(Device.device_id == device_id))
    if existing_dev.scalar_one_or_none():
        raise HTTPException(400, f'Device ID "{device_id}" already registered.')

    # Check email uniqueness
    existing_user = await db.execute(select(User).where(User.email == req.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    now = int(time.time())
    user_id = str(uuid.uuid4())
    # Use the pre-registered switch count unless the user overrides
    num_switches = req.num_switches if req.num_switches is not None else pre.num_switches
    default_names = ["Living Room", "Bedroom", "Kitchen", "Fan",
                     "Switch 5", "Switch 6", "Switch 7", "Switch 8"]

    # Create device
    device = Device(
        device_id=device_id,
        owner_name=req.name,
        email=req.email,
        num_switches=num_switches,
        online=False,
        last_seen=now,
        created_at=now,
    )
    db.add(device)
    await db.flush()

    # Create relays
    for i in range(1, num_switches + 1):
        key = f"relay{i}"
        name = (req.switch_names[i - 1] if i <= len(req.switch_names)
                else default_names[i - 1] if i <= len(default_names)
                else f"Switch {i}")
        db.add(Relay(device_id=device_id, relay_key=key, name=name, state=False, wattage=60.0))

    # Create user linked to this device
    user = User(
        id=user_id,
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        device_id=device_id,
        is_admin=False,
        created_at=now,
    )
    db.add(user)

    # Mark pre-registered device as claimed
    pre.is_claimed = True

    await db.commit()

    token = create_access_token({"sub": user_id})
    return {"token": token, "device_id": device_id, "name": req.name}


# ── Public: ESP32 auto-token endpoint ─────────────────────────────────────────
@app.get("/api/esp/connect/{device_id}")
async def esp_get_token(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Called by ESP32 on boot to fetch its JWT token automatically.
    No password needed — the device_id is the identity. Returns a token
    scoped to the device's owner user. If device is not yet claimed, returns 503
    so the ESP32 can retry later (device will work once the user registers online).
    """
    device_id = device_id.upper().strip()

    # Find the device
    dev_result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = dev_result.scalar_one_or_none()
    if not device:
        # Check if it's pre-registered but not yet claimed
        pre_result = await db.execute(
            select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
        )
        pre = pre_result.scalar_one_or_none()
        if pre:
            raise HTTPException(
                status_code=503,
                detail="Device not yet claimed. Please register on the dashboard first."
            )
        raise HTTPException(404, "Device ID not found.")

    # Find owner user
    user_result = await db.execute(
        select(User).where(User.device_id == device_id)
    )
    owner = user_result.scalar_one_or_none()
    if not owner:
        raise HTTPException(503, "Device has no owner yet. Please register on the dashboard.")

    token = create_access_token({"sub": owner.id})
    return {
        "token": token,
        "device_id": device_id,
        "name": owner.name,
        "num_switches": device.num_switches,
    }


@app.post("/api/auth/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Legacy / admin-level registration. Now validates that the device_id
    is pre-registered (or creates it if admin). Kept for backward compatibility.
    """
    device_id = req.device_id.upper().strip()
    if not device_id:
        raise HTTPException(400, "Device ID is required")

    # Check the device_id is pre-registered
    pre_result = await db.execute(
        select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
    )
    pre = pre_result.scalar_one_or_none()
    if pre and pre.is_claimed:
        raise HTTPException(400, f'Device ID "{device_id}" is already claimed. Please use login.')
    if not pre:
        raise HTTPException(
            400,
            f'Device ID "{device_id}" is not a registered device. '
            'Please use a pre-registered Device ID provided to you, '
            'or use the Claim Device tab.'
        )

    # Check device record uniqueness
    existing = await db.execute(select(Device).where(Device.device_id == device_id))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f'Device ID "{device_id}" already exists')

    # Check email uniqueness
    existing_user = await db.execute(select(User).where(User.email == req.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    now = int(time.time())
    user_id = str(uuid.uuid4())
    num_switches = req.num_switches
    default_names = ["Living Room", "Bedroom", "Kitchen", "Fan",
                     "Switch 5", "Switch 6", "Switch 7", "Switch 8"]

    # Create device
    device = Device(
        device_id=device_id,
        owner_name=req.name,
        email=req.email,
        num_switches=num_switches,
        online=False,
        last_seen=now,
        created_at=now,
    )
    db.add(device)
    await db.flush()

    # Create relays
    for i in range(1, num_switches + 1):
        key = f"relay{i}"
        name = (req.switch_names[i - 1] if i <= len(req.switch_names)
                else default_names[i - 1] if i <= len(default_names)
                else f"Switch {i}")
        db.add(Relay(device_id=device_id, relay_key=key, name=name, state=False, wattage=60.0))

    # Create user
    user = User(
        id=user_id,
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        device_id=device_id,
        is_admin=False,
        created_at=now,
    )
    db.add(user)

    # Mark pre-registered as claimed
    if pre:
        pre.is_claimed = True

    await db.commit()

    token = create_access_token({"sub": user_id})
    return {"token": token, "device_id": device_id, "name": req.name}


@app.post("/api/auth/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    device_id = req.device_id.upper().strip()

    # Look up device to get email
    device_result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(400, "Device ID not found")

    # Look up user by email
    result = await db.execute(select(User).where(User.email == device.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Incorrect password")

    token = create_access_token({"sub": user.id})
    return {"token": token, "device_id": device_id, "name": user.name, "is_admin": user.is_admin}


@app.post("/api/auth/admin-login")
async def admin_login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Admin login by email + password.
    Only succeeds if the user with that email is an admin.
    Useful for the admin who claimed ADMIN01 and wants to log in with their email.
    """
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    if not user.is_admin:
        raise HTTPException(403, "This account does not have admin access")
    token = create_access_token({"sub": user.id})
    return {
        "token": token,
        "device_id": user.device_id,
        "name": user.name,
        "is_admin": True,
    }


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str
    admin_secret: str


@app.post("/api/auth/reset-admin-password")
async def reset_admin_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Temporary admin password reset via ADMIN_SECRET.
    Requires the ADMIN_SECRET env var to be set and matched.
    Only works for admin users.
    """
    admin_secret_env = os.environ.get("ADMIN_SECRET", "")
    if not admin_secret_env or req.admin_secret != admin_secret_env:
        raise HTTPException(403, "Invalid or missing admin secret")

    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User with that email not found")
    if not user.is_admin:
        raise HTTPException(403, "That user is not an admin")

    user.hashed_password = hash_password(req.new_password)
    await db.commit()
    return {"success": True, "message": f"Password reset for {user.name} ({user.email})"}


@app.get("/api/auth/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "device_id": user.device_id,
        "is_admin": user.is_admin,
    }

# ── Device endpoints ──────────────────────────────────────────────────────────

@app.get("/api/devices/{device_id}")
async def get_device(
    device_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Users can only read their own device (admins can read any)
    if not user.is_admin and user.device_id != device_id.upper():
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Device).options(selectinload(Device.relays))
        .where(Device.device_id == device_id.upper())
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "Device not found")

    return _device_to_dict(device)


@app.post("/api/devices/{device_id}/relay/{relay_key}")
async def toggle_relay(
    device_id: str,
    relay_key: str,
    req: RelayToggleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Relay).where(Relay.device_id == device_id, Relay.relay_key == relay_key)
    )
    relay = result.scalar_one_or_none()
    if not relay:
        raise HTTPException(404, "Relay not found")

    old_state = relay.state
    relay.state = req.state

    # Log the power state change (for usage tracking)
    if old_state != req.state:
        db.add(PowerLog(
            device_id=device_id,
            relay_key=relay_key,
            state=req.state,
            timestamp=int(time.time()),
        ))

    await db.commit()

    # Push to ESP32 over WebSocket
    await manager.send_to_esp(device_id, {
        "type": "relay_cmd",
        relay_key: req.state
    })

    # Push to all dashboards watching this device
    await manager.broadcast_to_dashboards(device_id, {
        "type": "relay_update",
        "relay_key": relay_key,
        "state": req.state
    })

    return {"success": True, "relay_key": relay_key, "state": req.state}


@app.put("/api/devices/{device_id}/relay/{relay_key}/rename")
async def rename_relay(
    device_id: str,
    relay_key: str,
    req: RelayRenameRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Relay).where(Relay.device_id == device_id, Relay.relay_key == relay_key)
    )
    relay = result.scalar_one_or_none()
    if not relay:
        raise HTTPException(404, "Relay not found")

    relay.name = req.name
    await db.commit()
    return {"success": True}


@app.put("/api/devices/{device_id}/relay/{relay_key}/wattage")
async def update_wattage(
    device_id: str,
    relay_key: str,
    req: WattageUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set the wattage for a relay (used in power usage estimation)."""
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Relay).where(Relay.device_id == device_id, Relay.relay_key == relay_key)
    )
    relay = result.scalar_one_or_none()
    if not relay:
        raise HTTPException(404, "Relay not found")

    relay.wattage = max(1.0, min(req.wattage, 10000.0))  # clamp 1W–10kW
    await db.commit()
    return {"success": True, "wattage": relay.wattage}

# ── Schedule endpoints ────────────────────────────────────────────────────────

@app.get("/api/devices/{device_id}/schedules")
async def get_schedules(
    device_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Schedule).where(Schedule.device_id == device_id)
        .order_by(Schedule.created_at)
    )
    schedules = result.scalars().all()
    return [_schedule_to_dict(s) for s in schedules]


@app.post("/api/devices/{device_id}/schedules")
async def create_schedule(
    device_id: str,
    req: ScheduleCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    # Validate action
    if req.action not in ("on", "off"):
        raise HTTPException(400, "action must be 'on' or 'off'")

    # Validate time format HH:MM
    try:
        h, m = req.time.split(":")
        assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except Exception:
        raise HTTPException(400, "time must be in HH:MM format (24h)")

    sched = Schedule(
        id=str(uuid.uuid4()),
        device_id=device_id,
        relay_key=req.relay_key,
        action=req.action,
        time=req.time,
        days=req.days,
        enabled=req.enabled,
        label=req.label,
        created_at=int(time.time()),
    )
    db.add(sched)
    await db.commit()
    return _schedule_to_dict(sched)


@app.put("/api/devices/{device_id}/schedules/{schedule_id}")
async def update_schedule(
    device_id: str,
    schedule_id: str,
    req: ScheduleUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.device_id == device_id)
    )
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(404, "Schedule not found")

    if req.relay_key is not None:
        sched.relay_key = req.relay_key
    if req.action is not None:
        if req.action not in ("on", "off"):
            raise HTTPException(400, "action must be 'on' or 'off'")
        sched.action = req.action
    if req.time is not None:
        sched.time = req.time
    if req.days is not None:
        sched.days = req.days
    if req.enabled is not None:
        sched.enabled = req.enabled
    if req.label is not None:
        sched.label = req.label

    await db.commit()
    return _schedule_to_dict(sched)


@app.delete("/api/devices/{device_id}/schedules/{schedule_id}")
async def delete_schedule(
    device_id: str,
    schedule_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.device_id == device_id)
    )
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(404, "Schedule not found")

    await db.delete(sched)
    await db.commit()
    return {"success": True}

# ── Power Usage endpoints ─────────────────────────────────────────────────────

@app.get("/api/devices/{device_id}/power")
async def get_power_usage(
    device_id: str,
    days: int = Query(default=7, ge=1, le=30),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns per-relay power usage for the last N days.
    Calculates kWh using ON-time intervals from PowerLog, wattage from Relay.
    Also returns estimated cost at ₹8/kWh (Indian average rate).
    """
    device_id = device_id.upper()
    if not user.is_admin and user.device_id != device_id:
        raise HTTPException(403, "Access denied")

    # Get relay info (names, wattages)
    relay_result = await db.execute(
        select(Relay).where(Relay.device_id == device_id)
    )
    relays = {r.relay_key: r for r in relay_result.scalars().all()}

    # Get power logs for last N days
    since_ts = int(time.time()) - (days * 86400)
    log_result = await db.execute(
        select(PowerLog)
        .where(PowerLog.device_id == device_id, PowerLog.timestamp >= since_ts)
        .order_by(PowerLog.relay_key, PowerLog.timestamp)
    )
    logs = log_result.scalars().all()

    # Group logs by relay_key
    logs_by_relay: Dict[str, list] = {}
    for log in logs:
        logs_by_relay.setdefault(log.relay_key, []).append(log)

    now_ts = int(time.time())
    RATE_PER_KWH = 8.0  # ₹ per kWh (Indian average)

    result_data = {}
    total_kwh = 0.0
    total_cost = 0.0

    for relay_key, relay in relays.items():
        relay_logs = logs_by_relay.get(relay_key, [])
        wattage = relay.wattage or 60.0

        # Calculate ON-time in seconds
        on_seconds = 0.0
        on_start = None

        # If relay is currently ON, pretend there's a synthetic log at `since_ts`
        for log in relay_logs:
            if log.state:  # Turned ON
                on_start = log.timestamp
            else:  # Turned OFF
                if on_start is not None:
                    on_seconds += log.timestamp - on_start
                    on_start = None

        # If still ON at end of window
        if on_start is not None:
            on_seconds += now_ts - on_start

        hours_on = on_seconds / 3600.0
        kwh = (wattage * hours_on) / 1000.0
        cost = kwh * RATE_PER_KWH
        total_kwh += kwh
        total_cost += cost

        result_data[relay_key] = {
            "name": relay.name,
            "wattage": wattage,
            "hours_on": round(hours_on, 2),
            "kwh": round(kwh, 3),
            "cost_inr": round(cost, 2),
        }

    # Build daily breakdown (last 7 days) for chart
    import math
    daily_breakdown = []
    for day_offset in range(days - 1, -1, -1):
        day_start = int(time.time()) - (day_offset + 1) * 86400
        day_end = day_start + 86400
        day_label = datetime.fromtimestamp(day_start).strftime("%b %d")

        day_kwh_by_relay = {}
        for relay_key, relay in relays.items():
            relay_logs = logs_by_relay.get(relay_key, [])
            wattage = relay.wattage or 60.0
            on_seconds = 0.0
            on_start_day = None

            for log in relay_logs:
                if log.timestamp < day_start or log.timestamp > day_end:
                    continue
                if log.state:
                    on_start_day = log.timestamp
                else:
                    if on_start_day is not None:
                        on_seconds += log.timestamp - on_start_day
                        on_start_day = None

            if on_start_day is not None:
                on_seconds += min(day_end, now_ts) - on_start_day

            hours_on = on_seconds / 3600.0
            kwh = (wattage * hours_on) / 1000.0
            day_kwh_by_relay[relay_key] = round(kwh, 3)

        daily_breakdown.append({
            "date": day_label,
            "relays": day_kwh_by_relay,
            "total_kwh": round(sum(day_kwh_by_relay.values()), 3),
        })

    return {
        "device_id": device_id,
        "period_days": days,
        "relays": result_data,
        "daily_breakdown": daily_breakdown,
        "total_kwh": round(total_kwh, 3),
        "total_cost_inr": round(total_cost, 2),
        "rate_per_kwh_inr": RATE_PER_KWH,
    }

# ── Admin endpoints ───────────────────────────────────────────────────────────

@app.get("/api/admin/devices")
async def admin_list_devices(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).options(selectinload(Device.relays))
    )
    devices = result.scalars().all()
    return [_device_to_dict(d) for d in devices]


@app.get("/api/admin/pre-registered")
async def admin_list_pre_registered(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all pre-registered device IDs with their claim status."""
    result = await db.execute(
        select(PreRegisteredDevice).order_by(PreRegisteredDevice.created_at)
    )
    devices = result.scalars().all()
    return [
        {
            "device_id": d.device_id,
            "label": d.label,
            "num_switches": d.num_switches,
            "is_claimed": d.is_claimed,
            "created_at": d.created_at,
        }
        for d in devices
    ]


@app.post("/api/admin/seed-devices")
async def admin_seed_device(
    req: SeedDeviceRequest,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin: pre-register a new device ID so a user can claim it later."""
    device_id = req.device_id.upper().strip()
    if not device_id:
        raise HTTPException(400, "Device ID is required")

    existing = await db.execute(
        select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, f'Device ID "{device_id}" is already pre-registered')

    db.add(PreRegisteredDevice(
        device_id=device_id,
        label=req.label or "",
        num_switches=req.num_switches,
        is_claimed=False,
        created_at=int(time.time()),
    ))
    await db.commit()
    return {"success": True, "device_id": device_id, "label": req.label, "num_switches": req.num_switches}


@app.delete("/api/admin/pre-registered/{device_id}")
async def admin_delete_pre_registered(
    device_id: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin: remove an unclaimed pre-registered device ID."""
    device_id = device_id.upper()
    result = await db.execute(
        select(PreRegisteredDevice).where(PreRegisteredDevice.device_id == device_id)
    )
    pre = result.scalar_one_or_none()
    if not pre:
        raise HTTPException(404, "Pre-registered device not found")
    if pre.is_claimed:
        raise HTTPException(400, "Cannot delete a claimed device. Delete the Device record instead.")
    await db.delete(pre)
    await db.commit()
    return {"success": True}


@app.post("/api/admin/make-admin")
async def make_admin(
    secret: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Promote the current user to admin.
    - If ADMIN_SECRET env var is set and the request provides the matching 'secret' query param → always allowed.
    - Otherwise: allowed only if no admin exists yet (first-user bootstrap).
    """
    admin_secret_env = os.environ.get("ADMIN_SECRET", "")

    if admin_secret_env and secret == admin_secret_env:
        # Developer using the secret key — always promote
        pass
    else:
        # No secret: only allowed if no admin exists yet
        result = await db.execute(select(User).where(User.is_admin == True))  # noqa: E712
        existing_admin = result.scalar_one_or_none()
        if existing_admin and not user.is_admin:
            raise HTTPException(403, "An admin already exists. Contact your admin or use the admin secret.")

    user.is_admin = True
    await db.commit()
    return {"success": True, "message": f"{user.name} is now admin"}


@app.delete("/api/admin/devices/{device_id}")
async def admin_delete_device(
    device_id: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    device_id = device_id.upper()
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "Device not found")
    await db.delete(device)
    # Also remove user mapping
    user_result = await db.execute(select(User).where(User.device_id == device_id))
    for u in user_result.scalars().all():
        u.device_id = None
    await db.commit()
    return {"success": True}

# ── WebSocket — ESP32 Device ──────────────────────────────────────────────────

@app.websocket("/ws/esp/{device_id}")
async def esp_websocket(
    websocket: WebSocket,
    device_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for the ESP32.
    The ESP32 connects here and receives relay commands in real-time.
    It also sends heartbeats and state updates back.
    """
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    device_id = device_id.upper()
    await manager.connect_esp(device_id, websocket)

    # Mark device online
    await _set_device_online(db, device_id, True)
    await manager.broadcast_to_dashboards(device_id, {"type": "status", "online": True})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type", "")

            if msg_type == "heartbeat":
                # Update lastSeen + IP
                ip = data.get("ip", "")
                await _update_heartbeat(db, device_id, ip)
                await manager.broadcast_to_dashboards(device_id, {
                    "type": "heartbeat",
                    "last_seen": int(time.time()),
                    "online": True,
                })

            elif msg_type == "state_update":
                # ESP32 reports its local state (after a physical button press)
                states = data.get("states", {})
                await _log_relay_state_changes(db, device_id, states)
                await _update_relay_states(db, device_id, states)
                await manager.broadcast_to_dashboards(device_id, {
                    "type": "full_update",
                    "states": states,
                })

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect_esp(device_id)
        await _set_device_online(db, device_id, False)
        await manager.broadcast_to_dashboards(device_id, {"type": "status", "online": False})

# ── WebSocket — Dashboard (Browser) ──────────────────────────────────────────

@app.websocket("/ws/dashboard/{device_id}")
async def dashboard_websocket(
    websocket: WebSocket,
    device_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for browser dashboards.
    Pushes real-time relay/status updates from the backend.
    """
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    device_id = device_id.upper()
    await manager.connect_dashboard(device_id, websocket)

    # Send current device snapshot on connect
    result = await db.execute(
        select(Device).options(selectinload(Device.relays))
        .where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()
    if device:
        await websocket.send_text(json.dumps({
            "type": "snapshot",
            "device": _device_to_dict(device),
        }))

    try:
        while True:
            # Keep connection alive — browser can send pings
            await asyncio.sleep(30)
            try:
                await websocket.send_text(json.dumps({"type": "ping"}))
            except Exception:
                break
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        manager.disconnect_dashboard(device_id, websocket)

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.1.0", "mode": "self-hosted", "features": ["schedules", "power-usage"]}

# ── Helper functions ──────────────────────────────────────────────────────────

def _device_to_dict(device: Device) -> dict:
    return {
        "device_id": device.device_id,
        "owner_name": device.owner_name,
        "email": device.email,
        "num_switches": device.num_switches,
        "online": device.online,
        "last_seen": device.last_seen,
        "ip_address": device.ip_address,
        "created_at": device.created_at,
        "relays": {
            r.relay_key: {"name": r.name, "state": r.state, "wattage": r.wattage}
            for r in sorted(device.relays, key=lambda x: x.relay_key)
        },
    }


def _schedule_to_dict(sched: Schedule) -> dict:
    return {
        "id": sched.id,
        "device_id": sched.device_id,
        "relay_key": sched.relay_key,
        "action": sched.action,
        "time": sched.time,
        "days": sched.days,
        "enabled": sched.enabled,
        "label": sched.label,
        "created_at": sched.created_at,
    }


async def _set_device_online(db: AsyncSession, device_id: str, online: bool):
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device:
        device.online = online
        if online:
            device.last_seen = int(time.time())
        await db.commit()


async def _update_heartbeat(db: AsyncSession, device_id: str, ip: str):
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device:
        device.last_seen = int(time.time())
        device.online = True
        if ip:
            device.ip_address = ip
        await db.commit()


async def _update_relay_states(db: AsyncSession, device_id: str, states: dict):
    result = await db.execute(
        select(Relay).where(Relay.device_id == device_id)
    )
    relays = result.scalars().all()
    for relay in relays:
        if relay.relay_key in states:
            relay.state = bool(states[relay.relay_key])
    await db.commit()


async def _log_relay_state_changes(db: AsyncSession, device_id: str, states: dict):
    """Log ESP32-reported state changes into PowerLog for energy tracking."""
    result = await db.execute(select(Relay).where(Relay.device_id == device_id))
    relays = result.scalars().all()
    now = int(time.time())
    for relay in relays:
        if relay.relay_key in states:
            new_state = bool(states[relay.relay_key])
            if relay.state != new_state:
                db.add(PowerLog(
                    device_id=device_id,
                    relay_key=relay.relay_key,
                    state=new_state,
                    timestamp=now,
                ))
    await db.commit()


# ── Static Web UI ─────────────────────────────────────────────────────────────
# Serve the /web directory so the frontend is accessible from the same origin.
# This must come AFTER all API routes to avoid catching /api/* paths.
#
# Path resolution (works for both Railway Docker and local dev):
#   Railway: web/ is copied alongside main.py → /app/web
#   Local:   web/ is a sibling of backend/ → ../web

_here = os.path.dirname(os.path.abspath(__file__))

# Try sibling web/ first (Railway Docker layout: COPY web/ ./web/)
_WEB_DIR_SIBLING = os.path.join(_here, "web")
# Fall back to parent/../web (local dev: backend/ next to web/)
_WEB_DIR_PARENT  = os.path.join(_here, "..", "web")

if os.path.isdir(_WEB_DIR_SIBLING):
    _WEB_DIR = _WEB_DIR_SIBLING
else:
    _WEB_DIR = os.path.abspath(_WEB_DIR_PARENT)

print(f"[Static] Serving web UI from: {_WEB_DIR} (exists={os.path.isdir(_WEB_DIR)})")

if os.path.isdir(_WEB_DIR):
    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(os.path.join(_WEB_DIR, "index.html"))

    @app.get("/dashboard.html", include_in_schema=False)
    async def serve_dashboard():
        return FileResponse(os.path.join(_WEB_DIR, "dashboard.html"))

    @app.get("/admin.html", include_in_schema=False)
    async def serve_admin():
        return FileResponse(os.path.join(_WEB_DIR, "admin.html"))

    app.mount("/", StaticFiles(directory=_WEB_DIR, html=True), name="web")
