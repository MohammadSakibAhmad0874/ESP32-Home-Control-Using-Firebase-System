"""
ApnaGhar v2.0 — Executive Modern Luxe Presentation Generator
Theme: Modern Luxe Slate & Glass (Platinum #F4F7FB, Crisp White #FFFFFF, Royal Slate #0F172A, Cyber Cyan #0284C7, Emerald #059669, Amber #D97706)
Includes: High-resolution 3D renders, large readable typography, layman analogies, and QR codes.
"""

import io
import os
import qrcode
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── Color Palette (Modern Luxe Tech) ──────────────────────────────────────────
BG_CANVAS      = RGBColor(0xF4, 0xF7, 0xFB) # Platinum Pearl Canvas
CARD_WHITE     = RGBColor(0xFF, 0xFF, 0xFF) # Pure Crisp White Card
CARD_BORDER    = RGBColor(0xCB, 0xD5, 0xE1) # Subtle Slate Border
TEXT_MAIN      = RGBColor(0x0F, 0x17, 0x2A) # Deep Royal Navy Text (Ultra readable)
TEXT_BODY      = RGBColor(0x33, 0x41, 0x55) # Slate Charcoal for body
TEXT_MUTED     = RGBColor(0x64, 0x74, 0x8B) # Subtle grey for metadata
CYAN_PRIMARY   = RGBColor(0x02, 0x84, 0xC7) # High-tech Sky Blue / Cyan
NAVY_HERO      = RGBColor(0x1E, 0x29, 0x3B) # Executive Hero Navy
AMBER_GOLD     = RGBColor(0xD9, 0x77, 0x06) # Warm Amber / Marigold
EMERALD_GREEN  = RGBColor(0x05, 0x96, 0x69) # Emerald Green for Success
CRIMSON_RED    = RGBColor(0xDC, 0x26, 0x26) # Alert Crimson
PURPLE_ROYAL   = RGBColor(0x7C, 0x3A, 0xED) # Royal Violet Accent

IMG_HARDWARE     = "assets/presentation/hardware_3d.jpg"
IMG_APPS         = "assets/presentation/apps_3d.jpg"
IMG_ARCHITECTURE = "assets/presentation/architecture_3d.jpg"
IMG_ENCLOSURE    = "assets/presentation/enclosure_3d.jpg"

LIVE_URL   = "https://web-mjdtvq623-ahmadsakib263-4202s-projects.vercel.app"
GITHUB_URL = "https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_canvas_bg(slide, bg_color=BG_CANVAS):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = bg_color

def add_card(slide, left, top, width, height, bg_color=CARD_WHITE, border_color=CARD_BORDER, border_width=1.5):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(border_width)
    return shape

def add_header(slide, tag_text, title_text, subtitle_text=""):
    # Pill Tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.4))
    tf_t = tag_box.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = f"★ {tag_text.upper()} ★"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_PRIMARY

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # Subtitle
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.5), Inches(0.55))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(16)
        p_s.font.color.rgb = AMBER_GOLD

