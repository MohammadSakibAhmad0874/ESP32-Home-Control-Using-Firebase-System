"""
ApnaGhar v2.0 — 15-Slide PPTX Presentation Generator
Run: python generate_pptx.py
Creates: ApnaGhar_v2.0_Presentation.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
import qrcode
import io
import os
import struct, zlib

# ── Color Palette ──────────────────────────────────────────────────────────
DEEP_PURPLE  = RGBColor(0x0d, 0x08, 0x20)   # #0d0820
AUBERGINE    = RGBColor(0x3A, 0x0F, 0x34)   # #3A0F34
MARIGOLD     = RGBColor(0xEA, 0xAA, 0x00)   # #EAAA00
ICE_SILVER   = RGBColor(0xDD, 0xE3, 0xE8)   # #DDE3E8
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY   = RGBColor(0xB0, 0xB8, 0xC4)
GREEN        = RGBColor(0x22, 0xC5, 0x5E)
RED_COLOR    = RGBColor(0xEF, 0x44, 0x44)

LIVE_URL = "https://web-iota-ruddy-37.vercel.app"
GITHUB_URL = "https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System"
FIREBASE_URL = "https://console.firebase.google.com/project/apnaghar-3f865"

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]

def make_solid_png(w, h, r, g, b):
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    raw = b''.join(b'\x00' + bytes([r,g,b]*w) for _ in range(h))
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

def add_bg(slide, r=0x0d, g=0x08, b=0x20):
    """Fill slide background."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)

def txb(slide, text, l, t, w, h, sz=24, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    box.word_wrap = wrap
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(sz)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box

def accent_bar(slide, l=0, t=0, w=13.33, h=0.07, color=MARIGOLD):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()

def make_qr_image(url):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="#0d0820")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 1: Title
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 13.33, 0.08, MARIGOLD)
accent_bar(slide, 0, 7.42, 13.33, 0.08, MARIGOLD)

txb(slide, "🏠  ApnaGhar v2.0", 0.5, 1.2, 12, 1.4, sz=52, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(slide, "ESP32 Home Control Using Firebase", 0.5, 2.6, 12, 0.7, sz=26, color=MARIGOLD, align=PP_ALIGN.CENTER)
txb(slide, "Production Release  •  13 Engineering Tasks Completed  •  Firebase + Flutter + Voice AI", 0.5, 3.3, 12, 0.6, sz=16, color=ICE_SILVER, align=PP_ALIGN.CENTER)

# Divider
shape = slide.shapes.add_shape(1, Inches(4), Inches(4.0), Inches(5.33), Inches(0.03))
shape.fill.solid(); shape.fill.fore_color.rgb = AUBERGINE; shape.line.fill.background()

txb(slide, "Mohammad Sakib Ahmad  |  @MohammadSakibAhmad0874", 0.5, 4.2, 12, 0.5, sz=15, color=LIGHT_GREY, align=PP_ALIGN.CENTER)
txb(slide, "October 2026", 0.5, 4.7, 12, 0.4, sz=13, color=LIGHT_GREY, align=PP_ALIGN.CENTER)

# Mini tech pills
for i, (label, col) in enumerate([("ESP32", MARIGOLD), ("Firebase", RGBColor(0xFF,0xCA,0x28)), ("Flutter", RGBColor(0x54,0xC5,0xF8)), ("Alexa", RGBColor(0x1B,0xC4,0xE6))]):
    x = 2.7 + i * 2.1
    box = slide.shapes.add_shape(1, Inches(x), Inches(5.5), Inches(1.8), Inches(0.45))
    box.fill.solid(); box.fill.fore_color.rgb = AUBERGINE; box.line.color.rgb = col; box.line.width = Pt(1.2)
    txb(slide, label, x, 5.5, 1.8, 0.45, sz=13, bold=True, color=col, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 2: Problem Statement
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "❌  The Problem", 0.6, 0.3, 11, 0.7, sz=36, bold=True, color=MARIGOLD)
txb(slide, "Traditional Home Control is Broken", 0.6, 1.05, 11, 0.5, sz=20, color=ICE_SILVER)

problems = [
    ("🔘  Manual Switches Only", "No remote control — must be physically present"),
    ("📡  No Internet Control", "Can't turn off AC from office or control from phone"),
    ("🔋  Power Wasted", "No energy monitoring — no idea what consumes how much"),
    ("🔌  No Safety", "No surge protection, no brownout recovery, no watchdog"),
    ("🔔  No Alerts", "Appliance left on? No notification, no awareness"),
    ("🗣️  No Voice Control", "Alexa/Google Home not integrated with local hardware"),
]
for i, (title, desc) in enumerate(problems):
    y = 1.7 + i * 0.85
    box = slide.shapes.add_shape(1, Inches(0.6), Inches(y), Inches(11.8), Inches(0.72))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x1a, 0x10, 0x30)
    box.line.color.rgb = RED_COLOR; box.line.width = Pt(0.8)
    txb(slide, title, 0.9, y+0.05, 4, 0.62, sz=14, bold=True, color=RED_COLOR)
    txb(slide, desc, 4.5, y+0.05, 8, 0.62, sz=13, color=LIGHT_GREY)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 3: Our Solution — 3-Mode Architecture
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "✅  Our Solution — Hybrid 3-Mode Architecture", 0.6, 0.3, 12, 0.65, sz=30, bold=True, color=MARIGOLD)

