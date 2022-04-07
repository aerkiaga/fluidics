use <../lib/kicad_graphics_items.scad>

// F.Cu
color("#ff8080")
translate([0, 0, 0.4])
linear_extrude(0.4)
difference() {
    translate([-5, 0, 0])
    square([10, 10]);
    draw_fp_line(
        start = [0.0, 0.0],
        end = [2.0, 0.0],
        width = 0.4
    );
    draw_fp_line(
        start = [2.0, 0.0],
        end = [2.0, 1.0],
        width = 0.4
    );
    draw_fp_line(
        start = [-2.0, 1.0],
        end = [-2.0, 7.0],
        width = 0.4
    );
    draw_fp_line(
        start = [-2.0, 7.0],
        end = [1.0, 7.0],
        width = 0.4
    );
}

// B.Cu
color("#8080ff")
translate([0, 0, -0.8])
linear_extrude(0.4)
difference() {
    translate([-5, 0, 0])
    square([10, 10]);
    draw_fp_line(
        start = [2.0, 0.0],
        end = [4.0, 0.0],
        width = 0.4
    );
}

// F.Mask
color("#80ff80")
translate([0, 0, 0.8])
linear_extrude(0.4)
difference() {
    translate([-1, 0, 0])
    square([6, 6]);
    draw_fp_line(
        start = [0.0, 0.0],
        end = [0.0, 0.0],
        width = 0.4
    );
    draw_fp_line(
        start = [2.0, 1.0],
        end = [2.0, 2.0],
        width = 0.8
    );
}

// B.Mask
color("#80ff80")
translate([0, 0, -1.2])
linear_extrude(0.4)
difference() {
    translate([-5, 0, 0])
    square([10, 10]);
    draw_fp_line(
        start = [4.0, 0.0],
        end = [4.0, 0.0],
        width = 0.4
    );
}

// Dielectric
color("#808080")
translate([0, 0, -0.4])
linear_extrude(0.8)
difference() {
    translate([-5, 0, 0])
    square([10, 10]);
    draw_fp_line(
        start = [2.0, 0.0],
        end = [2.0, 0.0],
        width = 0.4
    );
}