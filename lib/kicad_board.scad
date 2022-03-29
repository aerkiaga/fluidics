epsilon = 0.01;

module board_assembly(
    invert = false, // render circuit, instead of negative board
    z_bounds // top and bottom z, as 2-vector
) {
    z_bounds = $preview ?
        [
            z_bounds[0] + epsilon,
            z_bounds[1] - epsilon
        ] :
        z_bounds
    ;
    height = abs(z_bounds[1] - z_bounds[0]);
    difference() {
        if(!invert)
        translate([0, 0, min(z_bounds)])
        linear_extrude(height)
            children(1);
        children(0);
    }
}