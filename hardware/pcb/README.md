# 🔌 Custom 2-Layer Smart Switch PCB Design (Task 7)

This directory contains the professional 2-layer hardware design files, schematic, bill of materials, layout rules, and manufacturing specifications for the **ApnaGhar 4-Channel ESP32 Smart Switch Controller**.

---

## 1. PCB Manufacturing Specifications

| Parameter | Specification | Industry Standard / Notes |
|:---|:---|:---|
| **Board Dimensions** | **100.0 mm $\times$ 80.0 mm** | Compact form factor fits inside standard 4-module concealed switchboards |
| **Layer Count** | **2 Layers** | Top: Signal routing & AC lines; Bottom: Solid DC GND plane |
| **Material / Base** | FR-4 Standard TG130–140 | Flame retardant, high insulation resistance |
| **Finished Copper Weight** | **2 oz ($70\mu\text{m}$)** | Mandatory for 10A continuous AC trace heating resistance |
| **Board Thickness** | 1.6 mm | Standard rigid mechanical stability |
| **Minimum Trace / Space** | 8 mil / 8 mil (DC) | Conservative manufacturing yield |
| **AC Trace Width** | **3.0 mm (120 mil) + Top/Bottom paralleling** | Rated for 10A continuous load at $\Delta T < 20^\circ\text{C}$ |
| **Isolation Creepage** | **$\ge 8.0\text{ mm}$ with physical isolation milling slots** | IEC 60950-1 & IEC 62368-1 electrical safety compliance |
| **Solder Mask** | Matte Dark Blue / Black | High-contrast visual inspection |
| **Silkscreen** | High-Definition White | Detailed pin names, ratings, and warnings |
| **Surface Finish** | HASL with Lead or ENIG (Electroless Nickel Immersion Gold) | Extended shelf-life and oxidation resistance |

---

## 2. Electrical Subsystems & Architecture

```
[ Mains 220V AC Input ]
       │
       ├──► [ 2A Fuse + 14D431K MOV ] ──► [ Hi-Link HLK-PM01 AC-DC ] ──► +5V DC Rail
       │                                                                      │
       │                                                                      ├──► [ AMS1117-3.3V LDO ] ──► +3.3V (ESP32)
       │                                                                      │
       │                                                                      └──► Relay Coils (JD-VCC)
       │
       └──► [ 4x Relays COM ] ──► [ Contacts NO + RC Snubber ] ──► [ 4x Load Terminals ]
                                           ▲
                                           │ (Optically Isolated)
                                    [ 4x EL817 Optocouplers ]
                                           ▲
                                           │
                             [ ESP32-WROOM-32E MCU ] ◄── [ 4x Manual Wall Switches ]
                                           ▲
                                           │
                                 [ PZEM-004T Header ]
```

---

## 3. High-Voltage Creepage & Safety Isolation Slot

To prevent electrical flashover under high humidity or atmospheric dust:
1. An **8.0mm physical air gap** separates all AC mains tracks (Live, Neutral, Load outputs) from the low-voltage DC microcontroller section.
2. A **2.0mm wide isolation routing slot (cutout)** is milled directly into the PCB substrate beneath the optical isolation barrier of the EL817 optocouplers.

---

## 4. Complete Bill of Materials (BOM)

| Ref Des | Component | Value / Footprint | Quantity | Description |
|:---|:---|:---|:---:|:---|
| **U1** | ESP32-WROOM-32E | Module (18x25.5mm) | 1 | 32-bit Dual-Core WiFi/BLE SoC |
| **U2** | HLK-PM01 | AC-DC 5V 1A Module | 1 | Regulated isolated power supply |
| **U3** | AMS1117-3.3 | SOT-223 | 1 | 3.3V 1A Low-Dropout Linear Regulator |
| **OK1-OK4**| EL817 | DIP-4 / SOP-4 | 4 | Optocoupler 5kV isolation |
| **K1-K4** | Songle SRD-05VDC-SL-C | SPDT Relay (19x15.5mm) | 4 | 5V Coil, 10A 250VAC Contacts |
| **Q1-Q4** | 2N2222 / S8050 | SOT-23 / TO-92 | 4 | NPN Relay Driver Transistors |
| **D1-D4** | 1N4007 | DO-41 / SMA | 4 | Coil Flyback Suppression Diodes |
| **MOV1** | 14D431K | Radial 14mm | 1 | 275VAC Transient Voltage Surge Varistor |
| **F1** | 5x20mm Glass Fuse + Holder | 2A 250V Slow-Blow | 1 | Primary AC Overcurrent Protection |
| **C_SNUB1-4**| Metallized Film Safety Cap | 100nF (0.1uF) 275VAC X2 | 4 | Inductive Arc Suppression Capacitor |
| **R_SNUB1-4**| Metal Oxide Resistor | 100 Ohm 2W Flameproof | 4 | Snubber Damping Resistor |
| **J_AC, J_LOAD**| Screw Terminal 5.08mm | 2-pin & 4-pin 300V 15A | 3 | Heavy-duty AC wiring terminals |
| **J_SWITCH**| Header 2.54mm | 5-pin Male Header | 1 | Manual Wall Switch inputs (GND, S1-S4) |
| **J_PZEM**| Header 2.54mm | 4-pin Male Header | 1 | PZEM-004T UART Interface (5V, GND, TX, RX) |

---

## 5. Directory Contents

- `README.md`: PCB specifications, layout guidelines, BOM (this file)
- `apnaghar_controller.kicad_sch`: KiCad 7/8 Schematic Source
- `apnaghar_controller.kicad_pcb`: KiCad 7/8 Board Layout Source
- `gerber.zip`: Complete RS-274X Gerber & Excellon Drill files ready for JLCPCB / PCBWay manufacturing.
