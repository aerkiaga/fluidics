#!/usr/bin/env python3

import fnmatch
import math
import os
import sexpdata
import shutil
import sys

script_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.join(script_path, "lib")

project_path = os.path.realpath(sys.argv[1])
pcb_path = os.path.join(project_path, "{}.kicad_pcb".format(os.path.basename(project_path)))
scad_path = os.path.join(project_path, "{}.scad".format(os.path.basename(project_path)))
project_lib_path = os.path.join(project_path, "scad")

required_libraries = set()
dependencies = set()
layer_graphics_items = {}
library_footprints = []
circuit_pads = []

def get_symbol(parent, name):
    try:
        return next(x for x in parent if type(x) == list and x[0] == sexpdata.Symbol(name))
    except StopIteration:
        return None

def get_number(parent):
    try:
        return next(x for x in parent if type(x) == int or type(x) == float)
    except StopIteration:
        return None

def apply_pos(pos1, pos2):
    if len(pos2) >= 3:
        angle_rad = math.radians(pos2[2])
        pos1_tmp = (
            math.cos(angle_rad)*pos1[0] - math.sin(angle_rad)*pos1[1],
            math.sin(angle_rad)*pos1[0] + math.cos(angle_rad)*pos1[1]
        )
        if len(pos1) >= 3:
            pos1 = (pos1_tmp[0], pos1_tmp[1], pos1_tmp[2] + pos2[2])
        else:
            pos1 = (pos1_tmp[0], pos1_tmp[1])
    if len(pos1) >= 3:
        return (pos1[0] + pos2[0], pos1[1] + pos2[1], pos1[2])
    else:
        return (pos1[0] + pos2[0], pos1[1] + pos2[1])

def parse_pos(pos):
    angle = 0
    if len(pos) >= 4:
        angle = pos[3]
    return (pos[1], pos[2], angle)

def element_is_graphics_item(element):
    if type(element) != list:
        return False
    for name in [
        "segment",
        "fp_line",
        "gr_rect"
    ]:
        if element[0] == sexpdata.Symbol(name):
            return True
    return False

def convert_graphics_item(element):
    global layer_graphics_items, required_libraries

    layer = get_symbol(element, "layer")[1]
    if layer not in layer_graphics_items:
        layer_graphics_items[layer] = []
    layer_graphics_items[layer].append(element)
    required_libraries.add("kicad_graphics_items")
    required_libraries.add("kicad_layers")

def convert_pad(element):
    global required_libraries

    circuit_pads.append(element)
    required_libraries.add("kicad_pads")
    required_libraries.add("kicad_layers")

def convert_library_footprint(footprint, path):
    global library_footprints

    pos = parse_pos(get_symbol(footprint, "at"))
    layers = set()
    for element in footprint:
        if element_is_graphics_item(element):
            layer = get_symbol(element, "layer")[1]
            layers.add(layer)
    layers_data = [sexpdata.Symbol("layers")]
    layers_data.extend(layers)
    footprint.append(layers_data)
    footprint.append([sexpdata.Symbol("scad_path"), path])
    library_footprints.append(footprint)
    dependency = os.path.relpath(os.path.splitext(path)[0], start = lib_path)
    required_libraries.add(dependency)

def convert_regular_footprint(footprint):
    pos = parse_pos(get_symbol(footprint, "at"))

    def apply_relative(element, name):
        var = get_symbol(element, name)
        if var:
            (var[1], var[2]) = apply_pos((var[1], var[2]), pos)

    for element in footprint:
        if type(element) != list:
            continue
        apply_relative(element, "at")
        apply_relative(element, "start")
        apply_relative(element, "end")
        if element_is_graphics_item(element):
            convert_graphics_item(element)
        elif element[0] == sexpdata.Symbol("pad"):
            convert_pad(element)

def convert_footprint(footprint):
    name = footprint[1].split(":", 1)
    footprint_path = os.path.join(lib_path, name[0], "{}.scad".format(name[1]))
    if os.path.isfile(footprint_path):
        convert_library_footprint(footprint, footprint_path)
    else:
        convert_regular_footprint(footprint)

with open(pcb_path, "rt") as file:
    global layer_definitions
    pcb = sexpdata.load(file)
    for element in pcb:
        if type(element) == list:
            if element[0] == sexpdata.Symbol("layers"):
                layer_definitions = element
            elif element[0] == sexpdata.Symbol("footprint"):
                convert_footprint(element)
            elif element_is_graphics_item(element):
                convert_graphics_item(element)
            elif element[0] == sexpdata.Symbol("pad"):
                convert_pad(element)

required_libraries.add("kicad_board")
required_libraries.add("kicad_layers")

##################################################################################################

pos_to_layers = {}
extents = ((1e+10, 1e+10), (-1e+10, -1e+10))