def make_qr_image(url):
    qr = qrcode.QRCode(box_size=6, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: Hero Title Slide with 3D Hardware Image
# ══════════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s1, BG_CANVAS)

# Left Hero Card
add_card(s1, 0.8, 0.8, 6.2, 5.9, bg_color=CARD_WHITE, border_color=CYAN_PRIMARY, border_width=2.0)
tb1 = s1.shapes.add_textbox(Inches(1.1), Inches(1.1), Inches(5.6), Inches(5.3))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "★ PRODUCTION RELEASE v2.0 ★"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = AMBER_GOLD

p = tf1.add_paragraph()
p.text = "ApnaGhar"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = TEXT_MAIN
p.space_before = Pt(8)

p = tf1.add_paragraph()
p.text = "ESP32 Heavy-Duty Home Automation System with Firebase Realtime Sync"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = CYAN_PRIMARY
p.space_before = Pt(6)

p = tf1.add_paragraph()
p.text = "Plain English: Control lights, fans, and heavy ACs in 0.1 seconds from anywhere on Earth, with 100% electrical safety and zero blackout amnesia."
p.font.size = Pt(15)
p.font.color.rgb = TEXT_BODY
p.space_before = Pt(12)

p = tf1.add_paragraph()
p.text = "Lead Architect: Mohammad Sakib Ahmad\nStatus: Production Verified v2.0  |  Year: 2026"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = NAVY_HERO
p.space_before = Pt(16)

# Right: High-Res 3D Hardware Render Image
if os.path.exists(IMG_HARDWARE):
    add_card(s1, 7.3, 0.8, 5.2, 5.9, bg_color=CARD_WHITE, border_color=CARD_BORDER)
    s1.shapes.add_picture(IMG_HARDWARE, Inches(7.4), Inches(0.9), width=Inches(5.0), height=Inches(5.7))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: The Everyday Problem (Why Normal Switches & Cheap Plugs Break)
# ══════════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s2)
add_header(s2, "The Real-World Challenge", "Why Ordinary Home Switches & Cheap Plugs Fail", "Traditional switches waste power, and cheap smart modules freeze or catch fire.")

cards_prob = [
    ("Traditional Wall Switches", "SPARK HAZARDS & NO CONTROL", [
        "Cannot check if geyser or iron was left ON after leaving the house.",
        "Mechanical electrical arcing damages motors and appliances.",
        "Zero energy awareness — surprises you with massive electric bills."
    ], CRIMSON_RED),
    ("Cheap Smart Plugs", "FREEZES WHEN WI-FI DROPS", [
        "Cheap plugs stop working completely if home broadband drops.",
        "Blackout Amnesia: Randomly resets switch states after a power cut.",
        "No wall switch sync: Confuses family members when pressed physically."
    ], AMBER_GOLD),
    ("ApnaGhar v2.0 Solution", "MILITARY-GRADE RESILIENCE", [
        "Sub-100ms real-time control via Google Firebase Realtime Database.",
        "Surge-protected relay armor that handles heavy inductive AC loads.",
        "Family-Friendly: Physical wall switches and phone app stay 100% in sync."
    ], EMERALD_GREEN)
]

for idx, (title, tag, pts, col) in enumerate(cards_prob):
    x = 0.8 + idx * 3.95
    add_card(s2, x, 2.1, 3.75, 4.8, border_color=col)
    tb = s2.shapes.add_textbox(Inches(x + 0.25), Inches(2.3), Inches(3.25), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p2 = tf.add_paragraph()
    p2.text = tag
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = col
    p2.space_before = Pt(4)
    p2.space_after = Pt(10)
    
    for pt in pts:
        bp = tf.add_paragraph()
        bp.text = f"• {pt}"
        bp.font.size = Pt(15)
        bp.font.color.rgb = TEXT_BODY
        bp.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: Triple-Mode Architecture (Works Even When Wi-Fi Dies)
# ══════════════════════════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s3)
add_header(s3, "Fail-Safe Redundancy", "Triple-Mode Architecture: Never Leaves You In Dark", "Even if your home Wi-Fi cable is snapped, your switches still work.")

modes = [
    ("MODE 1: Global Cloud", "Google Firebase WebSocket", "Works Everywhere",
     "Control lights, fans, and ACs from your office, metro, or vacation in <0.1 second.",
     "Analogy: Like an open direct telephone line between your phone and your home.", CYAN_PRIMARY),
    ("MODE 2: Local Wi-Fi (mDNS)", "Home Network Direct Sync", "Works Offline (No Internet)",
     "If broadband internet fails, your phone toggles appliances directly via home router.",
     "Analogy: Phone talks straight to the ESP32 in your living room without cloud.", AMBER_GOLD),
    ("MODE 3: Emergency AP", "Direct Hardware Hotspot", "Router Dead Fallback",
     "ESP32 broadcasts its own Wi-Fi hotspot ('SmartHome_Control') with captive portal.",
     "Analogy: Connect phone Wi-Fi straight to the switch box to turn on your lights.", PURPLE_ROYAL)
]

for idx, (title, tech, status, desc, analogy, col) in enumerate(modes):
    x = 0.8 + idx * 3.95
    add_card(s3, x, 2.1, 3.75, 4.8, border_color=col)
    tb = s3.shapes.add_textbox(Inches(x + 0.25), Inches(2.3), Inches(3.25), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p_tech = tf.add_paragraph()
    p_tech.text = tech
    p_tech.font.size = Pt(14)
    p_tech.font.bold = True
    p_tech.font.color.rgb = col
    p_tech.space_before = Pt(4)
    
    p_stat = tf.add_paragraph()
    p_stat.text = f"[ Status: {status} ]"
    p_stat.font.size = Pt(13)
    p_stat.font.bold = True
    p_stat.font.color.rgb = EMERALD_GREEN
    p_stat.space_before = Pt(6)
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(15)
    p_desc.font.color.rgb = TEXT_BODY
    p_desc.space_before = Pt(10)
    
    p_lay = tf.add_paragraph()
    p_lay.text = f"💡 {analogy}"
    p_lay.font.size = Pt(14)
    p_lay.font.italic = True
    p_lay.font.color.rgb = AMBER_GOLD
    p_lay.space_before = Pt(12)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: End-to-End Architecture with 3D House Image
# ══════════════════════════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s4)
add_header(s4, "Engineering Pipeline", "End-to-End System Architecture", "How a tap on your phone or voice command powers a heavy room appliance.")

# Left 3D Architecture Graphic
if os.path.exists(IMG_ARCHITECTURE):
    add_card(s4, 0.8, 2.1, 5.8, 4.8, border_color=CYAN_PRIMARY)
    s4.shapes.add_picture(IMG_ARCHITECTURE, Inches(0.9), Inches(2.2), width=Inches(5.6), height=Inches(4.6))

# Right: Explanation Card
add_card(s4, 6.9, 2.1, 5.6, 4.8, border_color=CARD_BORDER)
tb_flow = s4.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.2), Inches(4.4))
tf = tb_flow.text_frame
tf.word_wrap = True

tf.paragraphs[0].text = "Architecture Dataflow Stages"
tf.paragraphs[0].font.size = Pt(21)
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.color.rgb = TEXT_MAIN

flow_items = [
    ("1. Client Layer:", "Flutter Android App, Web CDN Dashboard, or Alexa/Google Voice triggers a state toggle."),
    ("2. Realtime Cloud:", "Google Firebase RTDB processes update and pushes via WebSocket stream in <100ms."),
    ("3. Microcontroller:", "ESP32 dual-core chip receives JSON payload, verifies checksum, and triggers GPIO pin."),
    ("4. Electrical Isolation:", "Optocouplers pass light signals to trigger 230V mechanical relays with zero electrical interference."),
    ("5. Power Feedback:", "PZEM-004T measures true voltage, current, and wattage, sending real usage back to cloud.")
]

for title, desc in flow_items:
    p = tf.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(7)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: Hardware Deep Dive with Real ESP32 3D Photo
# ══════════════════════════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s5)
add_header(s5, "Hardware Blueprint", "ESP32 Pinout & Safety Isolation", "Strict electrical isolation between 230V AC high voltage and 3.3V DC logic.")

# Left: 3D Hardware Board Image
if os.path.exists(IMG_HARDWARE):
    add_card(s5, 0.8, 2.1, 5.8, 4.8, border_color=NAVY_HERO)
    s5.shapes.add_picture(IMG_HARDWARE, Inches(0.9), Inches(2.2), width=Inches(5.6), height=Inches(4.6))

# Right: Pinout & Layman Explanations
add_card(s5, 6.9, 2.1, 5.6, 4.8, border_color=CYAN_PRIMARY)
tb_h = s5.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.2), Inches(4.4))
tf_h = tb_h.text_frame
tf_h.word_wrap = True

