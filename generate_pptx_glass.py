"""
ApnaGhar v2.0 — Ultra-Premium Glassmorphism Presentation Generator
Theme: Cyber Frosted Glass (Midnight Deep Navy #0B0819, Electric Cyan #00E5FF, Radiant Marigold #F59E0B, Neon Violet #8B5CF6)
Features: Large high-contrast typography, layman language analogies, 3D visual card elements, QR codes.
"""

import io
import os
import qrcode
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_COLOR       = RGBColor(0x0A, 0x07, 0x1A) # Ultra-deep midnight
TEXT_WHITE     = RGBColor(0xFF, 0xFF, 0xFF) # High-contrast crisp white
TEXT_MUTED     = RGBColor(0xDF, 0xE4, 0xEA) # Light silver for body readability
CYAN_ACCENT    = RGBColor(0x00, 0xE5, 0xFF) # Electric cyan
GOLD_ACCENT    = RGBColor(0xF5, 0x9E, 0x0B) # Warm marigold gold
PURPLE_ACCENT  = RGBColor(0xA7, 0x8B, 0xFA) # Neon violet
GREEN_ACCENT   = RGBColor(0x10, 0xB9, 0x81) # Emerald online green
RED_COLOR      = RGBColor(0xEF, 0x44, 0x44) # Crimson alert red
CARD_BORDER    = RGBColor(0x3B, 0x2D, 0x6E) # Glowing glass border

