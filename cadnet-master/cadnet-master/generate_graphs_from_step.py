import os
import glob
import pickle
import numpy as np
import utils.shape as shape
import utils.occ_face as occ_face
import utils.occ_utils as occ_utils


def feature_from_face(face_util):
    normal = occ_utils.as_list(occ_utils.normal_to_face_center(face_util))
    _, pnt = face_util.mid_point()
    pnt = occ_utils.as_list(pnt)
    d = np.dot(normal, pnt)
    return normal + [d]


def graph_from_shape(a_shape):
    a_graph = dict()
    a_graph['y'] = a_shape.face_truth
    a_graph['x'] = [None] * len(a_shape.face_ids)
    a_graph['edge_index'] = [[], []]

    for face in a_shape.face_ids:
        face_util = occ_face.Face(face)
        a_graph['x'][a_shape.face_ids[face]] = feature_from_face(face_util)
        for edge in face_util.edges():
            face_adjacent = occ_utils.face_adjacent(a_shape.shape, face, edge)
            a_graph['edge_index'][0].append(a_shape.face_ids[face])
            a_graph['edge_index'][1].append(a_shape.face_ids[face_adjacent])
    return a_graph


def save_graph(graph, graph_path, shape_name):
    with open(os.path.join(graph_path, shape_name + '.graph'), 'wb') as file:
        pickle.dump(graph, file)


def generate_graph(shape_dir, graph_path, shape_name):
    """Generate points for shapes listed in CATEGORY_NAME_step.txt
    """
    # if os.path.exists(os.path.join(graph_path, shape_name + '.graph')):
    #     return 0
    try:
        a_shape = shape.LabeledShape()
        a_shape.load(shape_dir, shape_name)
    except Exception as e:
        print(shape_name + ' failed loading')
        print(f"Error: {e}")
        return 0

    try:
        a_graph = graph_from_shape(a_shape)
    except:
        print(shape_name + 'failed to create graph')
        print(f"Error: {e}")
        return 0

    save_graph(a_graph, graph_path, shape_name)
    return 1


if __name__ == '__main__':
    shape_dir = "data/steps/"
    graph_dir = "data/graphs/"

    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)

    shape_paths = glob.glob(shape_dir + '*.step')
    shape_names = [shape_path.split(os.sep)[-1].split('.')[0] for shape_path in shape_paths]

    for shape_name in shape_names:
        generate_graph(shape_dir, graph_dir, shape_name)
