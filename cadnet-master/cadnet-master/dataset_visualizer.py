# -*- coding: utf-8 -*-
"""
A visualization tool for the machining feature dataset
"""
import os
import pickle
import random
import glob

from OCC.Core.Quantity import Quantity_NOC_WHITE, Quantity_Color
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.StepRepr import StepRepr_RepresentationItem
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.AIS import AIS_ColoredShape
from OCC.Display.SimpleGui import init_display


FEAT_NAMES = ['rectangular_through_slot', 'triangular_through_slot',
              'rectangular_passage', 'triangular_passage', '6sides_passage',
              'rectangular_through_step', '2sides_through_step', 'slanted_through_step',
              'rectangular_blind_step', 'triangular_blind_step',
              'rectangular_blind_slot',
              'rectangular_pocket', 'triangular_pocket', '6sides_pocket',
              'chamfer', 'stock']

COLORS = {"chamfer": 0, "through_hole": 10, "triangular_passage": 20, "rectangular_passage": 30,
          "6sides_passage": 40, "triangular_through_slot": 50, "rectangular_through_slot": 60,
          "circular_through_slot": 70, "rectangular_through_step": 80, "2sides_through_step": 90,
          "slanted_through_step": 100, "Oring": 110, "blind_hole": 120, "triangular_pocket": 130,
          "rectangular_pocket": 140, "6sides_pocket": 150, "circular_end_pocket": 160,
          "rectangular_blind_slot": 170, "v_circular_end_blind_slot": 180, "h_circular_end_blind_slot": 190,
          "triangular_blind_step": 200, "circular_blind_step": 210, "rectangular_blind_step": 220, "round": 230,
          "stock": 255}


def list_face(shape):
    """
    input
        shape: TopoDS_Shape
    output
        fset: [TopoDS_Face]
    """
    fset = set()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        s = exp.Current()
        exp.Next()
        face = topods.Face(s)
        fset.add(face)

    return list(fset)


def shape_with_fid_from_step(filename):
    """
    input
        filename:   path to the step file
    output
        shape:      TopoDS_Shape
        id_map:  {TopoDS_Face: int}
    """
    if not os.path.exists(filename):
        print(filename, 'does not exists')
        return None, None

    reader = STEPControl_Reader()
    reader.ReadFile(filename)
    reader.TransferRoots()
    shape = reader.OneShape()

    treader = reader.WS().TransferReader()

    id_map = {}
    fset = list_face(shape)
    # read the face names
    for face in fset:
        item = treader.EntityFromShapeResult(face, 1)
        if item is None:
            print(face)
            continue
        item = StepRepr_RepresentationItem.DownCast(item)
        name = item.Name().ToCString()
        if name:
            try:
                nameid = int(name)
                id_map[face] = nameid
            except ValueError:
                print(face)

    return shape, id_map


def display():
    global shape_index
    global shape_paths
    
    shape, face_ids = shape_with_fid_from_step(shape_paths[shape_index])
    if shape == None:
        return
    
    label_file = shape_paths[shape_index].split('.')[0] + '.face_truth'
    with open(label_file, 'rb') as file:
        face_labels = pickle.load(file)
        
    occ_display.EraseAll()
    AIS = AIS_ColoredShape(shape)
    
    for f in face_ids:
        fname = FEAT_NAMES[face_labels[face_ids[f]]]
        AIS.SetCustomColor(f, colors[fname])

    occ_display.Context.Display(AIS, True)
    occ_display.View_Iso()
    occ_display.FitAll()


def show_first():
    global shape_index
    shape_index = 0
    display()


def show_last():
    global shape_index
    global shape_paths    
    
    shape_index = len(shape_paths) - 1
    display()

    
def show_next():
    global shape_index
    global shape_paths
    
    shape_index = (shape_index + 1) % len(shape_paths)
    display()


def show_previous():
    global shape_index
    global shape_paths

    shape_index = (shape_index - 1 + len(shape_paths)) % len(shape_paths)
    display()

    
def show_random():
    global shape_index
    global shape_paths
    
    shape_index = random.randrange(0, len(shape_paths))
    display()


if __name__ == '__main__':
    dataset_dir = "dataset/step/"

    colors = {name: Quantity_Color(COLORS[name]) for name in COLORS}

    occ_display, start_occ_display, add_menu, add_function_to_menu = init_display()

    add_menu('explore')
    add_function_to_menu('explore', show_random)
    add_function_to_menu('explore', show_next)
    add_function_to_menu('explore', show_previous)
    add_function_to_menu('explore', show_first)
    add_function_to_menu('explore', show_last)

    shape_paths = glob.glob(dataset_dir + '*.step')
    print(shape_paths)
    print(len(shape_paths), 'shapes')

    if len(shape_paths) > 0:
        show_random()

    start_occ_display()
