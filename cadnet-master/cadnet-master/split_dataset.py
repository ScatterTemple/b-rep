import os
import glob
import math
import random
import pickle


def split_dataset(split, samples):
    random.shuffle(samples)
    random.shuffle(samples)

    train_idx = int(math.ceil(split["train"] * len(samples)))
    val_idx = int(math.ceil((split["val"] * len(samples))) + train_idx)

    train_list = samples[:train_idx]
    val_list = samples[train_idx:val_idx]
    test_list = samples[val_idx:]

    return train_list, val_list, test_list


def pickle_list(split, graph_list):
    file_path = "data/" + split + "_list"

    with open(file_path, 'wb') as handle:
        pickle.dump(graph_list, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    # Parameters to set
    main_dir = "data/graphs/"
    dataset_split = {"train": 0.7, "val": 0.15, "test": 0.15}

    list_of_files = glob.glob(main_dir + "*.graph")
    graph_names = []
    for file in list_of_files:
        graph_names.append(file[len(main_dir):])

    train_samples, val_samples, test_samples = split_dataset(dataset_split, graph_names)

    pickle_list("train", train_samples)
    pickle_list("val", val_samples)
    pickle_list("test", test_samples)
