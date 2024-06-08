# Module for training of the object detection model with yolov5.
# Features include tracking of training runs with mlflow.
#

from pathlib import Path
import importlib.util
#import json
import os
import ast

import yolov5
from yolov5 import YOLOv5
#from yolov5 import export  # does not work

import torch
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageDraw, ImageFont


home_dir = os.getcwd()
data_dir = home_dir + '/../data'

# Import yolo's prediction app (detect.py) manually
pred_app_path = os.path.dirname(yolov5.__file__) + '/detect.py'
pred_spec = importlib.util.spec_from_file_location('detect', pred_app_path)
detect = importlib.util.module_from_spec(pred_spec)
pred_spec.loader.exec_module(detect)

# Import yolo's training app
train_app_path = os.path.dirname(yolov5.__file__) + '/train.py'
train_spec = importlib.util.spec_from_file_location('train', train_app_path)
train = importlib.util.module_from_spec(train_spec)
train_spec.loader.exec_module(train)

# Set parameter file locations
data_yaml_path = os.path.join(data_dir, 'training/pen-parts', 'data.yaml')
cfg_path = os.path.join(data_dir, 'model/pen-parts', 'custom_yolov5s.yaml')
hyp_path = os.path.join(data_dir, 'model/pen-parts', 'hyp.yaml')
model_path = os.path.join(data_dir, 'model/pen-parts/weights', 'pen-parts.pt')
model_training_dir = os.path.join(data_dir, 'model/pen-parts')

# Do the training
train.run(
    data=data_yaml_path,
    cfg=cfg_path,
    hyp=hyp_path,
    imgsz=416,
    weights='',
    project=model_training_dir,
    name='pipeline',
    batch_size=1,
    epochs=100,
    workers=0 # DEBUG Execution failes when 'workers' is changed
)


