"""
HomeControl — Self-Hosted Backend
FastAPI app with JWT auth, PostgreSQL, and WebSocket real-time sync for ESP32.
"""
import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Optional

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
from database import get_db, init_db
from models import Device, Relay, User

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

# ── App lifecycle ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="HomeControl API", version="2.0.0", lifespan=lifespan)

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

class LoginRequest(BaseModel):
    device_id: str
    password: str

class RelayToggleRequest(BaseModel):
    state: bool

class RelayRenameRequest(BaseModel):
    name: str

# ── Auth endpoints ────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Validate device ID format
    device_id = req.device_id.upper().strip()
    if not device_id:
        raise HTTPException(400, "Device ID is required")

    # Check device uniqueness
    existing = await db.execute(select(Device).where(Device.device_id == device_id))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f'Device ID "{device_id}" already exists')

    # Check email uniqueness
    existing_user = await db.execute(select(User).where(User.email == req.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    now = int(time.time())
    user_id = str(uuid.uuid4())
    default_names = ["Living Room", "Bedroom", "Kitchen", "Fan",
                     "Switch 5", "Switch 6", "Switch 7", "Switch 8"]

    # Create device
    device = Device(
        device_id=device_id,
        owner_name=req.name,
        email=req.email,
        num_switches=req.num_switches,
        online=False,
        last_seen=now,
        created_at=now,
    )
    db.add(device)
    await db.flush()  # Get device_id before creating relays

    # Create relays
    for i in range(1, req.num_switches + 1):
        key = f"relay{i}"
        name = (req.switch_names[i - 1] if i <= len(req.switch_names)
                else default_names[i - 1] if i <= len(default_names)
                else f"Switch {i}")
        db.add(Relay(device_id=device_id, relay_key=key, name=name, state=False))

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

    relay.state = req.state
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


@app.post("/api/admin/make-admin")
async def make_admin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """First user to call this becomes admin. Subsequent calls require existing admin."""
    # Check if any admin exists
    result = await db.execute(select(User).where(User.is_admin == True))  # noqa: E712
    existing_admin = result.scalar_one_or_none()
    if existing_admin and not user.is_admin:
        raise HTTPException(403, "An admin already exists")
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
    # Validate device token (simple shared secret check: token must equal device_id for now,
    # or you can use JWT — using JWT here for proper auth)
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
    return {"status": "ok", "version": "2.0.0", "mode": "self-hosted"}

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
            r.relay_key: {"name": r.name, "state": r.state}
            for r in sorted(device.relays, key=lambda x: x.relay_key)
        },
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


# ── Static Web UI ─────────────────────────────────────────────────────────────
# Serve the /web directory so the frontend is accessible from the same origin.
# This must come AFTER all API routes to avoid catching /api/* paths.

_WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
_WEB_DIR = os.path.abspath(_WEB_DIR)

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