LIVE_URL   = "https://web-mjdtvq623-ahmadsakib263-4202s-projects.vercel.app"
GITHUB_URL = "https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def create_glass_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_alpha=0.18):
    """Adds a frosted glass card shape with subtle glowing border."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0x15, 0x11, 0x2E) # Translucent glass illusion
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape

def add_header(slide, tag_text, title_text, subtitle_text=""):
    """Adds a standardized high-contrast executive header with 3D glowing pill."""
    # Tag Pill
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.45))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = f"[ ⚡ {tag_text.upper()} ]"
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = CYAN_ACCENT

    # Main Title (Large & Clear)
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(32)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    # Subtitle / Layman summary
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.5), Inches(0.55))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = GOLD_ACCENT

def make_qr_image(url):
    qr = qrcode.QRCode(box_size=6, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A071A", back_color="#00E5FF").convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: Title Slide (Hero Glassmorphism)
# ══════════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

create_glass_card(s1, 1.2, 1.0, 10.933, 5.5, border_color=CYAN_ACCENT)

# Badge
b1 = s1.shapes.add_textbox(Inches(1.8), Inches(1.5), Inches(9.5), Inches(0.5))
b1.text_frame.word_wrap = True
p = b1.text_frame.paragraphs[0]
p.text = "★ PRODUCTION-READY IoT SMART HOME ARCHITECTURE ★"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = GOLD_ACCENT

# Big Title
t1 = s1.shapes.add_textbox(Inches(1.8), Inches(2.0), Inches(9.5), Inches(1.2))
t1.text_frame.word_wrap = True
p = t1.text_frame.paragraphs[0]
p.text = "ApnaGhar v2.0"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# Subtitle
st1 = s1.shapes.add_textbox(Inches(1.8), Inches(3.1), Inches(9.5), Inches(0.8))
st1.text_frame.word_wrap = True
p = st1.text_frame.paragraphs[0]
p.text = "ESP32 Heavy-Duty Home Automation with Firebase Realtime Sync"
p.font.size = Pt(22)
p.font.color.rgb = CYAN_ACCENT

# Layman Hook
lh = s1.shapes.add_textbox(Inches(1.8), Inches(3.9), Inches(9.5), Inches(1.0))
lh.text_frame.word_wrap = True
p = lh.text_frame.paragraphs[0]
p.text = "In Simple Words: Control high-power home appliances (lights, fans, ACs) in 0.1 seconds from anywhere on Earth, with 100% safety and zero blackout amnesia."
p.font.size = Pt(17)
p.font.color.rgb = TEXT_MUTED

# Author & Date
foot = s1.shapes.add_textbox(Inches(1.8), Inches(5.3), Inches(9.5), Inches(0.6))
foot.text_frame.word_wrap = True
p = foot.text_frame.paragraphs[0]
p.text = "Lead Architect: Mohammad Sakib Ahmad  |  Status: Verified Production v2.0 Release  |  Year: 2026"
p.font.size = Pt(14)
p.font.color.rgb = PURPLE_ACCENT

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: The Problem (Why Traditional Switches & Cheap Smart Plugs Fail)
# ══════════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Real-World Context", "The Everyday Problem: Why Smart Homes Break", "Traditional wall switches are blind, and cheap IoT modules burn or crash.")

cards_data = [
    ("Traditional Switches", "🔥 Spark Hazard & No Remote Check", [
        "No way to check if geyser or iron was left ON after leaving home.",
        "Mechanical arcing damages expensive motors over time.",
        "Zero energy awareness — high electric bills with no explanation."
    ], CARD_BORDER),
    ("Cheap Smart Plugs", "❌ Hangs When Wi-Fi Drops", [
        "Cheap plugs freeze when internet drops, leaving you locked out.",
        "No wall switch feedback — family members get confused.",
        "Blackout amnesia — resets all switches randomly during power cuts."
    ], GOLD_ACCENT),
    ("Our Solution: ApnaGhar", "🛡️ Triple-Layer Self-Healing", [
        "Sub-100ms real-time control via Google Firebase Realtime Database.",
        "Surge-protected relay armor that handles heavy inductive AC loads.",
        "Family-friendly: Physical wall switches and phone app stay 100% in sync."
    ], CYAN_ACCENT)
]

for idx, (title, tag, points, border) in enumerate(cards_data):
    x = 0.8 + idx * 3.95
    create_glass_card(s2, x, 2.1, 3.75, 4.8, border_color=border)
    tb = s2.shapes.add_textbox(Inches(x + 0.2), Inches(2.3), Inches(3.35), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    p2 = tf.add_paragraph()
    p2.text = tag
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = border
    p2.space_before = Pt(6)
    p2.space_after = Pt(12)
    
    for pt in points:
        bp = tf.add_paragraph()
        bp.text = f"• {pt}"
        bp.font.size = Pt(15)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: The Triple-Mode Safety Architecture (Never Leaves You In The Dark)
# ══════════════════════════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Fail-Safe Design", "Triple-Mode Architecture: Always Reachable", "Even if your home Wi-Fi cable is snapped, your switches still work.")

modes = [
    ("MODE 1: Global Cloud", "Google Firebase WebSocket", "Works Everywhere",
     "Control lights, fans, and ACs from office, metro, or vacation in <0.1s latency.",
     "Layman: Like a live telephone line between your phone and your home.", CYAN_ACCENT),
    ("MODE 2: Local Wi-Fi (mDNS)", "Local Network Direct Sync", "Works Offline (No Internet)",
     "If broadband internet goes down, your phone still toggles appliances over home router.",
     "Layman: Phone talks straight to the ESP32 in your living room without cloud.", GOLD_ACCENT),
    ("MODE 3: Emergency AP", "Direct Hardware Hotspot", "Router Dead Fallback",
     "ESP32 broadcasts its own Wi-Fi hotspot ('SmartHome_Control') with captive portal.",
     "Layman: Connect your phone directly to the switch box to turn on lights.", PURPLE_ACCENT)
]

for idx, (title, tech, status, desc, layman, color) in enumerate(modes):
    x = 0.8 + idx * 3.95
    create_glass_card(s3, x, 2.1, 3.75, 4.8, border_color=color)
    tb = s3.shapes.add_textbox(Inches(x + 0.25), Inches(2.35), Inches(3.25), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    p_tech = tf.add_paragraph()
    p_tech.text = tech
    p_tech.font.size = Pt(14)
    p_tech.font.color.rgb = color
    p_tech.font.bold = True
    p_tech.space_before = Pt(4)
    
    p_stat = tf.add_paragraph()
    p_stat.text = f"[ Status: {status} ]"
    p_stat.font.size = Pt(13)
    p_stat.font.color.rgb = GREEN_ACCENT
    p_stat.space_before = Pt(8)
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(15)
    p_desc.font.color.rgb = TEXT_MUTED
    p_desc.space_before = Pt(12)
    
    p_lay = tf.add_paragraph()
    p_lay.text = f"💡 {layman}"
    p_lay.font.size = Pt(14)
    p_lay.font.italic = True
    p_lay.font.color.rgb = GOLD_ACCENT
    p_lay.space_before = Pt(14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: Complete System Architecture Flow
# ══════════════════════════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Engineering Pipeline", "End-to-End System Architecture", "How a tap on your phone turns on a heavy AC in 0.1 seconds.")

flow_steps = [
    ("1. User Inputs", "Flutter App\nWeb Dashboard\nAlexa / Google Voice", "User triggers toggle", CYAN_ACCENT),
    ("2. Cloud Engine", "Google Firebase RTDB\nWebSocket Stream\nFCM Push Alerts", "Instant state change", PURPLE_ACCENT),
    ("3. Microcontroller", "ESP32 DevKit V1\nHardware WDT (15s)\nNVS Power Memory", "Dual-core processor", GOLD_ACCENT),
    ("4. Power & Safety", "4x Heavy Duty Relays\nRC Snubber + MOV\nPZEM Energy Sensor", "Switches 230V AC loads", GREEN_ACCENT)
]

for idx, (title, details, desc, color) in enumerate(flow_steps):
    x = 0.8 + idx * 2.95
    create_glass_card(s4, x, 2.2, 2.75, 4.5, border_color=color)
    tb = s4.shapes.add_textbox(Inches(x + 0.2), Inches(2.4), Inches(2.35), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    p_det = tf.add_paragraph()
    p_det.text = details
    p_det.font.size = Pt(15)
    p_det.font.color.rgb = color
    p_det.space_before = Pt(10)
    
    p_desc = tf.add_paragraph()
    p_desc.text = f"Role: {desc}"
    p_desc.font.size = Pt(14)
    p_desc.font.color.rgb = TEXT_MUTED
    p_desc.space_before = Pt(14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: Hardware & Pin Configuration (The Physical Brain)
# ══════════════════════════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Circuit Wiring", "ESP32 Hardware Pin Allocation", "Safe pin assignment avoiding boot-loop and strapping conflicts.")

create_glass_card(s5, 0.8, 2.1, 6.8, 4.8, border_color=CYAN_ACCENT)
tb_pins = s5.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(6.4), Inches(4.3))
tf = tb_pins.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "Hardware Pin Mapping Table"
p.font.size = Pt(21)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

pins_info = [
    ("GPIO 23", "Relay 1 (Living Room Light)", "Active-LOW Optocoupler"),
    ("GPIO 22", "Relay 2 (Bedroom Light)", "Active-LOW Optocoupler"),
    ("GPIO 21", "Relay 3 (Kitchen Fan)", "Active-LOW Optocoupler"),
    ("GPIO 19", "Relay 4 (Air Conditioner / Heater)", "Active-LOW Optocoupler"),
    ("GPIO 16 / 17", "PZEM-004T Energy Meter", "UART2 Serial (RX/TX)"),
    ("GPIO 32, 33, 25, 26", "Manual Wall Switches", "Internal Pull-Up Interrupts")
]

for pin, app, note in pins_info:
    pp = tf.add_paragraph()
    pp.text = f"• {pin}: {app} [{note}]"
    pp.font.size = Pt(15)
    pp.font.color.rgb = TEXT_MUTED
    pp.space_before = Pt(6)

create_glass_card(s5, 7.9, 2.1, 4.6, 4.8, border_color=GOLD_ACCENT)
tb_expl = s5.shapes.add_textbox(Inches(8.1), Inches(2.3), Inches(4.2), Inches(4.3))
tf_e = tb_expl.text_frame
tf_e.word_wrap = True

p = tf_e.paragraphs[0]
p.text = "💡 Plain English Explanation"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = GOLD_ACCENT

layman_hardware = [
    "Optocoupler Isolation: High voltage 230V electricity is separated by a beam of light from the 3.3V chip. Zero risk of electric shock.",
    "No Boot Glitches: Boot strapping pins (GPIO 0, 2, 12, 15) were deliberately avoided so the ESP32 never gets stuck during power-up.",
    "Manual Sync: If an elderly family member presses the wall switch, the ESP32 senses it immediately and updates the phone screen."
]

for lh in layman_hardware:
    pp = tf_e.add_paragraph()
    pp.text = f"• {lh}"
    pp.font.size = Pt(15)
    pp.font.color.rgb = TEXT_WHITE
    pp.space_before = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: Firebase Realtime Database Engine
# ══════════════════════════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Cloud Engine", "Google Firebase Realtime Sync (<100ms)", "Why WebSocket event streaming crushes traditional HTTP polling.")

create_glass_card(s6, 0.8, 2.1, 5.6, 4.8, border_color=RED_COLOR)
tb_old = s6.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_old = tb_old.text_frame
tf_old.word_wrap = True

p = tf_old.paragraphs[0]
p.text = "❌ Old 2-Second Polling"
p.font.size = Pt(21)
p.font.bold = True
p.font.color.rgb = RGBColor(0xEF, 0x44, 0x44)

old_points = [
    "Device asked the server 'Anything new?' every 2 seconds in an endless loop.",
    "Wasted massive network bandwidth and overheated the Wi-Fi chip.",
    "Up to 2.5 second delay before a light would turn on.",
    "Exceeded free database quota quickly."
]
for op in old_points:
    pp = tf_old.add_paragraph()
    pp.text = f"• {op}"
    pp.font.size = Pt(15)
    pp.font.color.rgb = TEXT_MUTED
    pp.space_before = Pt(10)

create_glass_card(s6, 6.8, 2.1, 5.7, 4.8, border_color=GREEN_ACCENT)
tb_new = s6.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_new = tb_new.text_frame
tf_new.word_wrap = True

p = tf_new.paragraphs[0]
p.text = "✅ ApnaGhar v2.0 Event Streaming"
p.font.size = Pt(21)
p.font.bold = True
p.font.color.rgb = GREEN_ACCENT

new_points = [
    "Always-Open WebSocket Pipeline: Server pushes state only when a button is pressed.",
    "Lightning Fast: Response in under 100 milliseconds.",
    "95% Less Bandwidth: Zero unnecessary traffic when idle.",
    "Auto Token Refresh: Keeps connection alive 24/7 with zero logouts."
]
for np in new_points:
    pp = tf_new.add_paragraph()
    pp.text = f"• {np}"
    pp.font.size = Pt(15)
    pp.font.color.rgb = TEXT_WHITE
    pp.space_before = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: The 13 Tasks Completed Matrix
# ══════════════════════════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Delivery Status", "13 Core Features: All 100% Completed", "Production-grade implementation spanning firmware, cloud, mobile, and hardware.")

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

create_glass_card(s7, 0.8, 2.1, 5.7, 4.8, border_color=CYAN_ACCENT)
tb1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.paragraphs[0].text = "Firmware & Core Cloud"
tf1.paragraphs[0].font.size = Pt(18)
tf1.paragraphs[0].font.bold = True
tf1.paragraphs[0].font.color.rgb = CYAN_ACCENT

for task, desc, st in t_list1:
    p = tf1.add_paragraph()
    p.text = f"{st} {task} — {desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

create_glass_card(s7, 6.8, 2.1, 5.7, 4.8, border_color=GOLD_ACCENT)
tb2 = s7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf2 = tb2.text_frame
tf2.word_wrap = True
tf2.paragraphs[0].text = "Hardware, Voice & Applications"
tf2.paragraphs[0].font.size = Pt(18)
tf2.paragraphs[0].font.bold = True
tf2.paragraphs[0].font.color.rgb = GOLD_ACCENT

for task, desc, st in t_list2:
    p = tf2.add_paragraph()
    p.text = f"{st} {task} — {desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8: 17 Bugs Diagnosed & Defeated
# ══════════════════════════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Quality Engineering", "17 Vulnerabilities & Bugs Resolved", "Transformed a hobby prototype into a resilient, enterprise-grade system.")

bug_categories = [
    ("4 Critical Bugs", "SECURITY & CRASHES", [
        "Public Database Rules: Anyone could flip relays without password. FIXED.",
        "Exposed Firebase API Keys in open repo. FIXED with .env.",
        "ESP32 Brownout Crashes when all 4 relays triggered simultaneously. FIXED with staggered 50ms startup.",
        "Silent Wi-Fi disconnect lockups. FIXED with non-blocking reconnect."
    ], RGBColor(0xEF, 0x44, 0x44)),
    ("5 High Priority Bugs", "PERFORMANCE & RELIABILITY", [
        "2-second polling spam. FIXED with WebSocket event stream.",
        "Firebase Token 1-hour expiry lockout. FIXED with auto-refresh.",
        "Zero hardware watchdog. FIXED with 15-second WDT timer.",
        "Missing SSL Root CA verification. FIXED with modern TLS validation.",
        "Blocking while waiting for Wi-Fi. FIXED with async FreeRTOS task."
    ], GOLD_ACCENT),
    ("8 Medium & Low Bugs", "USABILITY & HARDWARE", [
        "Loss of relay status during power cuts. FIXED with NVS flash memory.",
        "Physical wall switch out-of-sync. FIXED with GPIO interrupt feedback.",
        "Relay contact welding from AC motor spark. FIXED with RC snubber.",
        "Missing over-the-air firmware update. FIXED with ElegantOTA."
    ], GREEN_ACCENT)
]

for idx, (title, tag, bugs, color) in enumerate(bug_categories):
    x = 0.8 + idx * 3.95
    create_glass_card(s8, x, 2.1, 3.75, 4.8, border_color=color)
    tb = s8.shapes.add_textbox(Inches(x + 0.2), Inches(2.3), Inches(3.35), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    p2 = tf.add_paragraph()
    p2.text = tag
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = color
    p2.space_before = Pt(4)
    p2.space_after = Pt(8)
    
    for b in bugs:
        bp = tf.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(13)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_before = Pt(6)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9: Self-Healing & Hardware Armor (In Layman Terms)
# ══════════════════════════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Built-In Protection", "Self-Healing Armor (Layman Explanations)", "How ApnaGhar keeps running year after year without human maintenance.")

shields = [
    ("Watchdog Timer (WDT)", "Automatic Chip Doctor",
     "What it is: A 15-second countdown timer inside the chip.",
     "Layman Analogy: If the microcontroller ever freezes due to electrical noise, the timer reaches zero and automatically slaps the chip awake in 15 seconds. You never need to unplug it.",
     CYAN_ACCENT),
    ("NVS Flash Memory", "Blackout Memory",
     "What it is: On-chip non-volatile storage flash memory.",
     "Layman Analogy: Remembers whether your fan was ON or OFF right before a blackout. When main power returns, it restores your exact comfort level automatically.",
     GOLD_ACCENT),
    ("RC Snubber + MOV", "Appliance Bodyguard",
     "What it is: Resistor-Capacitor filter plus Metal Oxide Varistor.",
     "Layman Analogy: When an AC compressor or motor shuts off, it kicks back a violent 600V spark. The snubber absorbs this surge like a shock absorber so your relays never burn out.",
     PURPLE_ACCENT)
]

for idx, (title, tag, what, analogy, col) in enumerate(shields):
    x = 0.8 + idx * 3.95
    create_glass_card(s9, x, 2.1, 3.75, 4.8, border_color=col)
    tb = s9.shapes.add_textbox(Inches(x + 0.25), Inches(2.35), Inches(3.25), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
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
    pa.font.color.rgb = TEXT_WHITE
    pa.space_before = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10: Energy Metering: Real vs Estimated Power
# ══════════════════════════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Smart Metering", "PZEM-004T: True Electricity Measurement", "Real electrical metering versus naive software guess work.")

create_glass_card(s10, 0.8, 2.1, 5.6, 4.8, border_color=RGBColor(0xEF, 0x44, 0x44))
tb_e = s10.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_e = tb_e.text_frame
tf_e.word_wrap = True
tf_e.paragraphs[0].text = "❌ Naive Software Guessing"
tf_e.paragraphs[0].font.size = Pt(20)
tf_e.paragraphs[0].font.bold = True
tf_e.paragraphs[0].font.color.rgb = RGBColor(0xEF, 0x44, 0x44)

points_guess = [
    "Multiplies 60W x Hours: Assumes every bulb uses exactly 60W forever.",
    "Ignores Voltage Fluctuations: When grid voltage drops to 180V or surges to 260V, calculations are wildly inaccurate.",
    "Blind to Inductive Loads: Fans and refrigerators have power factors (cos φ) that software estimates completely distort.",
    "Result: Completely wrong electricity bill predictions."
]
for pg in points_guess:
    p = tf_e.add_paragraph()
    p.text = f"• {pg}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(8)

create_glass_card(s10, 6.8, 2.1, 5.7, 4.8, border_color=GREEN_ACCENT)
tb_m = s10.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_m = tb_m.text_frame
tf_m.word_wrap = True
tf_m.paragraphs[0].text = "✅ PZEM-004T Hardware Meter"
tf_m.paragraphs[0].font.size = Pt(20)
tf_m.paragraphs[0].font.bold = True
tf_m.paragraphs[0].font.color.rgb = GREEN_ACCENT

points_real = [
    "Dedicated High-Precision Energy Chip: Reads true RMS AC voltage (80-260V).",
    "Current Transformer (CT) Coil: Non-invasive current sensing up to 100 Amperes.",
    "Active Power & Energy Accumulation: Real kWh stored directly inside hardware memory.",
    "Frequency & Power Factor: Detects faulty appliances before they break.",
    "Layman: Exactly like the government electricity meter outside your home!"
]
for pr in points_real:
    p = tf_m.add_paragraph()
    p.text = f"• {pr}"
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11: Voice Control: Alexa Skill & Google Assistant
# ══════════════════════════════════════════════════════════════════════════════
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Hands-Free Living", "Voice Assistant Integration", "Natural voice control via Amazon Alexa & Google Smart Home Action.")

create_glass_card(s11, 0.8, 2.1, 5.6, 4.8, border_color=CYAN_ACCENT)
tb_al = s11.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_al = tb_al.text_frame
tf_al.word_wrap = True
tf_al.paragraphs[0].text = "🗣️ Amazon Alexa Skill"
tf_al.paragraphs[0].font.size = Pt(21)
tf_al.paragraphs[0].font.bold = True
tf_al.paragraphs[0].font.color.rgb = CYAN_ACCENT

alexa_pts = [
    "Skill Endpoint: Node.js Lambda function configured for Alexa Smart Home Skill API v3.",
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
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(8)

create_glass_card(s11, 6.8, 2.1, 5.7, 4.8, border_color=GOLD_ACCENT)
tb_gg = s11.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_gg = tb_gg.text_frame
tf_gg.word_wrap = True
tf_gg.paragraphs[0].text = "🎙️ Google Assistant Action"
tf_gg.paragraphs[0].font.size = Pt(21)
tf_gg.paragraphs[0].font.bold = True
tf_gg.paragraphs[0].font.color.rgb = GOLD_ACCENT

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
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12: Custom 2-Layer PCB & 3D Printed Flame-Retardant Box
# ══════════════════════════════════════════════════════════════════════════════
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Hardware Engineering", "Custom PCB & 3D Printable Enclosure", "Engineered to international electrical safety isolation standards.")

create_glass_card(s12, 0.8, 2.1, 5.6, 4.8, border_color=PURPLE_ACCENT)
tb_pcb = s12.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_pcb = tb_pcb.text_frame
tf_pcb.word_wrap = True
tf_pcb.paragraphs[0].text = "📐 Custom 2-Layer PCB"
tf_pcb.paragraphs[0].font.size = Pt(21)
tf_pcb.paragraphs[0].font.bold = True
tf_pcb.paragraphs[0].font.color.rgb = PURPLE_ACCENT

pcb_points = [
    "Dimensions: Compact 100mm x 80mm FR4 double-sided circuit board.",
    "Creepage Air Isolation Slots: Physical milling cuts between 230V AC lines and 3.3V DC tracks.",
    "Thick Copper Pour: 2oz copper traces capable of handling 10A per relay without heating.",
    "Layman: Physical safety barriers so 230V never touches sensitive electronics."
]
for pp in pcb_points:
    p = tf_pcb.add_paragraph()
    p.text = f"• {pp}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(8)

create_glass_card(s12, 6.8, 2.1, 5.7, 4.8, border_color=CYAN_ACCENT)
tb_enc = s12.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_enc = tb_enc.text_frame
tf_enc.word_wrap = True
tf_enc.paragraphs[0].text = "🖨️ 3D Enclosure (OpenSCAD)"
tf_enc.paragraphs[0].font.size = Pt(21)
tf_enc.paragraphs[0].font.bold = True
tf_enc.paragraphs[0].font.color.rgb = CYAN_ACCENT

enc_points = [
    "Parametric CAD Model: Designed in OpenSCAD ('hardware/enclosure/enclosure.scad').",
    "Flame Retardant Material: Designed for 3D printing in UL94 V-0 ABS or heat-resistant PETG.",
    "Internal Barrier Wall: Completely separates high-voltage wire terminals from logic board.",
    "DIN-Rail & Screw Mounts: Easy installation in standard home breaker panels."
]
for ep in enc_points:
    p = tf_enc.add_paragraph()
    p.text = f"• {ep}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13: Mobile App & Web Dashboard
# ══════════════════════════════════════════════════════════════════════════════
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "User Experience", "Flutter Mobile App & Web Dashboard", "Modern cyber-glass interface built for both phone and desktop.")

create_glass_card(s13, 0.8, 2.1, 5.6, 4.8, border_color=GOLD_ACCENT)
tb_app = s13.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.3))
tf_app = tb_app.text_frame
tf_app.word_wrap = True
tf_app.paragraphs[0].text = "📱 ApnaGhar Android App"
tf_app.paragraphs[0].font.size = Pt(21)
tf_app.paragraphs[0].font.bold = True
tf_app.paragraphs[0].font.color.rgb = GOLD_ACCENT

app_pts = [
    "Built with Flutter: Smooth 60 FPS animations on all Android devices.",
    "Signed Release APK (54.6 MB): Ready for immediate sideloading.",
    "Google Play Store AAB (44.8 MB): Pre-configured for Play Store release.",
    "1-Click Instant Connect: Pre-mapped for instant testing without typing credentials.",
    "Periodic Auto-Sync: Updates automatically when physical wall switch flips."
]
for ap in app_pts:
    p = tf_app.add_paragraph()
    p.text = f"• {ap}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(8)

create_glass_card(s13, 6.8, 2.1, 5.7, 4.8, border_color=CYAN_ACCENT)
tb_web = s13.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.3))
tf_web = tb_web.text_frame
tf_web.word_wrap = True
tf_web.paragraphs[0].text = "🌐 Live Web Dashboard"
tf_web.paragraphs[0].font.size = Pt(21)
tf_web.paragraphs[0].font.bold = True
tf_web.paragraphs[0].font.color.rgb = CYAN_ACCENT

web_pts = [
    "Deployed on Vercel CDN: Ultra-fast globally distributed web hosting.",
    "Realtime Firebase Bridge: Directly sends commands to device in <100ms.",
    "One-Click Access: Instant control dashboard button for examiners.",
    "Live Indicator Dot: Real-time green/red pulse showing if ESP32 is online."
]
for wp in web_pts:
    p = tf_web.add_paragraph()
    p.text = f"• {wp}"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14: Live Demo, Links & QR Codes
# ══════════════════════════════════════════════════════════════════════════════
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "Live Demonstration", "Try It Live: Scan QR Codes or Visit URLs", "Experience real-time sub-100ms relay control right now.")

# Card 1: Web Dashboard
create_glass_card(s14, 0.8, 2.1, 5.6, 4.8, border_color=CYAN_ACCENT)
tb_l1 = s14.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(3.2), Inches(4.3))
tf_l1 = tb_l1.text_frame
tf_l1.word_wrap = True
tf_l1.paragraphs[0].text = "🌐 Live Web Dashboard"
tf_l1.paragraphs[0].font.size = Pt(20)
tf_l1.paragraphs[0].font.bold = True
tf_l1.paragraphs[0].font.color.rgb = CYAN_ACCENT

p = tf_l1.add_paragraph()
p.text = "Open on any phone or laptop browser:"
p.font.size = Pt(14)
p.font.color.rgb = TEXT_MUTED
p.space_before = Pt(8)

p = tf_l1.add_paragraph()
p.text = LIVE_URL
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE
p.space_before = Pt(6)

p = tf_l1.add_paragraph()
p.text = "👉 Scan QR code to open directly without typing!"
p.font.size = Pt(13)
p.font.color.rgb = GOLD_ACCENT
p.space_before = Pt(12)

# Add Web QR
qr_web_buf = make_qr_image(LIVE_URL)
s14.shapes.add_picture(qr_web_buf, Inches(4.3), Inches(2.8), width=Inches(1.8), height=Inches(1.8))

# Card 2: GitHub Repository & APK
create_glass_card(s14, 6.8, 2.1, 5.7, 4.8, border_color=GOLD_ACCENT)
tb_l2 = s14.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(3.3), Inches(4.3))
tf_l2 = tb_l2.text_frame
tf_l2.word_wrap = True
tf_l2.paragraphs[0].text = "📦 GitHub & APK Release"
tf_l2.paragraphs[0].font.size = Pt(20)
tf_l2.paragraphs[0].font.bold = True
tf_l2.paragraphs[0].font.color.rgb = GOLD_ACCENT

p = tf_l2.add_paragraph()
p.text = "Full source code, schematics & guides:"
p.font.size = Pt(14)
p.font.color.rgb = TEXT_MUTED
p.space_before = Pt(8)

p = tf_l2.add_paragraph()
p.text = GITHUB_URL
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE
p.space_before = Pt(6)

p = tf_l2.add_paragraph()
p.text = "Local APK File: './ApnaGhar-v2.0-release.apk' (54.6 MB)"
p.font.size = Pt(13)
p.font.color.rgb = GREEN_ACCENT
p.space_before = Pt(12)

# Add GitHub QR
qr_gh_buf = make_qr_image(GITHUB_URL)
s14.shapes.add_picture(qr_gh_buf, Inches(10.4), Inches(2.8), width=Inches(1.8), height=Inches(1.8))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15: Conclusion & Future Roadmap
# ══════════════════════════════════════════════════════════════════════════════
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "Project Summary", "Summary: Why ApnaGhar v2.0 Stands Out", "The gap between DIY hobby projects and commercial-grade automation is bridged.")

create_glass_card(s15, 0.8, 2.1, 11.7, 4.8, border_color=CYAN_ACCENT)
tb_c = s15.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(10.9), Inches(4.3))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

tf_c.paragraphs[0].text = "🏆 Key Takeaways & Viva Highlights"
tf_c.paragraphs[0].font.size = Pt(22)
tf_c.paragraphs[0].font.bold = True
tf_c.paragraphs[0].font.color.rgb = GOLD_ACCENT

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
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

p_end = tf_c.add_paragraph()
p_end.text = "Thank You! Ready for Demonstration & Questions."
p_end.font.size = Pt(20)
p_end.font.bold = True
p_end.font.color.rgb = CYAN_ACCENT
p_end.space_before = Pt(18)

# Save
output_filename = "ApnaGhar_v2.0_Executive_Presentation.pptx"
prs.save(output_filename)
print(f"Presentation successfully created: {output_filename} ({os.path.getsize(output_filename)} bytes)")

# Also try to update the main file name if not locked by PowerPoint
try:
    import shutil
    shutil.copyfile(output_filename, "ApnaGhar_v2.0_Presentation.pptx")
    print("Also updated ApnaGhar_v2.0_Presentation.pptx")
except Exception as e:
    print(f"Note: ApnaGhar_v2.0_Presentation.pptx is open in PowerPoint ({e}). Saved as {output_filename}")