for (layer, items) in layer_graphics_items.items():
    for item in items:
        values = []
        start = get_symbol(item, "start")
        if start:
            values.append(parse_pos(start))
        end = get_symbol(item, "end")
        if end:
            values.append(parse_pos(end))
        for value in values:
            val = tuple(map(lambda x: round(x, 2), value[:2]))
            if val not in pos_to_layers:
                pos_to_layers[val] = set()
            pos_to_layers[val].add(layer)
            extents = (
                (min(val[0], extents[0][0]), min(val[1], extents[0][1])),
                (max(val[0], extents[1][0]), max(val[1], extents[1][1]))
            )

for pad in circuit_pads:
    pos = parse_pos(get_symbol(pad, "at"))
    input_layers = get_symbol(pad, "layers")
    output_layers = set()
    for layer_spec in input_layers[1:]:
        if layer_spec == sexpdata.Symbol("*.Cu"):
            layer_spec = "*.Cu"
        output_layers |= set(fnmatch.filter([
            "F.Cu", "B.Cu", "F.Mask", "B.Mask"
        ], layer_spec))
    if get_symbol(pad, "remove_unused_layers"):
        layers_to_remove = set(fnmatch.filter(output_layers, "*.Cu"))
        pos_key = tuple(map(lambda x: round(x, 2), pos[:2]))
        if pos_key in pos_to_layers:
            layers_to_remove -= pos_to_layers[pos_key]
        output_layers -= layers_to_remove
    del input_layers[1:]
    for layer in output_layers:
        input_layers.append(layer)

##################################################################################################

def get_sub_dependencies(dependency):
    global lib_path

    r = set()
    src_path = os.path.join(lib_path, f"{dependency}.scad")
    with open(src_path, "rt") as f:
        for line in f:
            words = line.strip().split()
            if len(words) < 1:
                continue
            if words[0] in {"module", "function"}:
                return r
            elif words[0] == "use":
                rel_path = words[1][1:-1]
                dep_path = os.path.relpath(\
                    os.path.normpath(os.path.join(os.path.dirname(src_path), rel_path)),\
                    start = lib_path\
                )
                dependency = os.path.splitext(dep_path)[0]
                r.add(dependency)
    return r

def export_required_libraries(scad):
    global required_libraries, dependencies, lib_path, project_lib_path

    if len(required_libraries) == 0:
        return

    for required_library in sorted(required_libraries):
        scad.write(f"use <./scad/{required_library}.scad>\n")

    if not os.path.isdir(project_lib_path):
        if os.path.exists(project_lib_path):
            raise Exception(f"{project_lib_path} exists, but is not a directory")
        os.mkdir(project_lib_path)

    dependencies |= required_libraries
    new_deps = dependencies
    while len(new_deps) > 0:
        sub_deps = set()
        for dependency in new_deps:
            sub_deps |= get_sub_dependencies(dependency)
        sub_deps -= dependencies
        dependencies |= new_deps
        new_deps = sub_deps

    for dependency in sorted(dependencies):
        src_path = os.path.join(lib_path, f"{dependency}.scad")
        dst_path = os.path.join(project_lib_path, f"{dependency}.scad")
        if not os.path.isdir(os.path.dirname(dst_path)):
            os.mkdir(os.path.dirname(dst_path))
        shutil.copy(src_path, dst_path)

    scad.write(f"\n")

def layer_index_from_name(name):
    global layer_definitions

    return next(x for x in layer_definitions if type(x) == list and x[1] == name)[0]

def layer_name_from_index(index):
    global layer_definitions

    return next(x for x in layer_definitions if type(x) == list and x[0] == index)[1]

def export_layer_calculations(scad):
    scad.write(
        f"layer_thickness = [\n"
        f"  [\"F.Cu\", 0.4],\n"
        f"  [\"B.Cu\", 0.4],\n"
        f"  [\"F.Mask\", 0.4],\n"
        f"  [\"B.Mask\", 0.4]\n"
        f"];\n"
        f"\n"
    )
    scad.write(
        f"dielectric_thickness = max([\n"
        f"  0.4,\n"
        f"]);\n"
        f"\n"
    )
    scad.write(
        f"board_description = [\n"
        f"  layer_thickness,\n"
        f"  dielectric_thickness,\n"
        f"];\n"
        f"\n"
    )

def export_board_start(scad):
    location = ((extents[0][0] + extents[1][0])/2, (extents[0][1] + extents[1][1])/2)
    scad.write(
        f"mirror([0, 1, 0])\n"
        f"translate([{-location[0]}, {-location[1]}, 0])\n"
        f"board_assembly(\n"
        f"  invert = false,\n"
        f"  z_bounds = bounds_from_layers([\n"
        f"    \"F.Cu\", \"B.Cu\",\n"
        f"    \"F.Mask\", \"B.Mask\"\n"
        f"  ], board_description)\n"
        f") {{ // board start\n"
        f"union() {{ // circuit start\n"
        f"\n"
    )

def export_outline_start(scad):
    scad.write(
        f"\n"
        f"}} // circuit end\n"
        f"union() {{ // outline start\n"
        f"\n"
    )

def export_board_end(scad):
    scad.write(
        f"}} // outline end\n"
        f"}} // board end\n"
        f"\n"
    )

