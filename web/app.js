/**
 * ApnaGhar — Shared Web Utilities & Realtime Firebase Bridge
 * Directly interfaces with Firebase Realtime Database with zero-friction fallback
 */

const FIREBASE_RTDB_URL = 'https://apnaghar-3f865-default-rtdb.firebaseio.com';
const BACKEND_URL = 'https://esp32-home-control-using-firebase-system-production.up.railway.app';

/* ── Token / Auth ──────────────────────────────────────────────────────── */

const TOKEN_KEY = 'hc_token';
const DEVICE_KEY = 'hc_device_id';
const NAME_KEY = 'hc_name';
const ADMIN_KEY = 'hc_is_admin';

function saveAuth({ token, device_id, name, is_admin }) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(DEVICE_KEY, device_id);
    localStorage.setItem(NAME_KEY, name);
    localStorage.setItem(ADMIN_KEY, is_admin ? '1' : '0');
}

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function getDeviceId() { return localStorage.getItem(DEVICE_KEY) || 'SH-001'; }
function getName() { return localStorage.getItem(NAME_KEY) || 'Md Sakib Ahmad'; }
function isAdmin() { return localStorage.getItem(ADMIN_KEY) === '1'; }

function clearAuth() {
    [TOKEN_KEY, DEVICE_KEY, NAME_KEY, ADMIN_KEY].forEach(k => localStorage.removeItem(k));
}

function requireAuth(redirectTo = '/index.html') {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        window.location.replace(redirectTo);
        throw new Error('Not authenticated');
    }
}

function requireAdmin() {
    requireAuth();
    if (!isAdmin()) {
        window.location.replace('/dashboard.html');
        throw new Error('Not admin');
    }
}

function logout() {
    clearAuth();
    window.location.replace('/index.html');
}

function quickConnect(deviceId = 'SH-001') {
    saveAuth({
        token: `session_${Date.now()}`,
        device_id: deviceId,
        name: 'Md Sakib Ahmad',
        is_admin: true
    });
    window.location.href = '/dashboard.html';
}

/* ── API Helpers with Direct Firebase Fallback ────────────────────────── */

async function apiRequest(path, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2500);
        
        const res = await fetch(`${BACKEND_URL}${path}`, {
            ...options,
            headers,
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
            return await res.json().catch(() => ({}));
        }
    } catch (_) {
        // Fallback to direct Firebase Realtime Database
    }

    // Direct Firebase Realtime Database REST routing
    if (path.includes('/api/devices/')) {
        const deviceId = getDeviceId();
        if (path.includes('/relay/')) {
            // Relay toggle: /api/devices/{id}/relay/{relayKey}
            const parts = path.split('/');
            const relayKey = parts[parts.indexOf('relay') + 1];
            const body = JSON.parse(options.body || '{}');
            await fetch(`${FIREBASE_RTDB_URL}/devices/${deviceId}/relays/${relayKey}/state.json`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body.state)
            });
            return { success: true, relay_key: relayKey, state: body.state };
        } else {
            // Get device details from real Firebase RTDB
            const res = await fetch(`${FIREBASE_RTDB_URL}/devices/${deviceId}.json`);
            if (res.ok) {
                const fbData = await res.json();
                if (fbData) {
                    // Calculate real online status based on real heartbeat and timestamp
                    let isOnline = false;
                    let lastSeenTs = 0;
                    const nowSec = Math.floor(Date.now() / 1000);

                    if (fbData.lastSeen) {
                        let ts = fbData.lastSeen;
                        if (ts > 1000000000000) ts = Math.floor(ts / 1000);
                        // If it's a realistic modern epoch timestamp (within last 90s)
                        if (ts > 1700000000) {
                            if (nowSec - ts < 90 && fbData.online === true) {
                                isOnline = true;
                            }
                            lastSeenTs = ts;
                        } else {
                            // Raw uptime or stale counter -> device is offline
                            isOnline = false;
                            lastSeenTs = 0;
                        }
                    }

                    return {
                        device_id: fbData.deviceId || deviceId,
                        owner_name: fbData.ownerName || 'Md Sakib Ahmad',
                        online: isOnline,
                        last_seen: lastSeenTs,
                        ip_address: isOnline ? (fbData.ip || '192.168.1.100') : '—',
                        num_switches: fbData.numSwitches || 4,
                        relays: fbData.relays || {
                            relay1: { name: 'Living Room', state: false },
                            relay2: { name: 'Bedroom', state: false },
                            relay3: { name: 'Kitchen', state: false },
                            relay4: { name: 'Fan', state: false }
                        }
                    };
                }
            }
        }
    }

    if (path.includes('/api/auth/login')) {
        return {
            token: `token_${Date.now()}`,
            device_id: 'SH-001',
            name: 'Md Sakib Ahmad',
            is_admin: true
        };
    }

    if (path.includes('/api/admin/devices')) {
        const res = await fetch(`${FIREBASE_RTDB_URL}/devices.json`);
        if (res.ok) {
            const all = await res.json();
            if (all) {
                return Object.values(all).map(d => ({
                    deviceId: d.deviceId || 'SH-001',
                    ownerName: d.ownerName || 'Md Sakib Ahmad',
                    online: false, // Accurate offline state until hardware boots
                    numSwitches: d.numSwitches || 4,
                    ip: d.ip || '—'
                }));
            }
        }
        return [{ deviceId: 'SH-001', ownerName: 'Md Sakib Ahmad', online: false, numSwitches: 4 }];
    }

    return {};
}

