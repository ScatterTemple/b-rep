from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer, topexp_MapShapesAndAncestors
from OCC.Core.TopoDS import TopoDS_Shape
import networkx as nx  # Using NetworkX to create the graph representation
from OCC.Core.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCC.Core.TopoDS import topods

from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopExp import topexp
from OCC.Core.TopAbs import TopAbs_REVERSED
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.TopoDS import topods
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE
from OCC.Core.TopoDS import topods_Vertex
from OCC.Core.BRep import BRep_Tool
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.BRepTools import breptools
from OCC.Core.TopExp import TopExp_Explorer

from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopoDS import topods
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE

import os
from typing import List


def read_step_file(filename: str) -> TopoDS_Shape:
    if not os.path.exists(filename):
        raise FileNotFoundError
    reader = STEPControl_Reader()
    reader.ReadFile(filename)
    reader.TransferRoots()
    shape = reader.OneShape()
    return shape


def get_edges(shape: TopoDS_Shape) -> List[TopoDS_Shape]:
    edges = []
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while edge_explorer.More():
        edges.append(edge_explorer.Current())
        edge_explorer.Next()
    return edges


def get_faces(shape: TopoDS_Shape) -> List[TopoDS_Shape]:
    faces = []
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while face_explorer.More():
        faces.append(face_explorer.Current())
        face_explorer.Next()
    return faces


def create_graph_representation(shape: TopoDS_Shape) -> nx.Graph:
    faces = get_faces(shape)
    edges = get_edges(shape)

    # Create a graph using NetworkX
    graph = nx.Graph()

    # Add nodes (faces) to the graph
    for face in faces:
        # face_feature = extract_face_features(face)
        # graph.add_node(face, feature=face_feature)
        graph.add_node(face)

    # Map edges to the faces they are connected to
    edges_and_their_faces = TopTools_IndexedDataMapOfShapeListOfShape()
    topexp_MapShapesAndAncestors(shape, TopAbs_EDGE, TopAbs_FACE, edges_and_their_faces)

    # add each edge and its adjusting faces to the graph
    for index in range(1, edges_and_their_faces.Size() + 1):
        # acquire edge
        edge = topods.Edge(edges_and_their_faces.FindKey(index))

        assert edge in edges, '決定された edge は edges の中にありません。'

        # edge_feature = extract_edge_features(edge)

        # check if edge has 2 adjusting faces
        face_pair = edges_and_their_faces.FindFromIndex(index)

        assert face_pair.Size() == 2, f'edge に接続している face が {face_pair.Size()} (!= 2) 個です。'

        face1 = topods.Face(face_pair.First())
        face2 = topods.Face(face_pair.Last())
        # graph.add_edge(face1, face2, edge=edge, feature=edge_feature)
        graph.add_edge(face1, face2, edge=edge)

    return graph


def extract_edge_features(edge):
    curve_adaptor = BRepAdaptor_Curve(edge)
    curve_type = curve_adaptor.GetType()

    # Calculate length
    length = GCPnts_AbscissaPoint.Length(curve_adaptor)

    # Check for convexity or other properties as needed
    # (for simplicity, assuming all edges are straight)
    convexity = 1  # Placeholder value

    edge_feature = {
        'curve_type': curve_type,
        'length': length,
        'convexity': convexity,
        'null': None,
    }

    return edge_feature


def extract_face_features(face):
    surface_adaptor = BRepAdaptor_Surface(face, True)
    surface_type = surface_adaptor.GetType()

    # Get the UV bounding box
    umin, umax, vmin, vmax = breptools.UVBounds(face)
    bounding_box_ratio = (umax - umin) / (vmax - vmin) if (vmax - vmin) != 0 else 0

    # Get the surface area
    props = GProp_GProps()
    brepgprop.SurfaceProperties(face, props)
    surface_area = props.Mass()

    # Get the surface normal at the center of the face
    u_mid = (umin + umax) / 2
    v_mid = (vmin + vmax) / 2
    geom_surface = surface_adaptor.Surface().Surface()
    props = GeomLProp_SLProps(geom_surface, 1, 1e-6)
    props.SetParameters(u_mid, v_mid)
    normal = props.Normal()

    face_feature = {
        'surface_type': surface_type,
        'bounding_box_ratio': bounding_box_ratio,
        'surface_area': surface_area,
        'normal': (normal.X(), normal.Y(), normal.Z())
    }

    return face_feature['normal']


def add_element_features(graph: nx.Graph):
    # グラフの各 node と edge について、論文に述べられている feature を計算する。
    # 隣との関係性で計算される feature もあるので、graph を受けるようにする。
    # ここの実装は仮実装
    nodes = nx.NodeView = graph.nodes
    for face, node in nodes.items():
        node['features'] = extract_face_features(face)

    edges = nx.EdgeView = graph.edges
    for face_pair, edge in edges.items():
        b_edge = edge['edge']
        edge['features'] = extract_edge_features(b_edge)



