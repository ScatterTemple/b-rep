import pickle
import os
import torch
from torch_geometric.data import Data, InMemoryDataset


class FaceNet(InMemoryDataset):
    def __init__(self, root, data_list_file):
        super(FaceNet, self).__init__(root)

        data_list = []
        with open(data_list_file, 'rb') as file:
            paths = pickle.load(file)

        for path in paths:
            path = os.path.join(root, path)

            try:
                with open(path, 'rb') as file:
                    a_graph = pickle.load(file)
                    x = torch.tensor(a_graph['x'], dtype=torch.float)
                    edge_index = torch.tensor(a_graph['edge_index'], dtype=torch.long)
                    y = torch.tensor(a_graph['y'], dtype=torch.long)
                    #data = Data(x=x, edge_index=edge_index.t().contiguous(), y=y)
                    data = Data(x=x, edge_index=edge_index, y=y)
                    data_list.append(data)

            except:
                print(path)

        self.data, self.slices = self.collate(data_list)

    @property
    def raw_file_names(self):
        return ['simple']

    @property
    def processed_file_names(self):
        return ['simple']

    def download(self):
        pass

    def process(self):
        pass
