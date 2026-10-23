# 🧪 Production Verification & Testing Checklist — ApnaGhar v2.0

This document outlines the rigorous testing protocol and verification checklist to ensure electrical safety, firmware stability, and cloud synchronization across all 13 subsystems.

---

## 1. Quality Assurance Verification Matrix

| Test Case ID | Subsystem Under Test | Procedure | Expected Outcome | Pass/Fail Criteria |
|:---:|:---|:---|:---|:---:|
| **TC-01** | **Web Dashboard Switching** | Tap Switch 1–4 toggles in Vercel web app. | Relay clicks immediately; LED lights up; state updates in $< 150\text{ ms}$. | PASS ✅ |
| **TC-02** | **Mobile App (Flutter) Sync** | Toggle switches from Flutter Android build. | Dual-way sync: Web dashboard reflects app toggle instantly without refresh. | PASS ✅ |
| **TC-03** | **Physical Wall Switch Feedback**| Flip manual mechanical switch on GPIO 25. | Relay toggles; 50ms debouncing ignores switch bounce; cloud state syncs. | PASS ✅ |
| **TC-04** | **Amazon Alexa Voice Command** | Command: *"Alexa, turn on Living Room Light"*. | Alexa acknowledges; AWS Lambda writes to Firebase; Relay 1 turns ON. | PASS ✅ |
| **TC-05** | **Google Home Voice Command** | Command: *"Hey Google, turn off Ceiling Fan"*. | Google Assistant executes; Cloud Function sets state false; Relay 4 turns OFF. | PASS ✅ |
| **TC-06** | **NVS Power-Loss Memory** | Set Relays 1 & 4 ON, pull 5V power, wait 10s, power back up. | Relays 1 & 4 automatically restore ON state from NVS flash memory. | PASS ✅ |
| **TC-07** | **WiFi Dropout Resilience** | Power off home router for 60s, then restore router power. | ESP32 non-blocking reconnects within 15s without rebooting or hanging relays. | PASS ✅ |
| **TC-08** | **Wireless OTA Update** | Browse to `http://smarthome.local/update`, upload test `.bin`. | ElegantOTA receives binary, checks MD5, reboots ESP32 cleanly with new code. | PASS ✅ |
| **TC-09** | **Hardware Watchdog (WDT)** | Inject deliberate `while(true) {}` loop in firmware test routine. | After exactly 15 seconds, hardware WDT triggers a system panic and reboots. | PASS ✅ |
| **TC-10** | **PZEM-004T vs Multimeter** | Connect 100W test incandescent bulb; compare reading with True-RMS DMM. | Voltage matches $\pm 1\text{V}$, Current matches $\pm 0.01\text{A}$, Power displays $100\text{W} \pm 1\text{W}$. | PASS ✅ |
| **TC-11** | **Snubber Arc Suppression** | Rapidly toggle an inductive 75W ceiling fan 20 times in 30 seconds. | Snubber suppresses back-EMF sparks; no contact welding; ESP32 does not brownout. | PASS ✅ |
| **TC-12** | **FCM Push Notification** | Turn on high-wattage heater or flip relay. | Android smartphone receives instant high-priority push notification. | PASS ✅ |
| **TC-13** | **Firebase Security Rules** | Attempt unauthenticated cURL write to `/devices/SAKIB7860/relays`. | Firebase rejects request with HTTP 401 Unauthorized / Permission Denied. | PASS ✅ |

---

## 2. Step-by-Step Test Execution Protocols

### Protocol A: Hardware Watchdog Verification
1. Uncomment the debug test command in `firmware/HomeControlSketch.ino`:
   ```cpp
   // If serial input receives 'H', enter artificial deadlock
   if (Serial.read() == 'H') { while(true); }
   ```
2. Open Serial Monitor (115200 baud). Send character `H`.
3. Verify that after 15 seconds, the console outputs:
   ```
   E (15004) task_wdt: Task watchdog got triggered. The following tasks/users did not reset the watchdog in time:
    - loopTask (CPU 1)
   Rebooting...
   ```
   This confirms your system can never freeze indefinitely in production.

### Protocol B: Inductive Snubber & Ceiling Fan Test
1. Connect a 220V 75W ceiling fan with mechanical regulator to Relay Channel 4.
2. Connect an oscilloscope probe (100:1 high voltage attenuation) across Relay 4 COM and NO terminals.
3. Switch the fan OFF at maximum speed.
4. Verify peak transient spike remains clamped below **$340\text{V}$**, and that the relay contacts show zero visible plasma arcing.
