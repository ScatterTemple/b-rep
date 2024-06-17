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


def read_step_file(filename):
    reader = STEPControl_Reader()
    reader.ReadFile(filename)
    reader.TransferRoots()
    shape = reader.OneShape()
    return shape


def get_edges(shape):
    edges = []
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while edge_explorer.More():
        edges.append(edge_explorer.Current())
        edge_explorer.Next()
    return edges


def get_faces(shape):
    faces = []
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while face_explorer.More():
        faces.append(face_explorer.Current())
        face_explorer.Next()
    return faces


def create_graph_representation(shape):
    faces = get_faces(shape)
    edges = get_edges(shape)
    edge_2_faces = []

    # Create a graph using NetworkX
    graph = nx.Graph()

    # Add nodes (faces) to the graph
    for face in faces:
        graph.add_node(face)

    # Map edges to the faces they are connected to
    edge_to_faces = TopTools_IndexedDataMapOfShapeListOfShape()
    topexp_MapShapesAndAncestors(shape, TopAbs_EDGE, TopAbs_FACE, edge_to_faces)

    # for each edge
    for i in range(1, edge_to_faces.Size() + 1):
        edge = topods.Edge(edge_to_faces.FindKey(i))
        if edge not in edges:
            raise Exception('決定された edge は edges の中にありません。')
        # if edge has 2 adjusting faces
        face_pair = edge_to_faces.FindFromIndex(i)
        if face_pair.Size() == 2:
            face1 = topods.Face(face_pair.First())
            face2 = topods.Face(face_pair.Last())
            edge_2_faces.append([
                face1,
                face2
            ])
            if (face1 in faces) and (face2 in faces):
                graph.add_edge(face1, face2, edge=edge)
            else:
                raise Exception('決定された face は faces の中にありません。')
        else:
            raise Exception(f'edge_to_faces.FindFromIndex(i).Size() is {edge_to_faces.FindFromIndex(i).Size()}!!!')


    return edge_2_faces, graph


def calculate_edge_convexity(edge, shape):
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while face_explorer.More():
        face = topods.Face(face_explorer.Current())
        edges = TopExp_Explorer(face, TopAbs_EDGE)
        while edges.More():
            current_edge = topods.Edge(edges.Current())
            if current_edge.IsEqual(edge):
                faces.append(face)
            edges.Next()
        face_explorer.Next()

    if len(faces) == 2:
        face1, face2 = faces
        surf1 = BRepAdaptor_Surface(face1, True)
        surf2 = BRepAdaptor_Surface(face2, True)

        u1, v1 = topexp.FirstUV(edge, face1)
        u2, v2 = topexp.FirstUV(edge, face2)

        norm1 = surf1.Normal(u1, v1)
        norm2 = surf2.Normal(u2, v2)

        angle = norm1.Angle(norm2)

        if angle > 3.14159:  # Angle > 180 degrees
            return -1  # Concave
        else:
            return 1  # Convex
    else:
        return 1  # Default to convex for boundary edges or unusual cases


def calculate_face_convexity(face):
    vertex_explorer = TopExp_Explorer(face, TopAbs_VERTEX)
    convexity = 1  # Default to convex

    while vertex_explorer.More():
        vertex = topods_Vertex(vertex_explorer.Current())
        vertex_pnt = BRep_Tool.Pnt(vertex)

        edge_explorer = TopExp_Explorer(face, TopAbs_EDGE)
        internal_angle_sum = 0.0
        num_adjacent_edges = 0

        while edge_explorer.More():
            edge = topods.Edge(edge_explorer.Current())
            curve_adaptor = BRepAdaptor_Curve(edge)
            umin, umax = curve_adaptor.FirstParameter(), curve_adaptor.LastParameter()

            edge_start = curve_adaptor.Value(umin)
            edge_end = curve_adaptor.Value(umax)

            if vertex_pnt.IsEqual(edge_start, 1e-6) or vertex_pnt.IsEqual(edge_end, 1e-6):
                # Calculate the internal angle at the vertex
                if num_adjacent_edges == 0:
                    prev_edge_dir = edge_end.Subtracted(edge_start).Normalized()
                else:
                    curr_edge_dir = edge_end.Subtracted(edge_start).Normalized()
                    angle = prev_edge_dir.Angle(curr_edge_dir)
                    internal_angle_sum += angle
                    prev_edge_dir = curr_edge_dir

                num_adjacent_edges += 1

            edge_explorer.Next()

        # Check if the sum of angles is less than 360 degrees
        if internal_angle_sum >= 2 * 3.14159:  # 2 * PI
            convexity = -1  # Concave
            break

        vertex_explorer.Next()

    return convexity


def main():
    import os
    here = os.path.dirname(__file__)
    filename = os.path.join(here, 'sample-step', 'cube.step')
    shape = read_step_file(filename)
    face_pair_list, graph = create_graph_representation(shape)

    # For demonstration, print the nodes and edges
    print(f'{len(face_pair_list)} face_pairs are detected.')
    for face_pair in face_pair_list:
        print(face_pair)

    print()
    print(graph)


if __name__ == '__main__':
    main()
