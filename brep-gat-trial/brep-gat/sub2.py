import os
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TDF import TDF_LabelSequence
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.TDF import TDF_Label
from OCC.Core.TCollection import TCollection_ExtendedString


def read_step_file(file_path):
    # Initialize the STEP reader
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(file_path)
    if status != 1:
        raise Exception("Error reading STEP file.")

    # Transfer contents to the document
    step_reader.TransferRoot()
    shape = step_reader.Shape()

    return shape


def get_shape_colors(doc):
    # Get the document tool for the colors
    colors_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())

    # Get all shapes
    shapes_labels = TDF_LabelSequence()
    colors_tool.GetColors()  # GetShapes(shapes_labels)




    # Store shape colors
    shape_colors = {}

    for i in range(shapes_labels.Length()):
        label = shapes_labels.Value(i + 1)
        if colors_tool.IsSet(label, XCAFDoc_ColorSurf):
            color = Quantity_Color()
            colors_tool.GetColor(label, XCAFDoc_ColorSurf, color)
            shape_colors[label] = color

    return shape_colors


def main(step_file_path):
    # Initialize the application and create a new document
    app = XCAFApp_Application.GetApplication().GetApplication()  # GetObject()
    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))
    app.NewDocument(TCollection_ExtendedString("Model"), doc)

    # Read the STEP file
    shape = read_step_file(step_file_path)

    # Get shape colors
    shape_colors = get_shape_colors(doc)

    # Print the colors
    for label, color in shape_colors.items():
        print(f"Label: {label}, Color: {color.Red()}, {color.Green()}, {color.Blue()}")


from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TDF import TDF_LabelSequence


if __name__ == "__main__":

    import os
    here = os.path.dirname(__file__)
    # filename = os.path.join(here, 'sample-step', 'cube.step')
    filename = os.path.join(here, 'sample-step', 'curved-cube.step')

    app = XCAFApp_Application.GetApplication().GetApplication()  # GetObject()

    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

    app.NewDocument(TCollection_ExtendedString("Model"), doc)

    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    l_colors = XCAFDoc_DocumentTool.ColorTool(doc.Main())
    l_layers = XCAFDoc_DocumentTool.LayerTool(doc.Main())
    l_materials = XCAFDoc_DocumentTool.MaterialTool(doc.Main())

    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)

    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)

    labels = TDF_LabelSequence()
    color_labels = TDF_LabelSequence()
    shape_tool.GetFreeShapes(labels)

    print("Number of shapes at root :%i" % labels.Length())
    for i in range(labels.Length()):
        sub_shapes_labels = TDF_LabelSequence()
        print("Is Assembly :", shape_tool.IsAssembly(labels.Value(i + 1)))
        sub_shapes = shape_tool.GetSubShapes(labels.Value(i + 1), sub_shapes_labels)
        print("Number of subshapes in the assemly :%i" % sub_shapes_labels.Length())
    l_colors.GetColors(color_labels)

    print("Number of colors=%i" % color_labels.Length())
    for i in range(color_labels.Length()):
        color = color_labels.Value(i + 1)
        # print(color.())
        pass


