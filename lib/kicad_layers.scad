use <./util.scad>

$fs = 0.01;

/* Get thickness of a layer by name */
function get_layer_thickness(layer, board_description) =
    lookup_dict(layer, board_description[0])
;

/* Get z-coordinate of a layer's back face */
function get_layer_back(layer, board_description) =
    is_num(layer) ? layer :
    !is_string(layer) ? undef :
    layer == "F.Mask" ? board_description[1]/2 + 
        get_layer_thickness("F.Cu", board_description) :
    layer == "F.Cu" ? board_description[1]/2 :
    layer == "B.Cu" ? -board_description[1]/2 - 
        get_layer_thickness("B.Cu", board_description) :
    layer == "B.Mask" ? -board_description[1]/2 - 
        get_layer_thickness("B.Cu", board_description) -
        get_layer_thickness("B.Mask", board_description) :
    undef
;

/* Get z-coordinate of a layer's front face */
function get_layer_front(layer, board_description) =
    is_num(layer) ? layer :
    !is_string(layer) ? undef :
    layer == "F.Mask" ? board_description[1]/2 + 
        get_layer_thickness("F.Mask", board_description) +
        get_layer_thickness("F.Cu", board_description) :
    layer == "F.Cu" ? board_description[1]/2 +
        get_layer_thickness("F.Cu", board_description) :
    layer == "B.Cu" ? -board_description[1]/2 :
    layer == "B.Mask" ? -board_description[1]/2 - 
        get_layer_thickness("B.Cu", board_description) :
    undef
;

/*
 * Get a [lower, higher] z-coordinate pair that
 * encompasses all the specified layers.
 */
function bounds_from_layers(layers, board_description) =
    [
        min([
            for(l = layers)
                get_layer_back(l, board_description)
        ]),
        max([
            for(l = layers)
                get_layer_front(l, board_description)
        ]),
    ]
;

module draw_layer(
    layer, // layer name, as canonical name on KiCAD
    board_description // board description, generated
) {
    thickness = get_layer_thickness(
        layer, board_description
    );
    pos3 = board_description[1] / 2 + thickness/2;
    pos2 = pos3 + (layer == "F.Mask" ?
        get_layer_thickness(
            "F.Cu", board_description
        ) : 0
    );
    pos1 = pos2 + (layer == "B.Mask" ?
        get_layer_thickness(
            "B.Cu", board_description
        ) : 0
    );
    pos = layer[0] == "B" ? -pos1 : pos1;
    translate([0, 0, pos - thickness/2])
    linear_extrude(thickness)
    children();
}