modes = [
    ("☁️  CLOUD MODE", "Via Firebase RTDB", "Control from anywhere in the world\nReal-time WebSocket streaming (<120ms)\nFCM push notifications", MARIGOLD),
    ("📡  LOCAL MODE", "Via mDNS on LAN", "Control on local WiFi\nFastAPI REST endpoint\nWorks when Firebase is slow", RGBColor(0x54,0xC5,0xF8)),
    ("📶  OFFLINE MODE", "Via ESP32 Access Point", "Always-on AP: SmartHome_Control\nCaptive portal on 192.168.4.1\nWorks with ZERO internet", GREEN),
]
for i, (title, sub, desc, col) in enumerate(modes):
    x = 0.5 + i * 4.28
    box = slide.shapes.add_shape(1, Inches(x), Inches(1.1), Inches(3.9), Inches(5.8))
    box.fill.solid(); box.fill.fore_color.rgb = AUBERGINE
    box.line.color.rgb = col; box.line.width = Pt(2)
    txb(slide, title, x, 1.2, 3.9, 0.6, sz=18, bold=True, color=col, align=PP_ALIGN.CENTER)
    txb(slide, sub,   x, 1.85, 3.9, 0.4, sz=12, color=LIGHT_GREY, align=PP_ALIGN.CENTER, italic=True)
    accent_bar(slide, x+0.2, 2.3, 3.5, 0.04, col)
    txb(slide, desc, x+0.2, 2.4, 3.5, 3.5, sz=13, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 4: System Architecture
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🏛️  System Architecture", 0.6, 0.25, 12, 0.6, sz=32, bold=True, color=MARIGOLD)

arch_text = """
📱 Flutter App ──────────────────────────────────┐
💻 Web Dashboard (Vercel) ───────────────────────┤
🗣️ Alexa Skill (AWS Lambda) ─────────────────────┤──► 🔥 Firebase RTDB ◄══EVENT STREAM══► ⚡ ESP32
🗣️ Google Action (Cloud Functions) ──────────────┤        (apnaghar-3f865)                    │
🔘 Physical Wall Switches ───────────────────────┘                                             │
                                                    📲 FCM Push ──────────────────────────┐    │
                                                                                          ▼    ▼
                                                                                  📱 Phone Alert
                                                                          
ESP32 Hardware Stack:
├── 15s FreeRTOS Watchdog (auto-reboot)      ├── ElegantOTA at /update
├── 4× Relay (GPIO 23,22,21,19)             ├── PZEM-004T UART Power Meter
└── 4× Wall Switch (GPIO 25,26,27,32)       └── HLK-PM01 AC-DC + MOV Surge
"""
txb(slide, arch_text, 0.6, 1.0, 12, 5.8, sz=11, color=ICE_SILVER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 5: Hardware
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "⚡  Hardware Design", 0.6, 0.25, 12, 0.6, sz=32, bold=True, color=MARIGOLD)

# Left: components
components = [
    ("ESP32 DevKit V1", "Dual-Core 240MHz, 520KB RAM, WiFi+BT"),
    ("4-Relay Module (10A)", "JD-VCC isolated, EL817 optocouplers"),
    ("PZEM-004T v3.0", "UART energy monitor: V/A/W/kWh ±0.5%"),
    ("HLK-PM01", "AC-DC 5V isolated power supply"),
    ("14D431K MOV", "Transient surge clamp <340V"),
    ("RC Snubber", "100nF X2 + 100Ω 2W — arc suppression"),
]
for i, (comp, desc) in enumerate(components):
    y = 1.0 + i * 0.95
    txb(slide, f"• {comp}", 0.6, y, 5, 0.45, sz=15, bold=True, color=MARIGOLD)
    txb(slide, desc, 0.6, y+0.42, 5.5, 0.42, sz=12, color=LIGHT_GREY)

# Right: pin table
txb(slide, "GPIO Pin Mapping", 7.0, 0.9, 5.8, 0.45, sz=16, bold=True, color=WHITE)
pins = [("GPIO 23","Relay 1 — Living Room Light"),("GPIO 22","Relay 2 — Bedroom Lamp"),("GPIO 21","Relay 3 — Kitchen Light"),
        ("GPIO 19","Relay 4 — Ceiling Fan"),("GPIO 25","Switch 1 (50ms debounce)"),("GPIO 26","Switch 2"),
        ("GPIO 27","Switch 3"),("GPIO 32","Switch 4"),("GPIO 17","PZEM TX"),("GPIO 16","PZEM RX")]
for i, (pin, label) in enumerate(pins):
    y = 1.4 + i * 0.58
    col_bg = RGBColor(0x1a,0x10,0x30) if i%2==0 else AUBERGINE
    box = slide.shapes.add_shape(1, Inches(7.0), Inches(y), Inches(5.8), Inches(0.52))
    box.fill.solid(); box.fill.fore_color.rgb = col_bg; box.line.fill.background()
    txb(slide, pin, 7.05, y+0.04, 1.5, 0.44, sz=12, bold=True, color=MARIGOLD)
    txb(slide, label, 8.6, y+0.04, 4.1, 0.44, sz=12, color=ICE_SILVER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 6: Firebase & Security
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🔥  Firebase — Security & Realtime DB", 0.6, 0.25, 12, 0.6, sz=30, bold=True, color=MARIGOLD)

rules_text = '''{
  "rules": {
    ".read": false,
    ".write": false,
    "devices": {
      "$deviceId": {
        ".read": "auth != null && auth.uid == data.child('owner').val()",
        ".write": "auth != null && auth.uid == data.child('owner').val()",
        "relays": { ".validate": "newData.hasChildren(['relay1','relay2','relay3','relay4'])" },
        "sensors": { ".write": false }
      }
    }
  }
}'''
txb(slide, "database.rules.json (Production)", 0.6, 1.0, 6.0, 0.45, sz=14, bold=True, color=GREEN)
txb(slide, rules_text, 0.6, 1.5, 6.2, 5.5, sz=10, color=ICE_SILVER)

# Right: DB schema
txb(slide, "Firebase RTDB Schema", 7.2, 1.0, 5.5, 0.45, sz=14, bold=True, color=MARIGOLD)
schema = ("apnaghar-3f865-rtdb/\n"
          "└── devices/\n"
          "    └── SH-001/\n"
          "        ├── owner: uid\n"
          "        ├── relays/\n"
          "        │   ├── relay1: true/false\n"
          "        │   ├── relay2: true/false\n"
          "        │   ├── relay3: true/false\n"
          "        │   └── relay4: true/false\n"
          "        └── sensors/\n"
          "            ├── voltage: 230.5\n"
          "            ├── current: 1.24\n"
          "            ├── power: 285.8\n"
          "            └── energy: 0.048")
txb(slide, schema, 7.2, 1.6, 5.6, 5.5, sz=12, color=ICE_SILVER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 7: 13 Tasks Matrix
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 13.33, 0.08, MARIGOLD)

txb(slide, "✅  All 13 Engineering Tasks — DONE", 0.3, 0.15, 12.5, 0.65, sz=28, bold=True, color=MARIGOLD, align=PP_ALIGN.CENTER)

tasks = [
    ("1","Firebase SDK Streaming","<120ms WebSocket event-driven (replaces 2s polling)"),
    ("2","Firebase Security Rules","Strict UID auth scope — no open read/write"),
    ("3","Token Auto-Refresh","TokenHelper.h — OAuth2 refresh before 3600s expiry"),
    ("4","PZEM-004T Sensing","V/A/W/kWh ±0.5% via UART (GPIO 16,17)"),
    ("5","OTA Updates","ElegantOTA at http://smarthome.local/update"),
    ("6","Hardware WDT","15s FreeRTOS Task Watchdog — auto reboot on hang"),
    ("7","Custom 2-Layer PCB","8mm HV isolation, KiCad + JLCPCB Gerbers ready"),
    ("8","UL94 V-0 Enclosure","Parametric OpenSCAD, dual AC/DC compartment"),
    ("9","Voice Assistant Skills","Alexa Smart Home v3 + Google Actions fulfillment"),
    ("10","Flutter Release Build","Signed keystore, Play Store AAB generated"),
    ("11","FCM Push Notifications","Relay flip + power surge alerts to phone"),
    ("12","Manual Wall Switch","GPIO 25-32 debounced, bidirectional cloud sync"),
    ("13","Snubber + MOV Circuit","RC 100nF/100Ω + 14D431K clamps <340V"),
]
cols = 2
per_col = 7
for col_idx in range(cols):
    x_base = 0.3 + col_idx * 6.65
    for i in range(per_col):
        idx = col_idx * per_col + i
        if idx >= len(tasks): break
        num, title, desc = tasks[idx]
        y = 1.0 + i * 0.9
        box = slide.shapes.add_shape(1, Inches(x_base), Inches(y), Inches(6.2), Inches(0.78))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x1a,0x10,0x30) if i%2==0 else AUBERGINE
        box.line.fill.background()
        txb(slide, f"  #{num}", x_base, y+0.07, 0.8, 0.6, sz=12, bold=True, color=MARIGOLD)
        txb(slide, title, x_base+0.75, y+0.07, 2.2, 0.35, sz=12, bold=True, color=WHITE)
        txb(slide, desc, x_base+0.75, y+0.42, 5.1, 0.32, sz=10, color=LIGHT_GREY)
        txb(slide, "✅", x_base+5.85, y+0.15, 0.4, 0.5, sz=16, color=GREEN)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 8: 17 Bugs Fixed
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🛡️  17 Bugs Found & Fixed", 0.6, 0.25, 12, 0.6, sz=32, bold=True, color=MARIGOLD)

categories = [
    ("🔴  CRITICAL (4)", RED_COLOR, [
        "Exposed Firebase API Key in source code",
        "Open database rules — anyone could read/write",
        "Brownout reset triggered by relay switching",
        "2s HTTP REST polling — high latency + battery drain",
    ]),
    ("🟠  HIGH (5)", RGBColor(0xF9,0x73,0x16), [
        "Firebase token expired after 1hr — device disconnected",
        "No SSL certificate pinning",
        "Blocking WiFi reconnect hung main loop",
        "No Hardware Watchdog — device stuck forever on crash",
        "No OTA update path — needed physical reflash",
    ]),
    ("🟡  MEDIUM + LOW (8)", MARIGOLD, [
        "No manual switch feedback to cloud",
        "No inductive load arc suppression (relay damage)",
        "No energy monitoring",
        "CORS misconfigured on backend",
        "+ 4 more low-severity UI/UX issues",
    ]),
]
y = 1.05
for cat_title, cat_color, bugs in categories:
    txb(slide, cat_title, 0.6, y, 12, 0.45, sz=16, bold=True, color=cat_color)
    y += 0.48
    for bug in bugs:
        txb(slide, f"   • {bug}", 0.6, y, 12, 0.38, sz=12, color=LIGHT_GREY)
        y += 0.38
    y += 0.12

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 9: Live Demo — Website + APK QR Codes
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🚀  Live Demo", 0.6, 0.25, 12, 0.6, sz=36, bold=True, color=MARIGOLD)

# Web QR
qr_web = make_qr_image(LIVE_URL)
slide.shapes.add_picture(qr_web, Inches(1.0), Inches(1.2), Inches(3.5), Inches(3.5))
txb(slide, "🌐  Web Dashboard", 0.6, 4.8, 4.5, 0.5, sz=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(slide, LIVE_URL, 0.5, 5.35, 4.7, 0.5, sz=11, color=MARIGOLD, align=PP_ALIGN.CENTER)

# GitHub QR
qr_gh = make_qr_image(GITHUB_URL)
slide.shapes.add_picture(qr_gh, Inches(5.0), Inches(1.2), Inches(3.5), Inches(3.5))
txb(slide, "📦  GitHub Repository", 4.7, 4.8, 4.5, 0.5, sz=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(slide, "MohammadSakibAhmad0874", 4.7, 5.35, 4.5, 0.5, sz=11, color=MARIGOLD, align=PP_ALIGN.CENTER)

# Firebase QR
qr_fb = make_qr_image(FIREBASE_URL)
slide.shapes.add_picture(qr_fb, Inches(9.0), Inches(1.2), Inches(3.5), Inches(3.5))
txb(slide, "🔥  Firebase Console", 8.7, 4.8, 4.5, 0.5, sz=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(slide, "apnaghar-3f865", 8.7, 5.35, 4.5, 0.5, sz=11, color=MARIGOLD, align=PP_ALIGN.CENTER)

txb(slide, "Scan QR codes for live access", 0.3, 6.7, 12.7, 0.5, sz=13, color=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 10: Firmware Highlights
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "⚡  Firmware Highlights", 0.6, 0.25, 12, 0.6, sz=32, bold=True, color=MARIGOLD)

highlights = [
    ("🔄  Firebase Streaming", "firebaseStream.h",
     "Firebase_ESP_Client event listener replaces 2s HTTP polling\n<120ms relay response time • TokenHelper auto-refreshes OAuth2"),
    ("⏱️  Hardware Watchdog", "watchdog.h",
     "FreeRTOS esp_task_wdt 15s timeout\nAuto-reboot if main loop hangs (power spike, deadlock)"),
    ("📡  OTA Updates", "otaManager.h",
     "ElegantOTA web UI at http://smarthome.local/update\nArduinoOTA for IDE flashing • No physical access needed"),
    ("💾  NVS Persistence", "config.h",
     "WiFi credentials + device ID stored in flash NVS\nSurvives power cuts — auto-reconnects in <5s"),
]
for i, (title, file, desc) in enumerate(highlights):
    y = 1.05 + i * 1.55
    box = slide.shapes.add_shape(1, Inches(0.6), Inches(y), Inches(12), Inches(1.35))
    box.fill.solid(); box.fill.fore_color.rgb = AUBERGINE; box.line.color.rgb = MARIGOLD; box.line.width = Pt(1)
    txb(slide, title, 0.85, y+0.07, 5, 0.5, sz=16, bold=True, color=MARIGOLD)
    txb(slide, f"📄 {file}", 6.5, y+0.1, 5.8, 0.4, sz=12, color=MARIGOLD, align=PP_ALIGN.RIGHT, italic=True)
    txb(slide, desc, 0.85, y+0.58, 11.5, 0.75, sz=12, color=ICE_SILVER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 11: PCB + Enclosure
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🔌  Custom PCB + 3D Enclosure", 0.6, 0.25, 12, 0.6, sz=30, bold=True, color=MARIGOLD)

# PCB section
txb(slide, "Custom 2-Layer PCB", 0.6, 1.0, 6, 0.45, sz=18, bold=True, color=WHITE)
pcb_specs = [
    "• 100mm × 80mm footprint",
    "• 2oz copper pour, 2-layer",
    "• 8.0mm high-voltage isolation slot (IPC-2221)",
    "• 4× EL817 optocouplers for relay isolation",
    "• HLK-PM01 onboard AC-DC 5V supply",
    "• PZEM-004T header (UART)",
    "• JLCPCB gerber.zip ready for fabrication ($12 for 5 boards)",
]
for i, spec in enumerate(pcb_specs):
    txb(slide, spec, 0.8, 1.55 + i*0.72, 6.2, 0.6, sz=13, color=ICE_SILVER)

# Enclosure section
txb(slide, "UL94 V-0 3D Printable Enclosure", 7.2, 1.0, 5.8, 0.45, sz=18, bold=True, color=WHITE)
enc_specs = [
    "• Material: ABS (UL94 V-0 flame retardant)",
    "• Parametric OpenSCAD design",
    "• Dual-compartment: AC side / DC side",
    "• Internal ABS barrier (8mm thick)",
    "• Ventilation slots for airflow",
    "• DIN rail mount points",
    "• Run: openscad enclosure.scad → export STL",
]
for i, spec in enumerate(enc_specs):
    txb(slide, spec, 7.4, 1.55 + i*0.72, 5.6, 0.6, sz=13, color=ICE_SILVER)

accent_bar(slide, 6.8, 1.0, 0.04, 6.2, RGBColor(0x40,0x20,0x60))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 12: Voice Control
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "🗣️  Voice Assistant Control", 0.6, 0.25, 12, 0.6, sz=32, bold=True, color=MARIGOLD)

# Alexa
txb(slide, "Amazon Alexa — Smart Home v3", 0.6, 1.0, 6, 0.5, sz=20, bold=True, color=RGBColor(0x1B,0xC4,0xE6))
alexa_cmds = ['"Alexa, turn on the living room light"','"Alexa, turn off bedroom lamp"','"Alexa, turn on all lights"','"Alexa, what is the status of the fan?"','"Alexa, discover my devices"']
for i, cmd in enumerate(alexa_cmds):
    box = slide.shapes.add_shape(1, Inches(0.6), Inches(1.6+i*0.95), Inches(6.2), Inches(0.75))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x0b,0x1e,0x2e); box.line.color.rgb = RGBColor(0x1B,0xC4,0xE6); box.line.width = Pt(0.8)
    txb(slide, cmd, 0.8, 1.65+i*0.95, 5.8, 0.6, sz=13, color=WHITE, italic=True)

# Google
txb(slide, "Google Assistant — Smart Home Actions", 7.0, 1.0, 6, 0.5, sz=20, bold=True, color=RGBColor(0x4C,0xAF,0x50))
google_cmds = ['"Hey Google, turn on the kitchen light"','"Hey Google, turn off the fan"','"Hey Google, turn on all devices"','"Hey Google, is the bedroom lamp on?"','"Hey Google, sync devices"']
for i, cmd in enumerate(google_cmds):
    box = slide.shapes.add_shape(1, Inches(7.0), Inches(1.6+i*0.95), Inches(6.0), Inches(0.75))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x0b,0x2b,0x0e); box.line.color.rgb = RGBColor(0x4C,0xAF,0x50); box.line.width = Pt(0.8)
    txb(slide, cmd, 7.2, 1.65+i*0.95, 5.6, 0.6, sz=13, color=WHITE, italic=True)

txb(slide, "Both skills linked to Firebase for realtime device control — no cloud latency", 0.3, 6.9, 12.7, 0.4, sz=12, color=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 13: Power Sensing — PZEM-004T
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 0.25, 7.5, MARIGOLD)

txb(slide, "⚡  Energy Monitoring — PZEM-004T v3.0", 0.6, 0.25, 12, 0.6, sz=28, bold=True, color=MARIGOLD)

metrics = [
    ("Voltage", "230.5 V", "±0.5%"),
    ("Current", "1.24 A", "±0.5%"),
    ("Active Power", "285.8 W", "±0.5%"),
    ("Energy (kWh)", "0.048 kWh", "±0.5%"),
    ("Frequency", "50.0 Hz", "±0.5%"),
    ("Power Factor", "0.98", "±0.5%"),
]
for i, (label, val, acc) in enumerate(metrics):
    x = 0.6 + (i % 3) * 4.2
    y = 1.15 + (i // 3) * 2.2
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.8), Inches(1.9))
    box.fill.solid(); box.fill.fore_color.rgb = AUBERGINE; box.line.color.rgb = MARIGOLD; box.line.width = Pt(1.5)
    txb(slide, label, x, y+0.1, 3.8, 0.5, sz=14, color=LIGHT_GREY, align=PP_ALIGN.CENTER)
    txb(slide, val, x, y+0.62, 3.8, 0.7, sz=24, bold=True, color=MARIGOLD, align=PP_ALIGN.CENTER)
    txb(slide, acc, x, y+1.35, 3.8, 0.4, sz=11, color=GREEN, align=PP_ALIGN.CENTER)

txb(slide, "Connection: PZEM-004T TX→GPIO16, RX→GPIO17  |  CT clamp on Live wire only  |  Isolated 5V supply", 0.3, 5.7, 12.7, 0.5, sz=12, color=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 14: Live Links
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 13.33, 0.08, MARIGOLD)
accent_bar(slide, 0, 7.42, 13.33, 0.08, MARIGOLD)

txb(slide, "🔗  All Live Links & Artifacts", 0.3, 0.2, 12.7, 0.6, sz=32, bold=True, color=MARIGOLD, align=PP_ALIGN.CENTER)

links = [
    ("🌐  Web Dashboard (LIVE)", LIVE_URL, GREEN),
    ("📦  GitHub Repository", GITHUB_URL, RGBColor(0x64,0xB5,0xF6)),
    ("🔥  Firebase Console", FIREBASE_URL, RGBColor(0xFF,0xCA,0x28)),
    ("⚡  Vercel Inspector", "https://vercel.com/ahmadsakib263-4202s-projects/web", RGBColor(0x00,0x00,0x00)),
    ("🤖  Railway Backend", "https://esp32-home-control-using-firebase-system-production.up.railway.app", RGBColor(0x8B,0x5C,0xF6)),
    ("📄  APK (local)", "./ApnaGhar-v2.0-release.apk", MARIGOLD),
    ("📊  PPTX", "./ApnaGhar_v2.0_Presentation.pptx", MARIGOLD),
    ("🔩  Firmware Flash Guide", "firmware/HomeControlSketch.ino  →  Arduino IDE  →  ESP32 Dev Module", ICE_SILVER),
]
for i, (label, url, col) in enumerate(links):
    y = 1.0 + i * 0.78
    box = slide.shapes.add_shape(1, Inches(0.4), Inches(y), Inches(12.5), Inches(0.65))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x1a,0x10,0x30) if i%2==0 else AUBERGINE; box.line.fill.background()
    txb(slide, label, 0.6, y+0.08, 4.2, 0.5, sz=13, bold=True, color=col)
    txb(slide, url, 4.8, y+0.08, 8.0, 0.5, sz=11, color=LIGHT_GREY, italic=True)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 15: Future Roadmap + Thank You
