$fs = 0.01;

module draw_pad(
    pos, // center point as 2-vector
    diameter, // diameter of hole, as number
    z_bounds, // top and bottom z, as 2-vector
) {
    translate([pos.x, pos.y, min(z_bounds)])
    cylinder(
        abs(z_bounds[1] - z_bounds[0]),
        d = diameter,
        center = false
    );
}

draw_pad([4, 5], 0.4, [-2, 3]);