# CADNet
Code for **Graph Representation of 3D CAD models for Machining Feature Recognition with Deep Learning** paper. This is an approach using graph neural networks to learning from planar B-Rep CAD models. In the paper, focus was given towards the machining feature recognition task. Here, faces in B-Rep models were classified as different machining feature classes.

The original paper can be found [here](https://asmedigitalcollection.asme.org/IDETC-CIE/proceedings-abstract/IDETC-CIE2020/84003/V11AT11A003/1090197).

MFCAD dataset can be found [here](https://github.com/hducg/MFCAD).

## Packages
- Python >= 3.8.5
- Pytorch >= 1.6.0
- Tensorboard >= 2.3.0
- Torch-geometric >= 1.6.1
- Numpy >= 1.21.2
- pythonocc-core >= 7.5.1 (https://github.com/tpaviot/pythonocc-core)

## Details on Data
- The MFCAD dataset contains a STEP file and .face_truth file for each CAD model in the dataset.
- Each B-Rep face in the STEP files are labels with an index starting from 0.
- The .face_truth file stores the ground-truth machining feature labels as a pickled Python list. The index of the list corresponds to the index given to a B-Rep face in the STEP file.
- To run the neural network, a .graph file needs generated for each CAD model. These are a pickle Python dictionary contains keys for the node features (planar equation of B-Rep face), node labels (machining feature class) and edge indexes (B-Rep face adjacency).

## Running Code
- Place STEP files and .face_truth files in /data/steps directory.
- Run `generate_graphs_from_step.py` to generate .graph files.
- Run `split_dataset.py` to split dataset into subsets, default split is 70:15:15 training/validation/testing split.
- Run `train.py` to train neural network on training subset.
- Run `test.py` to test neural network using test subset.
- To visualize CAD models with labels, run `dataset_visualizer.py`.

## Testing a Single CAD model
Once you have trained a neural network model, you can test the network on single STEP models. To do this use the following steps:
- In the `test_and_save.py` script, you need to set the `output_channels` variable, this should be the same as the network you previously trained and the number corresponds to the number of classes in your dataset.
- Set the `step_name` variable as the name of the STEP file looking to get predictions for. This is a string without the ".step" extension.
- Set the `step_dir` variable as the path to the directory where your STEP file is located.
- Set the `checkpoint_path` variable as the path for your pre-trained neural network model (i.e. "best.pth.tar").
- Once these are set, you can run `test_and_save.py`. This will generate a prediction STEP file and .face_truth Pickle file. These can then be visualized by running `dataset_vizualizer.py`.

## Citation
    @article{cadnet2020,
      Author = {Weijuan Cao, Trevor Robinson, Yang Hua, Flavien Boussage, Andrew R. Colligan, Wanbin Pan},
      Journal = {Proceedings of the ASME 2020, International Design Engineering Technical Conferences and Computers and Information in Engineering Conference},
      Title = {Graph Representation of 3D CAD models for Machining Feature Recognition with Deep Learning},
      Year = {2020}
    }
