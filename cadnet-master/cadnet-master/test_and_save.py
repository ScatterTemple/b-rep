"""
This module can be used to load a STEP file and use a pre-trained neural network model
to generate machining feature labels for each B-Rep face. These are used to save a new
STEP file and .face_truth Pickle file.
"""

import os
import pickle
import argparse
import glob

import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Dropout, Linear as Lin, ReLU, BatchNorm1d as BN
from torch_geometric.data import Data, DataLoader
from FaceNet import FaceNet
from generate_graphs_from_step import generate_graph
from network import Net
from utils.shape import LabeledShape


def load_checkpoint(checkpoint, model):
    """Load a pre-trained network model from a checkpoint."""
    if not os.path.exists(checkpoint):
        raise ("File doesn't exist {}".format(checkpoint))
    checkpoint = torch.load(checkpoint, map_location='cpu')
    model.load_state_dict(checkpoint['model'])

    return checkpoint


def test(loader, model, device, with_labels=False):
    """Test network model on single STEP file."""
    model.eval()
    correct_nodes = total_nodes = 0
    ious = []
    loss_list = []
    for data in loader:
        data = data.to(device)
        with torch.no_grad():
            out = model(data)
            if with_labels:
                loss = F.nll_loss(out, data.y)
                loss_list.append(loss.item())

        pred = out.max(dim=1)[1]

        if with_labels:
            correct_nodes += pred.eq(data.y).sum().item()
            total_nodes += data.num_nodes
            acc = correct_nodes / total_nodes
            print(f"Acc: {acc:.4f}")

    return pred


def save_prediction(step_dir, step_name, predictions):
    """Label CAD model with predictions."""
    a_shape = LabeledShape()
    a_shape.load(step_dir, step_name)

    # Face truth file is a Pickle file containing a list object of predictions
    a_shape.face_truth = predictions.tolist()
    a_shape.shape_name = f"{step_name}_pred"
    a_shape.save(step_dir)


def main(step_name, step_dir, checkpoint_path, output_channels, with_labels=False):
    """Main code block run network model on single STEP file and save results."""
    generate_graph(step_dir, step_dir, step_name)

    list_path = os.path.join(step_dir, f"{step_name}_list")
    with open(list_path, 'wb') as handle:
        pickle.dump([f"{step_name}.graph"], handle, protocol=pickle.HIGHEST_PROTOCOL)

    test_dataset = FaceNet(step_dir, list_path)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=1)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Net(output_channels).to(device)
    load_checkpoint(checkpoint_path, model)
    pred = test(test_loader, model, device, with_labels)
    save_prediction(step_dir, step_name, pred)


if __name__ == "__main__":
    import time

    # Number of classes
    output_channels = 16

    # Name of STEP file to be tested
    step_name = "0-0-0-0-0-23"

    # Directory of STEP file
    step_dir = os.path.join("data", "test_and_save")

    # Directory of save neural network model
    checkpoint_path = os.path.join("data", "test_and_save", "best.pth.tar")

    initial_time = time.time()
    main(step_name, step_dir, checkpoint_path, output_channels)
    end_time = time.time()
    print('Total training time {:.4f}'.format(end_time - initial_time))
