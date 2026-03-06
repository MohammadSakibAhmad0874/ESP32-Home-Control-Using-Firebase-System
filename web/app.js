/**
 * HomeControl — Shared App Utilities
 * Handles: auth tokens, API helpers, relay toggle helpers
 */

/* ── Backend URL ─────────────────────────────────────────────────────────
   Set BACKEND_URL to your Railway backend URL after deploying.
   Leave as empty string '' to use same-origin (local dev / ngrok).
   Example: 'https://homecontrol-backend.up.railway.app'
──────────────────────────────────────────────────────────────────────── */
const BACKEND_URL = ''; // ← paste Railway URL here after deploy

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
function getDeviceId() { return localStorage.getItem(DEVICE_KEY); }
function getName() { return localStorage.getItem(NAME_KEY) || 'User'; }
function isAdmin() { return localStorage.getItem(ADMIN_KEY) === '1'; }

function clearAuth() {
    [TOKEN_KEY, DEVICE_KEY, NAME_KEY, ADMIN_KEY].forEach(k => localStorage.removeItem(k));
}

function requireAuth(redirectTo = '/index.html') {
    if (!getToken()) { window.location.href = redirectTo; throw new Error('Not authenticated'); }
}

function requireAdmin() {
    requireAuth();
    if (!isAdmin()) { window.location.href = '/dashboard.html'; throw new Error('Not admin'); }
}

function logout() {
    clearAuth();
    window.location.href = '/index.html';
}

/* ── API Base URL ─────────────────────────────────────────────────────── */

function apiBase() {
    // Use BACKEND_URL if set, otherwise fall back to same origin (local dev)
    return BACKEND_URL || window.location.origin;
}

/* ── API Helpers ───────────────────────────────────────────────────────── */

async function apiRequest(path, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    const res = await fetch(`${apiBase()}${path}`, {
        ...options,
        headers,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        throw new Error(data.detail || `Request failed (${res.status})`);
    }

    return data;
}

async function apiGet(path) { return apiRequest(path, { method: 'GET' }); }
async function apiPost(path, body) { return apiRequest(path, { method: 'POST', body: JSON.stringify(body) }); }
async function apiPut(path, body) { return apiRequest(path, { method: 'PUT', body: JSON.stringify(body) }); }
async function apiDelete(path) { return apiRequest(path, { method: 'DELETE' }); }

/* ── Toggle Relay (HTTP) ──────────────────────────────────────────────── */

async function toggleRelay(deviceId, relayKey, newState) {
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
    const n = name.toLowerCase();
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
    if (!ts) return 'Never';
    const diff = Math.floor(Date.now() / 1000) - ts;
    if (diff < 5) return 'Just now';
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
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