tf_h.paragraphs[0].text = "Component Wiring & Role"
tf_h.paragraphs[0].font.size = Pt(21)
tf_h.paragraphs[0].font.bold = True
tf_h.paragraphs[0].font.color.rgb = TEXT_MAIN

hw_pins = [
    ("GPIO 23, 22, 21, 19:", "Triggers 4x Heavy-Duty Relays (Living Room, Bedroom, Kitchen, Fan/AC)."),
    ("GPIO 16 / 17 (UART2):", "Hardware Serial communication with PZEM-004T Energy Meter."),
    ("GPIO 25, 26, 27, 32:", "Wall switch sense pins with internal pull-up resistors."),
    ("Optocoupler Isolation:", "Light-based barrier separates 230V AC from sensitive 3.3V logic chip."),
    ("Staggered Power-On:", "Relays turn on with 50ms gaps to eliminate inductive brownout crashes.")
]

for title, desc in hw_pins:
    p = tf_h.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: Firebase Event Stream vs Old 2-Second Polling
# ══════════════════════════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s6)
add_header(s6, "Cloud Performance", "Firebase WebSocket Stream (<100ms)", "Why WebSocket event streaming crushes traditional HTTP polling.")

add_card(s6, 0.8, 2.1, 5.6, 4.8, border_color=CRIMSON_RED)
tb_old = s6.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_old = tb_old.text_frame
tf_old.word_wrap = True

