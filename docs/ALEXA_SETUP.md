# 🗣️ Amazon Alexa Smart Home Skill Setup (Task 9A)

This document provides step-by-step instructions for deploying and linking the ApnaGhar Alexa Smart Home Skill to control your ESP32 switches by voice.

---

## 1. Architecture

```mermaid
graph LR
    User([🗣️ "Alexa, turn on Living Room Light"]) --> Echo[Amazon Echo / Alexa App]
    Echo --> AlexaCloud[Alexa Smart Home Skill v3]
    AlexaCloud --> Lambda[AWS Lambda: alexa-skill/lambda]
    Lambda -->|admin.database().ref().set()| RTDB[("🔥 Firebase Realtime DB")]
    RTDB -->|Event Stream| ESP32[⚡ ESP32 Controller]
    ESP32 -->|GPIO 23 LOW| Relay[Relay 1 ON]
    Relay --> Light[💡 Living Room Light]
```

---

## 2. Deploying AWS Lambda Function

1. Log into the [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **AWS Lambda** $\rightarrow$ Click **Create Function**.
   - Name: `ApnaGharSmartHomeSkill`
   - Runtime: **Node.js 18.x**
   - Architecture: `x86_64`
3. Add Trigger $\rightarrow$ Select **Alexa Smart Home**:
   - Provide your Alexa Skill ID (generated in Section 3).
4. Upload code:
   ```bash
   cd alexa-skill/lambda
   npm install
   zip -r function.zip .
   ```
   Upload `function.zip` to the Lambda code console.
5. Copy the function ARN:
   `arn:aws:lambda:us-east-1:xxxxxxxxxxxx:function:ApnaGharSmartHomeSkill`

---

## 3. Creating the Alexa Developer Skill

1. Open [Amazon Alexa Developer Console](https://developer.amazon.com/alexa/console/ask).
2. Click **Create Skill**:
   - Name: `ApnaGhar Smart Home`
   - Model: **Smart Home**
   - Hosting: **Provision your own (AWS Lambda)**
3. Under **Smart Home $\rightarrow$ Default endpoint**:
   - Paste the Lambda ARN from Step 2.5.
4. Save endpoints.

---

## 4. Account Linking (OAuth2 with Firebase)

1. Under **Account Linking** in Alexa Developer Console:
   - Authorization URI: `https://<PROJECT-ID>.firebaseapp.com/__/auth/handler`
   - Access Token URI: `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<API-KEY>`
   - Client ID: `apnaghar-alexa-client`
   - Client Secret: `ApnaGharAlexaSecret@2026`
   - Scope: `read,write`

---

## 5. Voice Commands Supported

Once linked in the Alexa mobile app, tap **Discover Devices**. Alexa will add 4 endpoints:
- *"Alexa, turn on Living Room Light"*
- *"Alexa, turn off Bedroom Lamp"*
- *"Alexa, is the Ceiling Fan on?"*
- *"Alexa, turn off Kitchen Light"*
