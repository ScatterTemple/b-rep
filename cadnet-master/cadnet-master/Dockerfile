# Dockerfile only uses CPU for compute (for testing purposes) not CUDA for GPU acceleration
FROM continuumio/miniconda3

# Update repositories and install Calculix ccx, Graphviz and dependencies for GMSH
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /app

# Create the environment
COPY . .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "cadnet", "/bin/bash", "-c"]