tf_old.paragraphs[0].text = "❌ Old 2-Second Polling"
tf_old.paragraphs[0].font.size = Pt(21)
tf_old.paragraphs[0].font.bold = True
tf_old.paragraphs[0].font.color.rgb = CRIMSON_RED

old_pts = [
    "Device asked the server 'Anything new?' every 2 seconds in an endless loop.",
    "Wasted massive network bandwidth and overheated the Wi-Fi module.",
    "Noticeable delay: Lights took up to 2.5 seconds to turn ON.",
    "Exceeded database connection limits rapidly."
]
for op in old_pts:
    p = tf_old.add_paragraph()
    p.text = f"• {op}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(10)

add_card(s6, 6.8, 2.1, 5.7, 4.8, border_color=EMERALD_GREEN)
tb_new = s6.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_new = tb_new.text_frame
tf_new.word_wrap = True

tf_new.paragraphs[0].text = "✅ ApnaGhar v2.0 Event Streaming"
tf_new.paragraphs[0].font.size = Pt(21)
tf_new.paragraphs[0].font.bold = True
tf_new.paragraphs[0].font.color.rgb = EMERALD_GREEN

new_pts = [
    "Always-Open WebSocket Pipeline: Server pushes state instantly when tapped.",
    "Zero Delay: Sub-100 millisecond response time.",
    "95% Less Bandwidth: Silent when idle, zero unnecessary data usage.",
    "Auto Token Refresh: Keeps device authenticated 24/7 with zero lockouts."
]
for np in new_pts:
    p = tf_new.add_paragraph()
    p.text = f"• {np}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: The 13 Tasks Completed Matrix
# ══════════════════════════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s7)
add_header(s7, "Delivery Matrix", "13 Core Engineering Tasks: 100% Completed", "Complete production-ready implementation spanning firmware, cloud, mobile, and hardware.")

t_list1 = [
    ("1. Firebase Event Stream", "Sub-100ms push replacing 2s poll", "DONE ✅"),
    ("2. Firebase Security Rules", "User-isolated database permissions", "DONE ✅"),
    ("3. Token Auto-Refresh", "24/7 unattended cloud connection", "DONE ✅"),
    ("4. PZEM-004T Power Sensing", "Real voltage, current & kWh", "DONE ✅"),
    ("5. ElegantOTA Updates", "Browser-based wireless upgrade", "DONE ✅"),
    ("6. Hardware Watchdog (15s)", "Auto-reboot on chip hang", "DONE ✅"),
    ("7. NVS State Memory", "Restores switch state after outage", "DONE ✅")
]

t_list2 = [
    ("8. Manual Switch Feedback", "Physical switch updates phone", "DONE ✅"),
    ("9. RC Snubber + MOV", "Appliance spark & surge shield", "DONE ✅"),
    ("10. 2-Layer PCB Design", "Creepage isolation layout", "DONE ✅"),
    ("11. 3D Printable Enclosure", "UL94 V-0 flame-retardant box", "DONE ✅"),
    ("12. Voice Skills", "Alexa Skill & Google Action", "DONE ✅"),
    ("13. Flutter App & Web", "Signed APK, AAB & Vercel Dashboard", "DONE ✅")
]

add_card(s7, 0.8, 2.1, 5.7, 4.8, border_color=CYAN_PRIMARY)
tb1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.paragraphs[0].text = "Firmware & Cloud Core"
tf1.paragraphs[0].font.size = Pt(19)
tf1.paragraphs[0].font.bold = True
tf1.paragraphs[0].font.color.rgb = CYAN_PRIMARY

for task, desc, st in t_list1:
    p = tf1.add_paragraph()
    p.text = f"{st} {task} — {desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(4)

add_card(s7, 6.8, 2.1, 5.7, 4.8, border_color=AMBER_GOLD)
tb2 = s7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf2 = tb2.text_frame
tf2.word_wrap = True
tf2.paragraphs[0].text = "Hardware, Voice & Applications"
tf2.paragraphs[0].font.size = Pt(19)
tf2.paragraphs[0].font.bold = True
tf2.paragraphs[0].font.color.rgb = AMBER_GOLD

for task, desc, st in t_list2:
    p = tf2.add_paragraph()
    p.text = f"{st} {task} — {desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(4)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8: 17 Bugs Fixed (Security, Memory & Power)
# ══════════════════════════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s8)
add_header(s8, "Quality Engineering", "17 Vulnerabilities & Bugs Resolved", "Transformed a prototype into a secure, hardened commercial-grade product.")

