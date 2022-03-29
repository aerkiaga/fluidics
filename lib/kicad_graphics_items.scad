$fs = 0.01;

module draw_segment(
    start, // start point as 2-vector
    end, // end point as 2-vector
    width // width as number
) {
    vector = end - start;
    length = norm(vector);
    angle = atan2(vector[1], vector[0]);
    
    translate(start)
    rotate(angle) {
        translate([0, -width/2])
            square([length, width]);
        circle(d = width);
        translate([length, 0])
            circle(d = width);
    }
}

module draw_fp_line(
    start, // start point as 2-vector
    end, // end point as 2-vector
    width // width as number
) {
    draw_segment(
        start = start,
        end = end,
        width = width
    );
}

module draw_gr_poly(
    vertices, // list of vertices, as 2-vectors
    width, // stroke line width as number
    fill // whether to fill the shape, as boolean
) {
    for(i = [0 : len(vertices) - 2]) {
        draw_segment(
            start = vertices[i],
            end = vertices[i+1],
            width = width
        );
    }
    draw_segment(
        start = vertices[len(vertices) - 1],
        end = vertices[0],
        width = width
    );
    if(fill)
    polygon([
        for(v = vertices) v
    ]);
}

module draw_gr_rect(
    start, // start point as 2-vector
    end, // end point as 2-vector
    width, // stroke line width as number
    fill // whether to fill the shape, as boolean
) {
    draw_gr_poly(
        [
            start, [end.x, start.y],
            end, [start.x, end.y]
        ],
        width = width,
        fill = fill
    );
}

draw_fp_line([4, 5], [6, 7], 1);