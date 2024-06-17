import glob
import os
import csv
import pickle
import numpy as np


class Face:
    def __init__(self, tag):
        self.tag = tag
        self.id = None
        self.label = None
        self.facets = []
        self.a = None
        self.b = None
        self.c = None
        self.d = None


class Facet:
    def __init__(self, tag):
        self.tag = tag
        self.a = None
        self.b = None
        self.c = None
        self.d = None


def get_graph_files(root, directory):
    dir_path = os.path.join(root, directory)
    face_feature_path = dir_path + "/" + directory + "_facefeature.csv"
    face_adj_path = dir_path + "/" + directory + "_faceadj.csv"
    face_facet_link_path = dir_path + "/" + directory + "_facefacetlink.csv"
    facet_feature_path = dir_path + "/" + directory + "_facetfeature.csv"

    return face_feature_path, face_adj_path, face_facet_link_path, facet_feature_path


def files_exist(paths):
    for path in paths:
        if not os.path.isfile(path):
            return False
    return True


def get_graph_data(face_feature_path, face_adj_path, face_facet_link_path, facet_feature_path):
    face_class_dict = {}
    facet_class_dict = {}
    edge_list = []

    with open(face_feature_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue
            face = Face(int(row[0]))
            face.label = int(row[-1])
            face.id = i

            face_class_dict[face.tag] = face

    with open(face_facet_link_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue

            face_class_dict[int(row[0])].facets.append(int(row[1]))

    with open(facet_feature_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue

            facet = Facet(int(row[0]))
            facet.a = float(row[1])
            facet.b = float(row[2])
            facet.c = float(row[3])
            facet.d = float(row[4])

            facet_class_dict[facet.tag] = facet

    for key, value in face_class_dict.items():
        face_class_dict[key].a = facet_class_dict[value.facets[0]].a
        face_class_dict[key].b = facet_class_dict[value.facets[0]].b
        face_class_dict[key].c = facet_class_dict[value.facets[0]].c
        face_class_dict[key].d = facet_class_dict[value.facets[0]].d

    with open(face_adj_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue

            if row[0] == "null" or row[1] == "null":
                continue
            elif row[0] == row[1]:
                continue
            else:
                edge_list.append([face_class_dict[int(row[0])].id - 1, face_class_dict[int(row[1])].id - 1])
                edge_list.append([face_class_dict[int(row[1])].id - 1, face_class_dict[int(row[0])].id - 1])

    x = []
    y = []

    for values in face_class_dict.values():
        x.append([values.a, values.b, values.c, values.d])
        y.append(values.label)

    return x, y, edge_list


def pickle_graph(features, labels, edges, file):
    pickle_dict = {}
    pickle_dict["x"] = features
    pickle_dict["edge_index"] = edges
    pickle_dict["y"] = labels
    file_path = "data/graphs/" + file + ".graph"

    with open(file_path, 'wb') as handle:
        pickle.dump(pickle_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    csv_root = "/home/mlg/Documents/Andrew/Hierarchical-GCNN/hiergcn/data/CSVs_Planar/"
    csv_list = os.listdir(csv_root)

    count = 0
    for c in csv_list:
        if len(os.listdir(os.path.join(csv_root, c))) == 0:
            continue
        else:
            face_path, face_a_path, ff_link_path, facet_path = get_graph_files(csv_root, c)
            if files_exist([face_path, face_a_path, ff_link_path, facet_path]):
                x, y, edge_index = get_graph_data(face_path, face_a_path, ff_link_path, facet_path)
                pickle_graph(x, y, edge_index, c)
                count += 1

    print(count)