bug_cards = [
    ("4 Critical Bugs", "SECURITY & CRASHES", [
        "Public Database Rules: Anyone could flip relays without password. FIXED.",
        "Exposed Firebase API Keys in open repo. FIXED with .env.",
        "ESP32 Brownout Crashes when all 4 relays triggered simultaneously. FIXED with staggered 50ms startup.",
        "Silent Wi-Fi disconnect lockups. FIXED with non-blocking reconnect."
    ], CRIMSON_RED),
    ("5 High Priority Bugs", "PERFORMANCE & RELIABILITY", [
        "2-second polling spam. FIXED with WebSocket event stream.",
        "Firebase Token 1-hour expiry lockout. FIXED with auto-refresh.",
        "Zero hardware watchdog. FIXED with 15-second WDT timer.",
        "Missing SSL Root CA verification. FIXED with modern TLS validation.",
        "Blocking while waiting for Wi-Fi. FIXED with async FreeRTOS task."
    ], AMBER_GOLD),
    ("8 Medium & Low Bugs", "USABILITY & HARDWARE", [
        "Loss of relay status during power cuts. FIXED with NVS flash memory.",
        "Physical wall switch out-of-sync. FIXED with GPIO interrupt feedback.",
        "Relay contact welding from AC motor spark. FIXED with RC snubber.",
        "Missing over-the-air firmware update. FIXED with ElegantOTA."
    ], EMERALD_GREEN)
]

for idx, (title, tag, bugs, col) in enumerate(bug_cards):
    x = 0.8 + idx * 3.95
    add_card(s8, x, 2.1, 3.75, 4.8, border_color=col)
    tb = s8.shapes.add_textbox(Inches(x + 0.2), Inches(2.3), Inches(3.35), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p2 = tf.add_paragraph()
    p2.text = tag
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = col
    p2.space_before = Pt(4)
    p2.space_after = Pt(8)
    
    for b in bugs:
        bp = tf.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(13)
        bp.font.color.rgb = TEXT_BODY
        bp.space_before = Pt(6)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9: Self-Healing Armor (Layman Explanations)
# ══════════════════════════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s9)
add_header(s9, "Built-In Protection", "Self-Healing Armor (Layman Explanations)", "How ApnaGhar keeps running year after year without human maintenance.")

shields = [
    ("Watchdog Timer (WDT)", "Automatic Chip Doctor",
     "What it is: A 15-second countdown timer inside the chip.",
     "Layman Analogy: If the microcontroller ever freezes due to electrical noise, the timer reaches zero and automatically revives the chip in 15 seconds. You never need to unplug it.",
     CYAN_PRIMARY),
    ("NVS Flash Memory", "Blackout Memory",
     "What it is: On-chip non-volatile storage flash memory.",
     "Layman Analogy: Remembers whether your fan was ON or OFF right before a blackout. When main power returns, it restores your exact comfort level automatically.",
     AMBER_GOLD),
    ("RC Snubber + MOV", "Appliance Bodyguard",
     "What it is: Resistor-Capacitor filter plus Metal Oxide Varistor.",
     "Layman Analogy: When an AC compressor or motor shuts off, it kicks back a violent 600V spark. The snubber absorbs this surge like a shock absorber so your relays never burn out.",
     PURPLE_ROYAL)
]

for idx, (title, tag, what, analogy, col) in enumerate(shields):
    x = 0.8 + idx * 3.95
    add_card(s9, x, 2.1, 3.75, 4.8, border_color=col)
    tb = s9.shapes.add_textbox(Inches(x + 0.25), Inches(2.35), Inches(3.25), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    pt = tf.add_paragraph()
    pt.text = f"🛡️ {tag}"
    pt.font.size = Pt(15)
    pt.font.bold = True
    pt.font.color.rgb = col
    pt.space_before = Pt(4)
    
    pw = tf.add_paragraph()
    pw.text = what
    pw.font.size = Pt(14)
    pw.font.color.rgb = TEXT_MUTED
    pw.space_before = Pt(8)
    
    pa = tf.add_paragraph()
    pa.text = analogy
    pa.font.size = Pt(14)
    pa.font.color.rgb = TEXT_BODY
    pa.space_before = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10: Energy Metering: Real Hardware vs Guesswork
# ══════════════════════════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s10)
add_header(s10, "Smart Metering", "PZEM-004T: True Electricity Measurement", "Real electrical metering versus naive software guess work.")

add_card(s10, 0.8, 2.1, 5.6, 4.8, border_color=CRIMSON_RED)
tb_e = s10.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_e = tb_e.text_frame
tf_e.word_wrap = True
tf_e.paragraphs[0].text = "❌ Naive Software Guessing"
tf_e.paragraphs[0].font.size = Pt(20)
tf_e.paragraphs[0].font.bold = True
tf_e.paragraphs[0].font.color.rgb = CRIMSON_RED

pts_guess = [
    "Multiplies 60W x Hours: Assumes every bulb uses exactly 60W forever.",
    "Ignores Voltage Drops: When grid drops to 180V or surges to 260V, calculations fail.",
    "Blind to Inductive Loads: Fans and refrigerators have power factors (cos φ) that software estimates completely distort.",
    "Result: Inaccurate and misleading electricity bill calculations."
]
for pg in pts_guess:
    p = tf_e.add_paragraph()
    p.text = f"• {pg}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

add_card(s10, 6.8, 2.1, 5.7, 4.8, border_color=EMERALD_GREEN)
tb_m = s10.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_m = tb_m.text_frame
tf_m.word_wrap = True
tf_m.paragraphs[0].text = "✅ PZEM-004T Hardware Meter"
tf_m.paragraphs[0].font.size = Pt(20)
tf_m.paragraphs[0].font.bold = True
tf_m.paragraphs[0].font.color.rgb = EMERALD_GREEN

pts_real = [
    "Dedicated High-Precision Energy Chip: Reads true RMS AC voltage (80-260V).",
    "Current Transformer (CT) Coil: Non-invasive current sensing up to 100 Amperes.",
    "Active Power & Energy Accumulation: Real kWh stored directly inside hardware memory.",
    "Frequency & Power Factor: Detects appliance degradation before it breaks.",
    "Layman: Exactly like the government electricity meter outside your home!"
]
for pr in pts_real:
    p = tf_m.add_paragraph()
    p.text = f"• {pr}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11: Industrial 3D Enclosure & PCB with Real Image
# ══════════════════════════════════════════════════════════════════════════════
s11 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s11)
add_header(s11, "Industrial Design", "Custom 2-Layer PCB & 3D Printed Box", "Engineered to international electrical creepage and flame-retardant standards.")

# Left 3D Exploded View Image
if os.path.exists(IMG_ENCLOSURE):
    add_card(s11, 0.8, 2.1, 5.8, 4.8, border_color=PURPLE_ROYAL)
    s11.shapes.add_picture(IMG_ENCLOSURE, Inches(0.9), Inches(2.2), width=Inches(5.6), height=Inches(4.6))

# Right: Specifications
add_card(s11, 6.9, 2.1, 5.6, 4.8, border_color=CYAN_PRIMARY)
tb_enc = s11.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.2), Inches(4.4))
tf_enc = tb_enc.text_frame
tf_enc.word_wrap = True

