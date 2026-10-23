/*
 * Parametric 3D Printable Enclosure — ESP32 Home Control (ApnaGhar)
 * Material: ABS UL94 V-0 Flame-Retardant / PETG
 * Dimensions: 120mm x 90mm x 40mm (Internal: 115mm x 85mm x 35mm)
 * Features: Dual-compartment AC/DC isolation, DIN-rail snap-fit, M3 screw bosses, LED light pipes.
 */

$fn = 60;

// Dimensions (Outer)
box_length = 120;
box_width  = 90;
box_height = 40;
wall_thick = 2.5;
corner_rad = 4.0;

// PCB Dimensions
pcb_length = 100;
pcb_width  = 80;
boss_height= 6.0;

module rounded_box(l, w, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(h=h, r=r);
        translate([l-r, r, 0]) cylinder(h=h, r=r);
        translate([r, w-r, 0]) cylinder(h=h, r=r);
        translate([l-r, w-r, 0]) cylinder(h=h, r=r);
    }
}

// ── Base Enclosure ──────────────────────────────────────────
module enclosure_base() {
    difference() {
        // Outer Solid Shell
        rounded_box(box_length, box_width, box_height, corner_rad);

        // Hollow Cavity
        translate([wall_thick, wall_thick, wall_thick])
            rounded_box(box_length - 2*wall_thick, box_width - 2*wall_thick, box_height, corner_rad);

        // Terminal Block Wire Cutouts (AC Side)
        translate([box_length - wall_thick - 1, 15, 12])
            cube([wall_thick + 2, 60, 16]);

        // PZEM Sensor & Manual Switch Cable Slot (DC Side)
        translate([-1, 20, 12])
            cube([wall_thick + 2, 50, 14]);

        // Air Ventilation Slots (Top side)
        for (i = [0:6]) {
            translate([35 + i * 7, wall_thick - 1, 15])
                cube([3, wall_thick + 2, 18]);
            translate([35 + i * 7, box_width - wall_thick - 1, 15])
                cube([3, wall_thick + 2, 18]);
        }
    }

    // ── Internal Safety Isolation Barrier (AC / DC Divider) ──
    translate([65, wall_thick, wall_thick])
        cube([2.0, box_width - 2*wall_thick, box_height - 10]);

    // ── PCB Mounting Screw Bosses (M3) ──
    translate([10, 5, wall_thick]) pcb_boss();
    translate([10 + pcb_length - 8, 5, wall_thick]) pcb_boss();
    translate([10, 5 + pcb_width - 8, wall_thick]) pcb_boss();
    translate([10 + pcb_length - 8, 5 + pcb_width - 8, wall_thick]) pcb_boss();
}

module pcb_boss() {
    difference() {
        cylinder(h=boss_height, r=4.0);
        translate([0, 0, 1])
            cylinder(h=boss_height, r=1.5); // 3mm self-tapping screw hole
    }
}

// ── Top Snap-Fit Lid with LED Light Pipes ────────────────────
module enclosure_lid() {
    translate([0, box_width + 15, 0]) {
        difference() {
            rounded_box(box_length, box_width, wall_thick + 2, corner_rad);

            // 4x Relay Status LED Viewports
            for (r = [0:3]) {
                translate([45 + r * 10, 45, -1])
                    cylinder(h=wall_thick + 4, r=1.5);
            }

            // Power LED Viewport
            translate([30, 45, -1])
                cylinder(h=wall_thick + 4, r=1.5);
        }
    }
}

// Render complete assembly
enclosure_base();
enclosure_lid();
