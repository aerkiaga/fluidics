# Custom footprints

You can create custom footprints by adding the appropriate files in `kicad/footprints`.
The script will generate them as series of draw commands on different layers.
It's also possible to write custom OpenSCAD scripts to have more control over the final result.

## Standard footprints
A board, by default, has two "copper" connection layers, `F.Cu` and `B.Cu`.
The first is above the second, and both can be used to carry channels, rather than copper wires.
In between them is the "dielectric", a variably thick layer of material.
Above `F.Cu` and below `B.Cu` lie `F.Mask` and `B.Mask`, respectively;
these are meant to hydraulically insulate the connections.

![Layers diagram](src/layers.png)

All of these except the dielectric have a configurable size, set at the start of the output script.
The dielectric, though, is given a size according to the structures it must hold, more on that later.
Drawing on a layer in KiCAD will result in that segment of the layer being emptied in the script.

In order to be optimal, pads should have "Connected layers only" enabled, and not use any copper layer.
That way, the Python script will only create holes between the layers they actually require.
For example, you can select just `F.Mask` to create a hole to the top side, and connect it to any layer.


## OpenSCAD footprints
To make these, you must also create a KiCAD schematic, which will serve as the scaffold to build upon.
More importantly, drawn elements (but not pads!) on it will determine what layers the component can span.
Implicitly, all components can extend into the dielectric layer.