tf_enc.paragraphs[0].text = "Hardware Manufacturing Features"
tf_enc.paragraphs[0].font.size = Pt(21)
tf_enc.paragraphs[0].font.bold = True
tf_enc.paragraphs[0].font.color.rgb = TEXT_MAIN

enc_specs = [
    ("Creepage Isolation Slots:", "Physical milling cuts through the fiberglass board to stop 230V electricity from jumping to 3.3V logic."),
    ("2oz Heavy Copper:", "Thick copper traces handle 10A per relay without heating up."),
    ("Parametric 3D Box:", "OpenSCAD parametric CAD model ('enclosure.scad') ready for 3D printing."),
    ("UL94 V-0 Flame Retardant:", "Designed for self-extinguishing ABS/PETG housing."),
    ("DIN-Rail Clip:", "Snaps directly into standard electrical distribution breaker boards.")
]

for title, desc in enc_specs:
    p = tf_enc.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12: Voice Skills: Alexa & Google Home
# ══════════════════════════════════════════════════════════════════════════════
s12 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s12)
add_header(s12, "Voice Assistants", "Hands-Free Voice Control Ecosystem", "Turn on lights and appliances naturally using Alexa or Google Assistant.")

add_card(s12, 0.8, 2.1, 5.6, 4.8, border_color=CYAN_PRIMARY)
tb_al = s12.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_al = tb_al.text_frame
tf_al.word_wrap = True
tf_al.paragraphs[0].text = "🗣️ Amazon Alexa Skill"
tf_al.paragraphs[0].font.size = Pt(21)
tf_al.paragraphs[0].font.bold = True
tf_al.paragraphs[0].font.color.rgb = CYAN_PRIMARY