# ═══════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
accent_bar(slide, 0, 0, 13.33, 0.08, MARIGOLD)
accent_bar(slide, 0, 7.42, 13.33, 0.08, MARIGOLD)

txb(slide, "🚀  Roadmap + Thank You", 0.5, 0.2, 12, 0.65, sz=36, bold=True, color=MARIGOLD, align=PP_ALIGN.CENTER)
txb(slide, "ApnaGhar is production-ready — here is what comes next:", 0.5, 0.95, 12, 0.45, sz=16, color=LIGHT_GREY, align=PP_ALIGN.CENTER)

roadmap = [
    ("v2.1", "Matter/Thread protocol support (Apple Home, Samsung SmartThings)"),
    ("v2.2", "ESP32-S3 upgrade: USB-OTG, AI accelerator for on-device TinyML"),
    ("v2.3", "Solar panel + battery integration with charging MPPT controller"),
    ("v2.4", "Multi-room grouping + scenes (\"Movie Time\" = dim + fan + lock)"),
    ("v3.0", "Full local-only mode with Home Assistant integration"),
]
for i, (ver, desc) in enumerate(roadmap):
    y = 1.55 + i * 0.78
    box = slide.shapes.add_shape(1, Inches(0.5), Inches(y), Inches(11.9), Inches(0.65))
    box.fill.solid(); box.fill.fore_color.rgb = AUBERGINE; box.line.color.rgb = MARIGOLD; box.line.width = Pt(0.8)
    txb(slide, ver, 0.7, y+0.1, 1.2, 0.5, sz=14, bold=True, color=MARIGOLD)
    txb(slide, desc, 2.0, y+0.1, 10.2, 0.5, sz=13, color=ICE_SILVER)

txb(slide, "🙏  Thank You!", 0.5, 5.65, 12, 0.65, sz=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(slide, "Mohammad Sakib Ahmad  |  @MohammadSakibAhmad0874  |  IoT Engineer", 0.5, 6.35, 12, 0.4, sz=14, color=LIGHT_GREY, align=PP_ALIGN.CENTER)
txb(slide, GITHUB_URL, 0.5, 6.8, 12, 0.4, sz=12, color=MARIGOLD, italic=True, align=PP_ALIGN.CENTER)

# ── Save ─────────────────────────────────────────────────────────────────
output_path = 'ApnaGhar_v2.0_Presentation.pptx'
prs.save(output_path)
print(f"\n[OK] Saved: {output_path}")
print(f"   Slides: 15")
print(f"   Size: {os.path.getsize(output_path):,} bytes")
print("   Open with PowerPoint or Google Slides.")