def export_layer_start(layer, scad):
    scad.write(
        f"/* LAYER {layer} */\n"
        f"draw_layer(\"{layer}\", board_description) {{\n"
    )

def export_layer_end(layer, scad):
    scad.write(
        f"}}\n"
        f"\n"
    )

def export_segment(item, scad):
    start = parse_pos(get_symbol(item, "start"))
    end = parse_pos(get_symbol(item, "end"))
    width = get_symbol(item, "width")[1]
    scad.write(
        f"  draw_segment(\n"
        f"    start = [{start[0]}, {start[1]}],\n"
        f"    end = [{end[0]}, {end[1]}],\n"
        f"    width = {width}\n"
        f"  );\n"
    )

def export_fp_line(item, scad):
    start = parse_pos(get_symbol(item, "start"))
    end = parse_pos(get_symbol(item, "end"))
    width = get_symbol(item, "width")[1]
    scad.write(
        f"  draw_fp_line(\n"
        f"    start = [{start[0]}, {start[1]}],\n"
        f"    end = [{end[0]}, {end[1]}],\n"
        f"    width = {width}\n"
        f"  );\n"
    )

def export_gr_rect(item, scad, *, force_fill = False):
    start = parse_pos(get_symbol(item, "start"))
    end = parse_pos(get_symbol(item, "end"))
    width = get_symbol(item, "width")[1]
    fill = force_fill or get_symbol(item, "fill")[1] == sexpdata.Symbol("solid")
    scad.write(
        f"  draw_gr_rect(\n"
        f"    start = [{start[0]}, {start[1]}],\n"
        f"    end = [{end[0]}, {end[1]}],\n"
        f"    width = {width},\n"
        f"    fill = {str(fill).lower()}\n"
        f"  );\n"
    )

def export_graphics_item(item, scad, *, force_fill = False):
    if type(item) != list:
        return
    if item[0] == sexpdata.Symbol("segment"):
        export_segment(item, scad)
    elif item[0] == sexpdata.Symbol("fp_line"):
        export_fp_line(item, scad)
    elif item[0] == sexpdata.Symbol("gr_rect"):
        export_gr_rect(item, scad, force_fill = force_fill)

def export_circuit_items(scad):
    global layer_graphics_items

    for (layer, items) in layer_graphics_items.items():
        if len(items) == 0:
            continue
        if layer not in [
            "F.Cu", "B.Cu", "F.Mask", "B.Mask"
        ]:
            continue
        export_layer_start(layer, scad)
        for item in items:
            export_graphics_item(item, scad)
        export_layer_end(layer, scad)

def export_pads(scad):
    global circuit_pads

    scad.write(
        f"/* PADS */\n"
    )
    for pad in circuit_pads:
        pos = parse_pos(get_symbol(pad, "at"))
        diameter = 0.4
        drill = get_symbol(pad, "drill")
        if drill:
            diameter = get_number(drill)
        layers = get_symbol(pad, "layers")
        scad.write(
            f"draw_pad(\n"
            f"  pos = [{pos[0]}, {pos[1]}],\n"
            f"  diameter = {diameter},\n"
            f"  z_bounds = bounds_from_layers([\n"
        )
        for layer in layers[1:]:
            scad.write(
                f"    \"{layer}\",\n"
            )
        scad.write(
            f"  ], board_description)\n"
            f");\n"
        )

def export_components(scad):
    global library_footprints

    scad.write(
        f"\n"
        f"/* CUSTOM COMPONENTS */\n"
    )
    for component in library_footprints:
        pos = parse_pos(get_symbol(component, "at"))
        layers = get_symbol(component, "layers")[1:]
        path = get_symbol(component, "scad_path")[1]
        module = os.path.relpath(os.path.splitext(path)[0], start = lib_path)\
            .replace("/", "_").replace(".", "_")
        scad.write(
            f"{module}([\n"
            f"  [{pos[0]}, {pos[1]}],\n"
            f"  [\n"
        )
        for layer in layers:
            scad.write(
                f"    \"{layer}\",\n"
            )
        scad.write(
            f"  ]\n"
            f"]);\n"
        )

def export_outline_items(scad):
    global layer_graphics_items

    if "Edge.Cuts" not in layer_graphics_items:
        return
    for item in layer_graphics_items["Edge.Cuts"]:
        export_graphics_item(item, scad, force_fill = True)

with open(scad_path, "wt") as scad:
    scad.write(
        "/***************************************\n"
        "This file has been automatically created\n"
        "by kiconvert.py, a Python script to make\n"
        "OpenSCAD files from KiCAD board files\n"
        "for microfluidics applications.\n"
        "***************************************/\n"
        "\n"
    )
    export_required_libraries(scad)
    export_layer_calculations(scad)
    export_board_start(scad)
    export_circuit_items(scad)
    export_pads(scad)
    export_components(scad)
    export_outline_start(scad)
    export_outline_items(scad)
    export_board_end(scad)
