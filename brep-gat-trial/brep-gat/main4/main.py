import os

from occ import read_step_file, create_graph_representation, add_element_features
from graph import show, compare_graphs


if __name__ == '__main__':
    here = os.path.dirname(__file__)

    filename = os.path.join(here, '..', 'sample-step', 'curved-cube.step')
    shape = read_step_file(filename)
    graph = create_graph_representation(shape)
    add_element_features(graph)
    show(graph)

    graph1 = graph

    filename = os.path.join(here, '..', 'sample-step', 'cube.step')
    shape = read_step_file(filename)
    graph = create_graph_representation(shape)
    add_element_features(graph)
    show(graph)

    graph2 = graph

    compare_graphs(graph1, graph2)