# def calculate_edge_convexity(edge, shape):
#     face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
#     faces = []
#     while face_explorer.More():
#         face = topods.Face(face_explorer.Current())
#         edges = TopExp_Explorer(face, TopAbs_EDGE)
#         while edges.More():
#             current_edge = topods.Edge(edges.Current())
#             if current_edge.IsEqual(edge):
#                 faces.append(face)
#             edges.Next()
#         face_explorer.Next()
#
#     if len(faces) == 2:
#         face1, face2 = faces
#         surf1 = BRepAdaptor_Surface(face1, True)
#         surf2 = BRepAdaptor_Surface(face2, True)
#
#         u1, v1 = topexp.FirstUV(edge, face1)
#         u2, v2 = topexp.FirstUV(edge, face2)
#
#         norm1 = surf1.Normal(u1, v1)
#         norm2 = surf2.Normal(u2, v2)
#
#         angle = norm1.Angle(norm2)
#
#         if angle > 3.14159:  # Angle > 180 degrees
#             return -1  # Concave
#         else:
#             return 1  # Convex
#     else:
#         return 1  # Default to convex for boundary edges or unusual cases
#
#
# def calculate_face_convexity(face):
#     vertex_explorer = TopExp_Explorer(face, TopAbs_VERTEX)
#     convexity = 1  # Default to convex
#
#     while vertex_explorer.More():
#         vertex = topods_Vertex(vertex_explorer.Current())
#         vertex_pnt = BRep_Tool.Pnt(vertex)
#
#         edge_explorer = TopExp_Explorer(face, TopAbs_EDGE)
#         internal_angle_sum = 0.0
#         num_adjacent_edges = 0
#
#         while edge_explorer.More():
#             edge = topods.Edge(edge_explorer.Current())
#             curve_adaptor = BRepAdaptor_Curve(edge)
#             umin, umax = curve_adaptor.FirstParameter(), curve_adaptor.LastParameter()
#
#             edge_start = curve_adaptor.Value(umin)
#             edge_end = curve_adaptor.Value(umax)
#
#             if vertex_pnt.IsEqual(edge_start, 1e-6) or vertex_pnt.IsEqual(edge_end, 1e-6):
#                 # Calculate the internal angle at the vertex
#                 if num_adjacent_edges == 0:
#                     prev_edge_dir = edge_end.Subtracted(edge_start).Normalized()
#                 else:
#                     curr_edge_dir = edge_end.Subtracted(edge_start).Normalized()
#                     angle = prev_edge_dir.Angle(curr_edge_dir)
#                     internal_angle_sum += angle
#                     prev_edge_dir = curr_edge_dir
#
#                 num_adjacent_edges += 1
#
#             edge_explorer.Next()
#
#         # Check if the sum of angles is less than 360 degrees
#         if internal_angle_sum >= 2 * 3.14159:  # 2 * PI
#             convexity = -1  # Concave
#             break
#
#         vertex_explorer.Next()
#
#     return convexity


def main():
    import os
    here = os.path.dirname(__file__)
    # filename = os.path.join(here, 'sample-step', 'cube.step')
    filename = os.path.join(here, 'sample-step', 'curved-cube.step')
    shape = read_step_file(filename)
    graph = create_graph_representation(shape)

    # For demonstration, print the nodes and edges
    # print(f'{len(face_pair_list)} face_pairs are detected.')
    # for face_pair in face_pair_list:
    #     print(face_pair)

    print()
    print(graph)

    import matplotlib.pyplot as plt
    pos = nx.spring_layout(graph, k=5)
    nx.draw(graph, pos, with_labels=True)
    features = nx.get_node_attributes(graph, 'feature')

    labels = dict()
    for node in graph.nodes:
        print('=====')
        print(type(features[node]))
        message = str(features[node])
        print(message)
        message = message.replace('{', '')
        message = message.replace('}', '')
        message = message.replace(', \'', '\n')
        message = message.replace("'", '')
        print(message)
        labels[node] = f"\n\n\n\n\n{message}"
    nx.draw_networkx_labels(graph, pos, labels=labels)

    features = nx.get_edge_attributes(graph, 'feature')
    labels = dict()
    for edge in graph.edges:
        print('=====')
        print(type(features[edge]))
        message = str(features[edge])
        print(message)
        message = message.replace('{', '')
        message = message.replace('}', '')
        message = message.replace(', \'', '\n')
        message = message.replace("'", '')
        print(message)
        labels[edge] = f"{message}"
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=labels
    )



    # nx.draw_networkx_labels(graph, pos, labels=features)
    plt.show()


if __name__ == '__main__':
    main()
