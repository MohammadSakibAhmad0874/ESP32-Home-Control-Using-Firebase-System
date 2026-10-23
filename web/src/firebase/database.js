import { ref, get, set, update, onValue, remove } from 'firebase/database';
import { db } from './firebase-config';

// ── User Device Management ──────────────────────────────────────────────────

export const getUserDevices = async (uid) => {
  if (!uid) return [];
  const snap = await get(ref(db, `users/${uid}/devices`));
  if (!snap.exists()) return [];
  const val = snap.val();
  return Object.keys(val || {}).filter(k => val[k]);
};

export const subscribeUserDevices = (uid, callback) => {
  if (!uid) return () => {};
  return onValue(ref(db, `users/${uid}/devices`), (snapshot) => {
    const val = snapshot.val() || {};
    const deviceIds = Object.keys(val).filter(k => val[k]);
    callback(deviceIds);
  });
};

export const subscribeUserPending = (uid, callback) => {
  if (!uid) return () => {};
  return onValue(ref(db, `users/${uid}/pendingRequests`), (snapshot) => {
    const val = snapshot.val() || {};
    callback(val);
  });
};

export const subscribeDevice = (deviceId, callback) => {
  if (!deviceId) return () => {};
  return onValue(ref(db, `devices/${deviceId}`), (snapshot) => {
    callback(snapshot.val());
  });
};

export const toggleRelayState = async (deviceId, relayKey, newState) => {
  const relayRef = ref(db, `devices/${deviceId}/relays/${relayKey}/state`);
  await set(relayRef, newState);
};

// ── Device Request Flow ─────────────────────────────────────────────────────

export const requestDeviceAccess = async (deviceIdInput, user) => {
  const deviceId = (deviceIdInput || '').trim().toUpperCase();
  if (!deviceId) throw new Error('Please enter a valid Device ID.');

  // 1. Verify that device exists in /devices
  const devSnap = await get(ref(db, `devices/${deviceId}`));
  if (!devSnap.exists()) {
    throw new Error(`Device ID "${deviceId}" was not found in the system. Check your device box or contact admin.`);
  }

  const reqId = `${deviceId}_${user.uid}`;
  const requestData = {
    requestId: reqId,
    deviceId,
    userId: user.uid,
    userEmail: user.email,
    userName: user.displayName || user.email.split('@')[0],
    status: 'pending',
    timestamp: Date.now()
  };

  // 2. Write request in /deviceRequests
  await set(ref(db, `deviceRequests/${reqId}`), requestData);

  // 3. Mark in user profile
  await set(ref(db, `users/${user.uid}/pendingRequests/${deviceId}`), {
    status: 'pending',
    requestedAt: Date.now()
  });

  return requestData;
};

// ── Admin Functions ─────────────────────────────────────────────────────────

export const subscribeAllPendingRequests = (callback) => {
  return onValue(ref(db, 'deviceRequests'), (snapshot) => {
    const data = snapshot.val() || {};
    const pendingList = Object.entries(data)
      .map(([id, req]) => ({ id, ...req }))
      .filter(r => r.status === 'pending')
      .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    callback(pendingList);
  });
};

export const approveDeviceRequest = async (request, adminUid) => {
  const { id, deviceId, userId, userEmail } = request;

  // 1. Mark request as approved
  await update(ref(db, `deviceRequests/${id}`), {
    status: 'approved',
    approvedAt: Date.now(),
    approvedBy: adminUid
  });

  // 2. Grant device to user
  await set(ref(db, `users/${userId}/devices/${deviceId}`), true);

  // 3. Remove from user pending
  await remove(ref(db, `users/${userId}/pendingRequests/${deviceId}`));

  // 4. Update device owner in /devices/{deviceId}
  await update(ref(db, `devices/${deviceId}`), {
    owner: userId,
    claimedBy: userEmail,
    claimedAt: Date.now()
  });
};

export const rejectDeviceRequest = async (request) => {
  const { id, deviceId, userId } = request;
  await update(ref(db, `deviceRequests/${id}`), {
    status: 'rejected',
    rejectedAt: Date.now()
  });
  await remove(ref(db, `users/${userId}/pendingRequests/${deviceId}`));
};

export const subscribeAllDevices = (callback) => {
  return onValue(ref(db, 'devices'), (snapshot) => {
    const data = snapshot.val() || {};
    const list = Object.entries(data).map(([deviceId, d]) => ({
      deviceId,
      ...d
    }));
    callback(list);
  });
};

export const subscribeAllUsers = (callback) => {
  return onValue(ref(db, 'users'), (snapshot) => {
    const data = snapshot.val() || {};
    const list = Object.entries(data).map(([uid, u]) => ({
      uid,
      ...u
    }));
    callback(list);
  });
};

export const updateUserRole = async (userId, role) => {
  await set(ref(db, `users/${userId}/role`), role);
};