alexa_pts = [
    "Skill Endpoint: Node.js Lambda function configured for Alexa Smart Home API v3.",
    "Voice Commands Supported:",
    "  • 'Alexa, turn on Living Room Light'",
    "  • 'Alexa, turn off Bedroom Fan'",
    "  • 'Alexa, is the Kitchen Light ON?'",
    "Direct Firebase Token Linking: Secure, zero-delay voice bridge."
]
for ap in alexa_pts:
    p = tf_al.add_paragraph()
    p.text = ap
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

add_card(s12, 6.8, 2.1, 5.7, 4.8, border_color=AMBER_GOLD)
tb_gg = s12.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_gg = tb_gg.text_frame
tf_gg.word_wrap = True
tf_gg.paragraphs[0].text = "🎙️ Google Assistant Action"
tf_gg.paragraphs[0].font.size = Pt(21)
tf_gg.paragraphs[0].font.bold = True
tf_gg.paragraphs[0].font.color.rgb = AMBER_GOLD

google_pts = [
    "Google Home Smart Home Action: Full support for SYNC, QUERY, and EXECUTE intents.",
    "Natural Voice Controls:",
    "  • 'Hey Google, turn on AC'",
    "  • 'Hey Google, turn off all room lights'",
    "Real-time Two-Way State Sync: Google Home app displays live button toggles immediately."
]
for gp in google_pts:
    p = tf_gg.add_paragraph()
    p.text = gp
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13: Mobile App & Web Dashboard with 3D UI Image
# ══════════════════════════════════════════════════════════════════════════════
s13 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s13)
add_header(s13, "Cross-Platform Apps", "Flutter Mobile App & Web Dashboard", "Modern responsive interface for iOS, Android, and Desktop browsers.")

# Left 3D Mobile/Tablet Image
if os.path.exists(IMG_APPS):
    add_card(s13, 0.8, 2.1, 5.8, 4.8, border_color=CYAN_PRIMARY)
    s13.shapes.add_picture(IMG_APPS, Inches(0.9), Inches(2.2), width=Inches(5.6), height=Inches(4.6))

# Right: Feature List
add_card(s13, 6.9, 2.1, 5.6, 4.8, border_color=CARD_BORDER)
tb_app = s13.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.2), Inches(4.4))
tf_app = tb_app.text_frame
tf_app.word_wrap = True

tf_app.paragraphs[0].text = "App & Dashboard Features"
tf_app.paragraphs[0].font.size = Pt(21)
tf_app.paragraphs[0].font.bold = True
tf_app.paragraphs[0].font.color.rgb = TEXT_MAIN

app_features = [
    ("Flutter Android App (54.6 MB):", "Smooth 60 FPS animations, signed release keystore, NDK 27 compilation."),
    ("Play Store Bundle (44.8 MB):", "Google Play Store .aab package ready for console upload."),
    ("Vercel Web Dashboard:", "Global CDN deployment with sub-100ms Firebase RTDB synchronization."),
    ("Accurate Online Status:", "Dynamic heartbeat monitoring shows exact hardware state (Online / Offline)."),
    ("One-Click Access:", "Instant test buttons for viva examiners and demonstration without password friction.")
]

for title, desc in app_features:
    p = tf_app.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14: Live Demo Links & High-Contrast QR Codes
# ══════════════════════════════════════════════════════════════════════════════
s14 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s14)
add_header(s14, "Live Demonstration", "Experience It Live: Scan QR Codes or Visit URLs", "Control appliances in real time with sub-100ms latency right now.")

# Card 1: Web Dashboard
add_card(s14, 0.8, 2.1, 5.6, 4.8, border_color=CYAN_PRIMARY)
tb_l1 = s14.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(3.2), Inches(4.3))
tf_l1 = tb_l1.text_frame
tf_l1.word_wrap = True
tf_l1.paragraphs[0].text = "🌐 Live Web Dashboard"
tf_l1.paragraphs[0].font.size = Pt(20)
tf_l1.paragraphs[0].font.bold = True
tf_l1.paragraphs[0].font.color.rgb = CYAN_PRIMARY

p = tf_l1.add_paragraph()
p.text = "Open in any mobile or desktop browser:"
p.font.size = Pt(14)
p.font.color.rgb = TEXT_MUTED
p.space_before = Pt(8)

p = tf_l1.add_paragraph()
p.text = LIVE_URL
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = TEXT_MAIN
p.space_before = Pt(6)

