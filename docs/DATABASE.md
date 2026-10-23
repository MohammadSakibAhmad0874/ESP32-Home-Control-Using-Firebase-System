# 🗄️ Database Architecture & Security Rules — Firebase Realtime Database

This document defines the Firebase Realtime Database (RTDB) schema, JSON data structures, telemetry payloads, access control vulnerabilities, and production security rules.

---

## 1. Firebase Realtime Database Schema

The database is organized into hierarchical nodes designed for low read/write latency and direct subscription via mobile and web clients:

```
apnaghar-default-rtdb/
├── devices/
│   └── <DEVICE_ID>/           # e.g., "SH-001" or "SAKIB7860"
│       ├── info/
│       │   ├── name: "Living Room Controller"
│       │   ├── owner: "USER_UID_12345"
│       │   ├── firmwareVersion: "1.2.0"
│       │   └── ip: "192.168.1.45"
│       ├── status/
│       │   ├── online: true
│       │   └── lastSeen: 1710214800
│       └── relays/
│           ├── relay1/
│           │   ├── name: "Ceiling Chandelier"
│           │   ├── state: true
│           │   └── wattage: 40.0
│           ├── relay2/
│           │   ├── name: "AC Unit"
│           │   ├── state: false
│           │   └── wattage: 1500.0
│           ├── relay3/
│           │   ├── name: "Kitchen Exhaust"
│           │   ├── state: false
│           │   └── wattage: 65.0
│           └── relay4/
│               ├── name: "Ceiling Fan"
│               ├── state: true
│               └── wattage: 75.0
├── users/
│   └── <USER_UID>/
│       ├── profile/
│       │   ├── email: "user@example.com"
│       │   ├── name: "Sakib"
│       │   └── role: "homeowner"
│       └── claimedDevices/
│           └── <DEVICE_ID>: true
└── logs/
    └── <DEVICE_ID>/
        └── <TIMESTAMP_ID>/
            ├── event: "relay_toggle"
            ├── target: "relay1"
            ├── newState: true
            ├── triggeredBy: "web_dashboard"
            └── timestamp: 1710214815
```

---

## 2. Sample Database JSON Representation

```json
{
  "devices": {
    "SH-001": {
      "online": true,
      "lastSeen": 1710214800,
      "ip": "192.168.1.45",
      "owner": "usr_987654321",
      "relays": {
        "relay1": { "name": "Living Room Light", "state": true, "wattage": 60 },
        "relay2": { "name": "Bedroom Lamp", "state": false, "wattage": 40 },
        "relay3": { "name": "Kitchen Light", "state": false, "wattage": 25 },
        "relay4": { "name": "Ceiling Fan", "state": true, "wattage": 75 }
      }
    }
  },
  "users": {
    "usr_987654321": {
      "role": "admin",
      "email": "sakib@apnaghar.com",
      "name": "Sakib Ahmad",
      "devices": {
        "SH-001": true
      }
    }
  },
  "logs": {
    "SH-001": {
      "log_1710214815": {
        "relay": "relay1",
        "state": true,
        "source": "App",
        "timestamp": 1710214815
      }
    }
  }
}
```

---

## 3. The Security Problem: Insecure Development Rules

Many initial prototypes use wildcard open rules in the Firebase console:

### ⚠️ Dangerous Development Rules (Insecure)
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

> [!CAUTION]
> **Why Open Rules Are a Critical Threat:**
> 1. Anyone who inspects the client website JavaScript (`firebase-config.js`) obtains the project Database URL (`https://<project-id>-default-rtdb.firebaseio.com`).
> 2. With `".read": true` and `".write": true`, any attacker can send an unauthenticated HTTP `PUT` request via cURL or Postman to flip your relays, turn off home appliances, trigger electrical shorts, or delete all registered device records.

---

## 4. Production Security Rules (Recommended)

The following `database.rules.json` enforces:
1. **Mandatory User Authentication**: Anonymous or unauthenticated requests are blocked.
2. **Owner Isolation**: Users can only read and write devices that they have explicitly claimed in their user profile (`/users/$uid/devices/$deviceId`).
3. **Data Type Validation**: Ensures relay states can only be written as booleans (`true` or `false`).
4. **Admin Privileges**: Users with `role == 'admin'` have full system auditing visibility.

### 🔒 Recommended `database.rules.json`
```json
{
  "rules": {
    "devices": {
      "$deviceId": {
        // Allow read/write if the authenticated user owns this device OR is an admin
        ".read": "auth != null && (root.child('users').child(auth.uid).child('devices').child($deviceId).val() === true || root.child('users').child(auth.uid).child('role').val() === 'admin')",
        ".write": "auth != null && (root.child('users').child(auth.uid).child('devices').child($deviceId).val() === true || root.child('users').child(auth.uid).child('role').val() === 'admin')",
        
        "relays": {
          "$relayId": {
            "state": {
              // Validate that state is strictly a boolean
              ".validate": "newData.isBoolean()"
            },
            "name": {
              ".validate": "newData.isString() && newData.val().length <= 32"
            }
          }
        },
        "online": {
          ".validate": "newData.isBoolean()"
        },
        "lastSeen": {
          ".validate": "newData.isNumber()"
        }
      }
    },
    "users": {
      "$uid": {
        // Users can only read and write their own profile
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid",
        
        "role": {
          // Prevent standard users from escalating themselves to admin
          ".write": "auth != null && root.child('users').child(auth.uid).child('role').val() === 'admin'"
        }
      }
    },
    "logs": {
      "$deviceId": {
        // Only device owners can read logs; append-only writes
        ".read": "auth != null && (root.child('users').child(auth.uid).child('devices').child($deviceId).val() === true || root.child('users').child(auth.uid).child('role').val() === 'admin')",
        "$logId": {
          ".write": "auth != null",
          ".validate": "newData.hasChildren(['relay', 'state', 'timestamp'])"
        }
      }
    }
  }
}
```

---

## 5. Deployment Instructions for Database Rules

1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```
2. Log in and initialize database rules:
   ```bash
   firebase login
   firebase init database
   ```
3. Save the JSON above into `database.rules.json`.
4. Deploy rules directly to production:
   ```bash
   firebase deploy --only database
   ```
5. Verify in Firebase Console under **Realtime Database $\rightarrow$ Rules tab**.
