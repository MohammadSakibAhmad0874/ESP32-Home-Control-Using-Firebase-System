/* =============================================================
   HomeControl Self-Hosted — Global API Client
   Replaces Firebase SDK with JWT + fetch() + WebSocket
   ============================================================= */

const API_BASE = '';  // Same origin via Nginx

// ── Token storage ──────────────────────────────────────────────────────────

function getToken() {
    return localStorage.getItem('hc_token');
}

function setToken(t) {
    localStorage.setItem('hc_token', t);
}

function getDeviceId() {
    return localStorage.getItem('hc_device_id');
}

function setDeviceId(id) {
    localStorage.setItem('hc_device_id', id);
}

function clearSession() {
    localStorage.removeItem('hc_token');
    localStorage.removeItem('hc_device_id');
    localStorage.removeItem('hc_name');
    localStorage.removeItem('hc_is_admin');
}

// ── HTTP helpers ────────────────────────────────────────────────────────────

// ngrok bypass: skip the interstitial warning page in all fetch requests
const NGROK_HEADERS = { 'ngrok-skip-browser-warning': '1' };

async function apiGet(path) {
    const r = await fetch(API_BASE + path, {
        headers: { Authorization: 'Bearer ' + getToken(), ...NGROK_HEADERS }
    });
    if (r.status === 401) { logout(); throw new Error('Unauthenticated'); }
    if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: 'Server error' }));
        throw new Error(err.detail || `HTTP ${r.status}`);
    }
    return r.json();
}

async function apiPost(path, body) {
    const r = await fetch(API_BASE + path, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + getToken(),
            ...NGROK_HEADERS
        },
        body: JSON.stringify(body)
    });
    if (r.status === 401) { logout(); throw new Error('Unauthenticated'); }
    return r.json();
}

async function apiPut(path, body) {
    const r = await fetch(API_BASE + path, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + getToken(),
            ...NGROK_HEADERS
        },
        body: JSON.stringify(body)
    });
    return r.json();
}

async function apiDelete(path) {
    const r = await fetch(API_BASE + path, {
        method: 'DELETE',
        headers: { Authorization: 'Bearer ' + getToken(), ...NGROK_HEADERS }
    });
    return r.json();
}

// ── Auth helpers ────────────────────────────────────────────────────────────

function logout() {
    clearSession();
    window.location.href = '/cloud/index.html';
}

function requireAuth(callback) {
    const token = getToken();
    if (!token) {
        window.location.href = '/cloud/index.html';
        return;
    }
    callback();
}

// ── Relay control ───────────────────────────────────────────────────────────

async function toggleRelay(deviceId, relayKey, currentState) {
    await apiPost(`/api/devices/${deviceId}/relay/${relayKey}`, {
        state: !currentState
    });
}

// ── Time formatting ─────────────────────────────────────────────────────────

function getTimeAgo(timestamp) {
    // timestamp is Unix seconds from backend
    let tsMs = timestamp < 1e11 ? timestamp * 1000 : timestamp;
    const diffMs = Date.now() - tsMs;
    if (diffMs < 0 || diffMs > 1e12) return 'Just now';
    const s = Math.floor(diffMs / 1000);
    if (s < 5) return 'Just now';
    if (s < 60) return s + ' sec ago';
    if (s < 3600) return Math.floor(s / 60) + ' min ago';
    if (s < 86400) return Math.floor(s / 3600) + ' hr ago';
    return Math.floor(s / 86400) + ' days ago';
}

// ── UI helpers ──────────────────────────────────────────────────────────────

function showError(msg) {
    const el = document.getElementById('errorMsg');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
    const s = document.getElementById('successMsg');
    if (s) s.style.display = 'none';
}

function showSuccess(msg) {
    const el = document.getElementById('successMsg');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
    const e = document.getElementById('errorMsg');
    if (e) e.style.display = 'none';
}

function clearMessages() {
    const e = document.getElementById('errorMsg');
    const s = document.getElementById('successMsg');
    if (e) e.style.display = 'none';
    if (s) s.style.display = 'none';
}