p = tf_l1.add_paragraph()
p.text = "👉 Scan the QR code to open the dashboard instantly!"
p.font.size = Pt(13)
p.font.color.rgb = AMBER_GOLD
p.space_before = Pt(12)

qr_web_buf = make_qr_image(LIVE_URL)
s14.shapes.add_picture(qr_web_buf, Inches(4.3), Inches(2.8), width=Inches(1.8), height=Inches(1.8))

# Card 2: GitHub Repository & APK
add_card(s14, 6.8, 2.1, 5.7, 4.8, border_color=AMBER_GOLD)
tb_l2 = s14.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(3.3), Inches(4.3))
tf_l2 = tb_l2.text_frame
tf_l2.word_wrap = True
tf_l2.paragraphs[0].text = "📦 GitHub & APK Release"
tf_l2.paragraphs[0].font.size = Pt(20)
tf_l2.paragraphs[0].font.bold = True
tf_l2.paragraphs[0].font.color.rgb = AMBER_GOLD

p = tf_l2.add_paragraph()
p.text = "Full source code, schematics & guides:"
p.font.size = Pt(14)
p.font.color.rgb = TEXT_MUTED
p.space_before = Pt(8)

p = tf_l2.add_paragraph()
p.text = GITHUB_URL
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = TEXT_MAIN
p.space_before = Pt(6)

p = tf_l2.add_paragraph()
p.text = "Local APK File: './ApnaGhar-v2.0-release.apk' (54.6 MB)"
p.font.size = Pt(13)
p.font.color.rgb = EMERALD_GREEN
p.space_before = Pt(12)

qr_gh_buf = make_qr_image(GITHUB_URL)
s14.shapes.add_picture(qr_gh_buf, Inches(10.4), Inches(2.8), width=Inches(1.8), height=Inches(1.8))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15: Conclusion & Viva Highlights
# ══════════════════════════════════════════════════════════════════════════════
s15 = prs.slides.add_slide(blank_layout)
set_canvas_bg(s15)
add_header(s15, "Project Summary", "Summary: Why ApnaGhar v2.0 Stands Out", "Bridges the gap between hobby DIY projects and commercial electrical standards.")

add_card(s15, 0.8, 2.1, 11.7, 4.8, border_color=CYAN_PRIMARY)
tb_c = s15.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(10.9), Inches(4.3))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

tf_c.paragraphs[0].text = "🏆 Key Takeaways & Viva Highlights"
tf_c.paragraphs[0].font.size = Pt(22)
tf_c.paragraphs[0].font.bold = True
tf_c.paragraphs[0].font.color.rgb = AMBER_GOLD

conclusions = [
    ("Real-Time Event Stream:", "Sub-100ms latency via Google Firebase RTDB replaces slow 2-second polling."),
    ("Zero Blackout Amnesia:", "NVS storage flash memory ensures appliances remember state after power restoration."),
    ("Self-Healing Firmware:", "Hardware Watchdog Timer automatically revives the ESP32 in 15 seconds if it ever hangs."),
    ("Electrical Armor:", "RC snubber circuit and MOV absorb dangerous inductive spikes from motors and air conditioners."),
    ("Triple-Mode Resilience:", "Functions via Cloud Firebase, Local Wi-Fi (offline), or Emergency ESP32 Access Point Hotspot.")
]

for title, desc in conclusions:
    p = tf_c.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_BODY
    p.space_before = Pt(8)

p_end = tf_c.add_paragraph()
p_end.text = "Thank You! Ready for Demonstration & Questions."
p_end.font.size = Pt(20)
p_end.font.bold = True
p_end.font.color.rgb = CYAN_PRIMARY
p_end.space_before = Pt(18)

# Save with fallback if locked by PowerPoint
saved_path = None
candidate_names = [
    "ApnaGhar_v2.0_Presentation.pptx",
    "ApnaGhar_v2.0_Executive_Presentation.pptx",
    "ApnaGhar_v2.0_Modern_Luxe.pptx"
]

for name in candidate_names:
    try:
        prs.save(name)
        saved_path = name
        print(f"Presentation successfully created: {name} ({os.path.getsize(name)} bytes)")
        break
    except Exception as e:
        print(f"Could not save to {name} (probably open in PowerPoint): {e}")

if saved_path:
    # Try copying to other names if possible
    import shutil
    for name in candidate_names:
        if name != saved_path:
            try:
                shutil.copyfile(saved_path, name)
                print(f"Also synced to {name}")
            except Exception as e:
                print(f"Could not sync to {name}: {e}")

