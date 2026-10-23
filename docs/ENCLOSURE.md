# 📦 Flame-Retardant 3D Enclosure Specification (Task 8)

This document provides mechanical dimensions, 3D printing parameters, material flammability compliance (UL94 V-0), and installation guidelines for the ApnaGhar smart switch enclosure.

---

## 1. Mechanical Dimensions & Compatibility

- **Outer Dimensions**: **120.0 mm (L) $\times$ 90.0 mm (W) $\times$ 40.0 mm (H)**
- **Wall Thickness**: **2.5 mm** heavy-duty perimeter wall
- **Internal PCB Clearance**: Fits $100\text{ mm} \times 80\text{ mm}$ ApnaGhar PCB on four M3 screw bosses
- **Switchboard Compatibility**: Specifically engineered to slide into standard domestic 4-module concealed wall metal backboxes, or mount on a standard 35mm DIN rail inside sub-distribution panels.

```
       120 mm
┌─────────────────────────┐ ───
│  DC Logic  │  AC Mains  │  │
│  [ESP32]   │  [Relays]  │ 90 mm
│  Low Volt  │  240V Load │  │
└─────────────────────────┘ ───
      │ 40 mm height
```

---

## 2. Dual-Compartment Safety Partition

> [!CRITICAL]
> **Internal Physical Isolation Barrier:**
> A molded 2.0mm thick solid partition wall divides the interior cavity into two distinct chambers:
> 1. **Low-Voltage DC Chamber**: Houses the ESP32 module, reset button, manual switch wiring, and PZEM TTL headers.
> 2. **High-Voltage AC Chamber**: Houses the HLK-PM01, 240V Live/Neutral inputs, fuse holder, varistor, and 4 relay output terminal blocks.
> This physical wall guarantees that a loose live AC wire cannot accidentally touch the low-voltage ESP32 pins.

---

## 3. Recommended 3D Printing Settings

| Parameter | Recommended Setting | Rationale |
|:---|:---|:---|
| **Material** | **ABS (UL94 V-0 Rated) or Flame-Retardant PETG** | Mandatory fire-retardant self-extinguishing safety |
| **Layer Height** | **0.20 mm** | Optimum interlayer adhesion and water-resistant finish |
| **Perimeters / Walls** | **4 Walls ($1.6\text{ mm}$ minimum)** | High mechanical rigidity against screw torque |
| **Infill Density** | **40% Gyroid or Honeycomb** | Superior crush and torsion resistance |
| **Nozzle Temperature** | $245^\circ\text{C} - 255^\circ\text{C}$ (ABS) | Maximum layer fusion |
| **Bed Temperature** | $100^\circ\text{C} - 110^\circ\text{C}$ with enclosure | Eliminates corner warping |
| **Cooling Fan** | 0% - 15% | Prevents delamination in ABS prints |

---

## 4. Assembly & Mounting Steps

1. **Tap Screw Bosses**:
   Pre-thread the four 3.0mm PCB mounting bosses using an M3 screw tap or thread-forming plastics screw.
2. **Mount PCB**:
   Insert the assembled ApnaGhar PCB into the base and secure using four $M3 \times 6\text{mm}$ pan-head screws.
3. **Route Wiring**:
   Feed AC mains Live/Neutral and 4 load wires through the high-voltage cable slot.
   Feed low-voltage manual switch wires through the DC cable slot.
4. **Fasten Lid**:
   Snap-fit the top lid onto the base shell. Secure corners using four $M3 \times 12\text{mm}$ counter-sunk screws.
5. **DIN-Rail Attachment**:
   Snap the integrated rear bracket onto standard 35mm EN 50022 DIN rails.
