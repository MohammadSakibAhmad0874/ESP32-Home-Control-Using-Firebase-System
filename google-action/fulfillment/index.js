/**
 * Google Home Smart Home Fulfillment Function
 * Handles SYNC, QUERY, and EXECUTE intents from Google Assistant.
 */

const { smarthome } = require('actions-on-google');
const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp();
const db = admin.database();

const app = smarthome({
  debug: true,
});

/**
 * 1. SYNC Intent: Discovers user's 4 smart relays
 */
app.onSync((body) => {
  return {
    requestId: body.requestId,
    payload: {
      agentUserId: 'apnaghar-user-001',
      devices: [
        {
          id: 'SAKIB7860-relay1',
          type: 'action.devices.types.LIGHT',
          traits: ['action.devices.traits.OnOff'],
          name: {
            defaultNames: ['Living Room Light'],
            name: 'Living Room Light',
            nicknames: ['living room light', 'hall light'],
          },
          willReportState: true,
          deviceInfo: {
            manufacturer: 'ApnaGhar',
            model: 'ESP32-4CH-v2',
            hwVersion: '2.0',
            swVersion: '2.0',
          },
        },
        {
          id: 'SAKIB7860-relay2',
          type: 'action.devices.types.LIGHT',
          traits: ['action.devices.traits.OnOff'],
          name: {
            defaultNames: ['Bedroom Lamp'],
            name: 'Bedroom Lamp',
            nicknames: ['bedroom light', 'bed lamp'],
          },
          willReportState: true,
        },
        {
          id: 'SAKIB7860-relay3',
          type: 'action.devices.types.LIGHT',
          traits: ['action.devices.traits.OnOff'],
          name: {
            defaultNames: ['Kitchen Light'],
            name: 'Kitchen Light',
            nicknames: ['kitchen light'],
          },
          willReportState: true,
        },
        {
          id: 'SAKIB7860-relay4',
          type: 'action.devices.types.FAN',
          traits: ['action.devices.traits.OnOff'],
          name: {
            defaultNames: ['Ceiling Fan'],
            name: 'Ceiling Fan',
            nicknames: ['fan', 'bedroom fan'],
          },
          willReportState: true,
        },
      ],
    },
  };
});

/**
 * 2. QUERY Intent: Checks current state of relays
 */
app.onQuery(async (body) => {
  const { devices } = body.inputs[0].payload;
  const deviceStates = {};

  for (const device of devices) {
    const parts = device.id.split('-');
    const deviceId = parts[0];
    const relayId = parts[1];

    const snap = await db.ref(`/devices/${deviceId}/relays/${relayId}/state`).once('value');
    const isOn = snap.val() === true;

    deviceStates[device.id] = {
      on: isOn,
      online: true,
      status: 'SUCCESS',
    };
  }

  return {
    requestId: body.requestId,
    payload: {
      devices: deviceStates,
    },
  };
});

/**
 * 3. EXECUTE Intent: Turns switches ON or OFF
 */
app.onExecute(async (body) => {
  const { commands } = body.inputs[0].payload;
  const successfulDeviceIds = [];

  for (const command of commands) {
    for (const execution of command.execution) {
      if (execution.command === 'action.devices.commands.OnOff') {
        const turnOn = execution.params.on;

        for (const device of command.devices) {
          const parts = device.id.split('-');
          const deviceId = parts[0];
          const relayId = parts[1];

          await db.ref(`/devices/${deviceId}/relays/${relayId}/state`).set(turnOn);
          successfulDeviceIds.push(device.id);
        }
      }
    }
  }

  return {
    requestId: body.requestId,
    payload: {
      commands: [
        {
          ids: successfulDeviceIds,
          status: 'SUCCESS',
          states: {
            online: true,
          },
        },
      ],
    },
  };
});

exports.smarthome = functions.https.onRequest(app);
