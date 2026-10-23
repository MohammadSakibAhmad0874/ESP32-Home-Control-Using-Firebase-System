/**
 * AWS Lambda Function for Alexa Smart Home Skill v3
 * Connects Alexa voice commands directly to Firebase Realtime Database.
 */

const admin = require('firebase-admin');

// Initialize Firebase Admin SDK
if (!admin.apps.length) {
  admin.initializeApp({
    databaseURL: 'https://apnaghar-3f865-default-rtdb.firebaseio.com',
  });
}

const db = admin.database();

exports.handler = async function (event, context) {
  console.log('[Alexa] Incoming Request:', JSON.stringify(event));

  const namespace = event.directive.header.namespace;
  const name = event.directive.header.name;

  // 1. Discovery Directive: Alexa asks "Discover my smart home devices"
  if (namespace === 'Alexa.Discovery' && name === 'Discover') {
    return handleDiscovery(event);
  }

  // 2. PowerController Directive: "Turn on/off <appliance>"
  if (namespace === 'Alexa.PowerController') {
    return handlePowerControl(event);
  }

  // 3. State Report Directive: "Is the living room light on?"
  if (namespace === 'Alexa' && name === 'ReportState') {
    return handleStateReport(event);
  }

  console.warn('[Alexa] Unhandled directive:', namespace, name);
  return null;
};

/**
 * Discovers and exposes the 4 relay endpoints to Alexa
 */
function handleDiscovery(event) {
  const header = {
    namespace: 'Alexa.Discovery',
    name: 'Discover.Response',
    payloadVersion: '3',
    messageId: event.directive.header.messageId + '-R',
  };

  const endpoints = [
    createEndpoint('SAKIB7860-relay1', 'Living Room Light', 'LIGHT', ['light', 'hall light']),
    createEndpoint('SAKIB7860-relay2', 'Bedroom Lamp', 'LIGHT', ['bedroom light', 'night lamp']),
    createEndpoint('SAKIB7860-relay3', 'Kitchen Light', 'LIGHT', ['kitchen light', 'cooking light']),
    createEndpoint('SAKIB7860-relay4', 'Ceiling Fan', 'FAN', ['fan', 'bedroom fan']),
  ];

  return {
    event: {
      header: header,
      payload: {
        endpoints: endpoints,
      },
    },
  };
}

function createEndpoint(endpointId, friendlyName, displayCategory, cookieDescriptions) {
  return {
    endpointId: endpointId,
    manufacturerName: 'ApnaGhar Technologies',
    friendlyName: friendlyName,
    description: 'ApnaGhar 4-Channel ESP32 Smart Switch Channel',
    displayCategories: [displayCategory],
    cookie: {
      extraDetails: cookieDescriptions.join(', '),
    },
    capabilities: [
      {
        type: 'AlexaInterface',
        interface: 'Alexa',
        version: '3',
      },
      {
        type: 'AlexaInterface',
        interface: 'Alexa.PowerController',
        version: '3',
        properties: {
          supported: [{ name: 'powerState' }],
          proactivelyReported: true,
          retrievable: true,
        },
      },
    ],
  };
}

/**
 * Handles TurnOn and TurnOff requests
 */
async function handlePowerControl(event) {
  const directive = event.directive;
  const endpointId = directive.endpoint.endpointId; // e.g. "SAKIB7860-relay1"
  const action = directive.header.name;             // "TurnOn" or "TurnOff"
  const newState = (action === 'TurnOn');

  const parts = endpointId.split('-');
  const deviceId = parts[0];
  const relayId = parts[1]; // "relay1"

  console.log(`[Alexa Control] Writing to Firebase: /devices/${deviceId}/relays/${relayId}/state = ${newState}`);

  // Write directly to Firebase Realtime Database
  await db.ref(`/devices/${deviceId}/relays/${relayId}/state`).set(newState);

  // Return standard Alexa Response
  const response = {
    context: {
      properties: [
        {
          namespace: 'Alexa.PowerController',
          name: 'powerState',
          value: newState ? 'ON' : 'OFF',
          timeOfSample: new Date().toISOString(),
          uncertaintyInMilliseconds: 200,
        },
      ],
    },
    event: {
      header: {
        namespace: 'Alexa',
        name: 'Response',
        payloadVersion: '3',
        messageId: directive.header.messageId + '-R',
        correlationToken: directive.header.correlationToken,
      },
      endpoint: {
        endpointId: endpointId,
      },
      payload: {},
    },
  };

  return response;
}

/**
 * Returns current relay state to Alexa
 */
async function handleStateReport(event) {
  const directive = event.directive;
  const endpointId = directive.endpoint.endpointId;
  const parts = endpointId.split('-');
  const deviceId = parts[0];
  const relayId = parts[1];

  const snap = await db.ref(`/devices/${deviceId}/relays/${relayId}/state`).once('value');
  const currentState = snap.val() === true;

  return {
    context: {
      properties: [
        {
          namespace: 'Alexa.PowerController',
          name: 'powerState',
          value: currentState ? 'ON' : 'OFF',
          timeOfSample: new Date().toISOString(),
          uncertaintyInMilliseconds: 100,
        },
      ],
    },
    event: {
      header: {
        namespace: 'Alexa',
        name: 'StateReport',
        payloadVersion: '3',
        messageId: directive.header.messageId + '-R',
        correlationToken: directive.header.correlationToken,
      },
      endpoint: {
        endpointId: endpointId,
      },
      payload: {},
    },
  };
}
