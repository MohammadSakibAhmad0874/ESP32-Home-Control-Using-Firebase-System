# 🚀 Deploying Firebase Realtime Database Security Rules

This guide provides the commands and procedures to deploy production security rules to Firebase Realtime Database.

---

## 1. Prerequisites

1. Install the official Firebase CLI tool via Node.js / npm:
   ```bash
   npm install -g firebase-tools
   ```
2. Verify installation:
   ```bash
   firebase --version
   ```

---

## 2. Authentication & Project Linking

1. Log into your Google account associated with the Firebase project:
   ```bash
   firebase login
   ```
2. Check your active projects:
   ```bash
   firebase projects:list
   ```
3. Link this repository to your Firebase project:
   ```bash
   firebase use --add apnaghar-3f865
   ```

---

## 3. Validating & Deploying Security Rules

1. Inspect the rule definition file in [`database.rules.json`](../database.rules.json):
   - Verifies user authentication (`auth != null`).
   - Ensures user can only toggle devices they have claimed.
   - Enforces boolean validation on switch states.
2. Deploy only the database rules to production:
   ```bash
   firebase deploy --only database
   ```
3. Deployment confirmation output will display:
   ```
   === Deploying to 'apnaghar-3f865'...
   i  deploying database
   i  database: checking rules syntax...
   ✔  database: rules syntax for database apnaghar-3f865-default-rtdb is valid
   i  database: releasing rules...
   ✔  database: rules for database apnaghar-3f865-default-rtdb released successfully
   ✔  Deploy complete!
   ```

---

## 4. Testing Your Rules

You can verify the rules live in the Firebase Console:
1. Open [Firebase Console](https://console.firebase.google.com/) $\rightarrow$ **Realtime Database** $\rightarrow$ **Rules tab**.
2. Click **Rules Playground**.
3. Test a Simulated Read on `/devices/SH-001/relays`:
   - Without authentication: **Denied** ❌
   - With authenticated UID claiming `SH-001`: **Allowed** ✅
