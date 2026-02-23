import torchvision
import torch
from backbone import vgg
model=vgg(model_name='vgg16')
print(model)
