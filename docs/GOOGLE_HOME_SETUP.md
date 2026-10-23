# 🗣️ Google Home & Google Assistant Integration Guide (Task 9B)

This document provides step-by-step instructions for deploying and configuring Google Assistant voice control for ApnaGhar ESP32 smart home switches.

---

## 1. Integration Flow

```mermaid
graph LR
    User([🗣️ "Hey Google, turn on Bedroom Lamp"]) --> Nest[Google Nest / Phone Assistant]
    Nest --> GoogleCloud[Google Smart Home Cloud]
    GoogleCloud --> Fulfillment[Firebase Cloud Function: smarthome]
    Fulfillment -->|admin.database().ref().set()| RTDB[("🔥 Firebase Realtime DB")]
    RTDB -->|Realtime Stream| ESP32[⚡ ESP32 Controller]
    ESP32 -->|GPIO 22 LOW| Relay[Relay 2 ON]
    Relay --> Lamp[💡 Bedroom Lamp]
```

---

## 2. Deploying Fulfillment Cloud Function

1. Open your terminal in `google-action/fulfillment`:
   ```bash
   cd google-action/fulfillment
   npm install
   ```
2. Deploy the fulfillment HTTPS endpoint using Firebase CLI:
   ```bash
   firebase deploy --only functions:smarthome
   ```
3. Copy the generated Function URL:
   `https://us-central1-apnaghar-3f865.cloudfunctions.net/smarthome`

---

## 3. Creating Google Actions Console Project

1. Navigate to the [Google Actions Console](https://console.actions.google.com/).
2. Click **New Project** $\rightarrow$ Name: `ApnaGhar Home Control`.
3. Choose **Smart Home** card $\rightarrow$ Click **Start Building**.
4. In **Fulfillment URL**, paste your deployed Cloud Function URL:
   `https://us-central1-apnaghar-3f865.cloudfunctions.net/smarthome`
5. Under **Quick Setup $\rightarrow$ Setup Account Linking**:
   - Grant Type: **Authorization Code**
   - Client ID: `apnaghar-google-client`
   - Client Secret: `ApnaGharGoogleSecret@2026`
   - Authorization URL: `https://<PROJECT-ID>.firebaseapp.com/__/auth/handler`
   - Token URL: `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<API-KEY>`
   - Scopes: `email, profile`

---

## 4. Testing with Google Home App

1. On your smartphone, open the **Google Home App**.
2. Tap **Add (+) $\rightarrow$ Set up device $\rightarrow$ Works with Google**.
3. Search for **[test] ApnaGhar Home Control**.
4. Log into your ApnaGhar account to link.
5. Your 4 switches will appear in the Google Home room selector!

### Sample Commands:
- *"Hey Google, turn on Living Room Light"*
- *"Hey Google, turn off the Fan"*
- *"Hey Google, is the Kitchen Light on?"*
- *"Hey Google, turn off all lights"*
