import os.path as osp
import os
import time
import numpy as np
import shutil
from torch.utils.tensorboard import SummaryWriter
import sys

sys.path.append('..')
#import logger

import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Dropout, Linear as Lin, ReLU, BatchNorm1d as BN
from torch_geometric.data import DataLoader
from torch_geometric.utils import mean_iou

from network import Net
from FaceNet import FaceNet


def save_checkpoint(state, is_best):
    filepath = osp.join(log_path, 'last.pth.tar')
    torch.save(state, filepath)
    if is_best:
        shutil.copyfile(filepath, filepath.replace('last', 'best'))


loss_train = []


def train():
    model.train()

    total_loss = correct_nodes = total_nodes = 0
    loss_list = []

    for i, data in enumerate(train_loader):
        data = data.to(device)
        optimizer.zero_grad()
        out = model(data)
        loss = F.nll_loss(out, data.y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        loss_list.append(loss.item())
        correct_nodes += out.max(dim=1)[1].eq(data.y).sum().item()
        total_nodes += data.num_nodes

        if (i + 1) % 100 == 0:
            print('[{}/{}] Loss: {:.4f}, Train Accuracy: {:.4f}'.format(
                i + 1, len(train_loader), total_loss / 100,
                correct_nodes / total_nodes
            ))
            total_loss = correct_nodes = total_nodes = 0
    loss_train.append(sum(loss_list) / len(loss_list))


loss_valid = []
best = 0


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
    loss_valid.append(sum(loss_list) / len(loss_list))
    acc = correct_nodes / total_nodes
    save_checkpoint({'model': model.state_dict()}, acc > best)
    return acc, torch.cat(ious, dim=0).mean().item()


if __name__ == "__main__":
    root = osp.join("data/graphs")
    log_path = osp.join("data")

    train_dataset = FaceNet(root, osp.join(log_path, 'train_list'))
    test_dataset = FaceNet(root, osp.join(log_path, 'val_list'))
    train_loader = DataLoader(
        train_dataset, batch_size=12, shuffle=False, num_workers=6)
    test_loader = DataLoader(
        test_dataset, batch_size=12, shuffle=False, num_workers=6)

    output_channels = 16
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Net(output_channels).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.8)

    initial_time = time.time()

    for epoch in range(1, 101):
        start = time.time()
        train()
        end = time.time()
        print('training time {:.4f}'.format(end - start))
        acc, iou = test(test_loader)
        print('Epoch: {:02d}, Acc: {:.4f}, IoU: {:.4f}'.format(epoch, acc, iou))
        scheduler.step()

    end_time = time.time()
    print('Total training time {:.4f}'.format(end_time - initial_time))