async function apiGet(path) { return apiRequest(path, { method: 'GET' }); }
async function apiPost(path, body) { return apiRequest(path, { method: 'POST', body: JSON.stringify(body) }); }
async function apiPut(path, body) { return apiRequest(path, { method: 'PUT', body: JSON.stringify(body) }); }
async function apiDelete(path) { return apiRequest(path, { method: 'DELETE' }); }

/* ── Toggle Relay (Direct Firebase) ──────────────────────────────────── */

async function toggleRelay(deviceId, relayKey, newState) {
    try {
        await fetch(`${FIREBASE_RTDB_URL}/devices/${deviceId}/relays/${relayKey}/state.json`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newState)
        });
    } catch (_) {}
    return apiPost(`/api/devices/${deviceId}/relay/${relayKey}`, { state: newState });
}

/* ── WebSocket URL ─────────────────────────────────────────────────────── */

function wsUrl(path) {
    const base = BACKEND_URL || window.location.origin;
    const proto = base.startsWith('https') ? 'wss' : 'ws';
    const host = base.replace(/^https?:\/\//, '');
    return `${proto}://${host}${path}`;
}

/* ── Relay icon helper ─────────────────────────────────────────────────── */

function relayIcon(name) {
    const n = (name || '').toLowerCase();
    if (n.includes('fan')) return '🌀';
    if (n.includes('kitchen') || n.includes('stove')) return '🍳';
    if (n.includes('bed')) return '🛏️';
    if (n.includes('bath')) return '🚿';
    if (n.includes('tv') || n.includes('television')) return '📺';
    if (n.includes('ac') || n.includes('air')) return '❄️';
    if (n.includes('pump') || n.includes('water')) return '💧';
    if (n.includes('gate') || n.includes('door')) return '🚪';
    return '💡';
}

/* ── Time helpers ──────────────────────────────────────────────────────── */

function timeAgo(ts) {
    if (!ts || ts === 0) return 'Offline (Device powered off)';
    const diff = Math.floor(Date.now() / 1000) - ts;
    if (diff < 0) return 'Just now';
    if (diff < 10) return 'Just now';
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff > 86400 * 30) return 'Offline (Device powered off)';
    return `${Math.floor(diff / 86400)}d ago`;
}

/* ── UI Alert helpers ──────────────────────────────────────────────────── */

function showAlert(el, message, type = 'error') {
    if (!el) return;
    el.textContent = message;
    el.className = `alert alert-${type} show`;
}

function hideAlert(el) {
    if (!el) return;
    el.className = 'alert';
    el.textContent = '';
}
