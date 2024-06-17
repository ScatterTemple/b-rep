from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.BRepTools import breptools
from OCC.Core.TopExp import TopExp_Explorer


def read_step_file(filename):
    reader = STEPControl_Reader()
    reader.ReadFile(filename)
    reader.TransferRoots()
    shape = reader.OneShape()
    return shape


def extract_edge_features(shape):
    edge_features = []
    edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while edge_explorer.More():
        edge = edge_explorer.Current()
        curve_adaptor = BRepAdaptor_Curve(edge)
        curve_type = curve_adaptor.GetType()

        # Calculate length
        length = GCPnts_AbscissaPoint.Length(curve_adaptor)

        # Check for convexity or other properties as needed
        # (for simplicity, assuming all edges are straight)
        convexity = 1  # Placeholder value

        edge_features.append({
            'curve_type': curve_type,
            'length': length,
            'convexity': convexity
        })

        edge_explorer.Next()
    return edge_features


def extract_face_features(shape):
    face_features = []
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while face_explorer.More():
        face = face_explorer.Current()
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

        face_features.append({
            'surface_type': surface_type,
            'bounding_box_ratio': bounding_box_ratio,
            'surface_area': surface_area,
            'normal': (normal.X(), normal.Y(), normal.Z())
        })

        face_explorer.Next()
    return face_features


def create_graph_representation(face_features, edge_features):
    graph_nodes = [{'type': 'face', 'features': f} for f in face_features]
    graph_edges = [{'type': 'edge', 'features': e} for e in edge_features]

    # Placeholder for graph edges connections (add your logic here)
    for edge in graph_edges:
        # Example connection, adjust based on your logic
        edge['nodes'] = (0, 1)  # Connect node 0 and node 1

    return graph_nodes, graph_edges


def main():
    import os
    here = os.path.dirname(__file__)
    filename = os.path.join(here, 'sample-step', 'as1-ac-214.stp')
    shape = read_step_file(filename)

    print('===== edge features =====')
    edge_features = extract_edge_features(shape)
    for edge_feature in edge_features:
        print(edge_feature)

    print('===== face features =====')
    face_features = extract_face_features(shape)
    for face_feature in face_features:
        print(face_feature)

    print('===== graph =====')
    graph_nodes, graph_edges = create_graph_representation(face_features, edge_features)
    print(graph_nodes)
    print(graph_edges)


if __name__ == '__main__':
    main()