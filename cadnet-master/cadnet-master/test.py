import os.path as osp
import os
import pickle
import argparse
import glob

import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Dropout, Linear as Lin, ReLU, BatchNorm1d as BN
from torch_geometric.data import Data, DataLoader
from torch_geometric.utils import mean_iou
from FaceNet import FaceNet

from network import Net


def load_checkpoint(checkpoint, model):
    if not os.path.exists(checkpoint):
        raise ("File doesn't exist {}".format(checkpoint))
    checkpoint = torch.load(checkpoint, map_location='cpu')
    model.load_state_dict(checkpoint['model'])

    return checkpoint


def test(loader):
    model.eval()
    correct_nodes = total_nodes = 0
    ious = []
    loss_list = []
    for data in loader:
        data = data.to(device)
        with torch.no_grad():
            out = model(data)
            loss = F.nll_loss(out, data.y)
            loss_list.append(loss.item())
        pred = out.max(dim=1)[1]
        correct_nodes += pred.eq(data.y).sum().item()
        ious += [mean_iou(pred, data.y, output_channels, data.batch)]
        total_nodes += data.num_nodes
    acc = correct_nodes / total_nodes
    return acc, torch.cat(ious, dim=0).mean().item()


if __name__ == "__main__":
    import time

    output_channels = 16
    root = osp.join("data/graphs")
    log_path = "data"

    initial_time = time.time()
    test_dataset = FaceNet(root, osp.join(log_path, 'test_list'))
    test_loader = DataLoader(
        test_dataset, batch_size=12, shuffle=False, num_workers=6)
    print(len(test_dataset), 'testing data')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Net(16).to(device)

    load_checkpoint(osp.join(log_path, 'best.pth.tar'), model)
    acc, iou = test(test_loader)
    end_time = time.time()
    print('Total training time {:.4f}'.format(end_time - initial_time))
    print('Acc: {:.4f}, IoU: {:.4f}'.format(acc, iou))
