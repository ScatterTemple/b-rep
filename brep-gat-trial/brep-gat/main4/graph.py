import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial.distance import cosine


def show(graph):

    pos = nx.spring_layout(graph, k=5)
    nx.draw(graph, pos, with_labels=True)
    features = nx.get_node_attributes(graph, 'features')

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

    features = nx.get_edge_attributes(graph, 'features')
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
    plt.show()


from scipy.spatial.distance import cosine


def feature_similarity(f1, f2):
    return 1 - cosine(f1, f2)


def compare_graphs(G1, G2):
    node_correspondence = {}

    for node1 in G1.nodes(data=True):
        max_similarity = -1
        best_match = None
        for node2 in G2.nodes(data=True):
            similarity = feature_similarity(node1[1]['features'], node2[1]['features'])
            if similarity > max_similarity:
                max_similarity = similarity
        #         best_match = node2[0]
        # node_correspondence[node1[0]] = best_match
                best_match = node2[1]['features']
        node_correspondence[node1[1]['features']] = best_match

    print("Node Correspondence from G2 to G1:", node_correspondence)
    return node_correspondence


if __name__ == '__main__':
    import networkx as nx
    import numpy as np
    from scipy.spatial.distance import cosine

    # Initialize the first graph with 3 nodes
    G1 = nx.Graph()
    G1.add_node(1, feature=[0.1, 0.2, 0.3])
    G1.add_node(2, feature=[0.4, 0.5, 0.6])
    G1.add_node(3, feature=[0.7, 0.8, 0.9])
    G1.add_edge(1, 2, feature=[1.1, 1.2])
    G1.add_edge(2, 3, feature=[1.3, 1.4])
    G1.add_edge(1, 3, feature=[1.5, 1.6])

    # Initialize the second graph with 4 nodes
    G2 = nx.Graph()
    G2.add_node(1, feature=[0.1, 0.2, 0.31])
    G2.add_node(2, feature=[0.4, 0.51, 0.6])
    G2.add_node(3, feature=[0.71, 0.8, 0.9])
    G2.add_node(4, feature=[0.9, 1.0, 1.1])
    G2.add_edge(1, 2, feature=[1.1, 1.21])
    G2.add_edge(2, 3, feature=[1.31, 1.4])
    G2.add_edge(1, 3, feature=[1.51, 1.6])
    G2.add_edge(3, 4, feature=[1.7, 1.8])
    correspondence = compare_graphs(G2, G1)
    print("Node Correspondence from G2 to G1:", correspondence)