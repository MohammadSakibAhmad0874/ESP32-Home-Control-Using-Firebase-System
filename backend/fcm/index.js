/**
 * Firebase Cloud Functions for ApnaGhar Push Notifications (FCM)
 * Triggers on relay state changes and electrical anomalies (power surge / overcurrent).
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp();

/**
 * 1. Relay State Change Alert
 * Fires immediately when any switch is turned ON or OFF.
 */
exports.relayStateAlert = functions.database
  .ref('/devices/{deviceId}/relays/{relayId}/state')
  .onWrite(async (change, context) => {
    const deviceId = context.params.deviceId;
    const relayId = context.params.relayId;
    const newState = change.after.val();
    const oldState = change.before.val();

    // Ignore if value didn't actually change
    if (newState === oldState) return null;

    console.log(`[FCM] Device ${deviceId} Relay ${relayId} changed to ${newState}`);

    // Lookup device metadata to find registered owner UID
    const deviceSnap = await admin.database().ref(`/devices/${deviceId}/owner`).once('value');
    const ownerUid = deviceSnap.val();

    if (!ownerUid) {
      console.log(`[FCM] No registered owner UID found for device ${deviceId}`);
      return null;
    }

    // Retrieve owner's FCM device token
    const tokenSnap = await admin.database().ref(`/users/${ownerUid}/fcmToken`).once('value');
    const fcmToken = tokenSnap.val();

    if (!fcmToken) {
      console.log(`[FCM] No FCM token found for user ${ownerUid}`);
      return null;
    }

    const statusText = newState ? 'TURNED ON 🟢' : 'TURNED OFF 🔴';
    const message = {
      token: fcmToken,
      notification: {
        title: `⚡ Switch Update: Relay ${relayId}`,
        body: `Appliance on Relay ${relayId} (${deviceId}) was ${statusText}.`,
      },
      data: {
        deviceId: deviceId,
        relayId: relayId,
        state: String(newState),
        timestamp: String(Date.now()),
      },
      android: {
        priority: 'high',
        notification: {
          channelId: 'apnaghar_switch_alerts',
          sound: 'default',
        },
      },
    };

    try {
      const response = await admin.messaging().send(message);
      console.log('[FCM] Successfully dispatched push notification:', response);
      return response;
    } catch (error) {
      console.error('[FCM] Error dispatching push notification:', error);
      return null;
    }
  });

/**
 * 2. Power Surge & Overcurrent Emergency Alert
 * Fires when PZEM-004T measures active power exceeding 3,000 Watts or overcurrent.
 */
exports.powerSurgeAlert = functions.database
  .ref('/devices/{deviceId}/power/power')
  .onWrite(async (change, context) => {
    const deviceId = context.params.deviceId;
    const currentWatts = change.after.val();

    // Alert threshold: 3000 Watts
    if (!currentWatts || currentWatts < 3000) return null;

    console.warn(`[FCM SURGE WARNING] Device ${deviceId} load reached ${currentWatts}W!`);

    const deviceSnap = await admin.database().ref(`/devices/${deviceId}/owner`).once('value');
    const ownerUid = deviceSnap.val();
    if (!ownerUid) return null;

    const tokenSnap = await admin.database().ref(`/users/${ownerUid}/fcmToken`).once('value');
    const fcmToken = tokenSnap.val();
    if (!fcmToken) return null;

    const message = {
      token: fcmToken,
      notification: {
        title: '⚠️ High Power Warning!',
        body: `Device ${deviceId} power draw exceeded ${Math.round(currentWatts)}W! Check your connected loads.`,
      },
      data: {
        alertType: 'POWER_SURGE',
        deviceId: deviceId,
        watts: String(currentWatts),
      },
    };

    return admin.messaging().send(message);
  });
