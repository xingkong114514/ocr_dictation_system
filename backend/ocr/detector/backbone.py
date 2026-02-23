import torch.nn as nn
import torch
from configparser import ConfigParser
import ast

'''
1.实现VGG特征提取
'''

class VGGBackbone(nn.Module):
    def __init__(self,features,class_num=1000,init_weights=False):
        super(VGGBackbone,self).__init__()
        self.features=features

        # CTPN 论文中，在 VGG 后接了一个 3x3 conv
        self.conv = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.relu = nn.ReLU(inplace=True)



    def forward(self,x):
        # N*3*224*224
        x=self.features(x)
        x=self.relu(self.conv(x))
        return x


    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m,nn.Conv2d):
                nn.init.xavier_uniform_(m.weight) #初始化全连接层权重
                if m.bias is not None:
                    nn.init.constant_(m.bias,0) #偏置设为0
            elif isinstance(m,nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)


def read_cfg(model_name):
    config_parser = ConfigParser()
    config_parser.read('net.cfg')
    config = config_parser['default']
    vgg_net= ast.literal_eval(config[model_name])
    # print(vgg_net)
    # print(type(vgg_net))
    return vgg_net


def make_features(cfg: list):
    layers = []
    in_channels = 3
    for v in cfg:
        if v == "M":
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        else:
            conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
            layers += [conv2d, nn.ReLU(True)]
            in_channels = v
    # print(layers)
    return nn.Sequential(*layers)

def vgg(model_name="myvgg", **kwargs):
    cfg = read_cfg(model_name)

    # print(cfg)
    model =VGGBackbone(make_features(cfg), **kwargs)
    return model


def test_feature_map_each_layer():
    vgg_model = vgg("myvgg")
    # x = torch.randn(1, 3, 224, 224)
    x = torch.randn(1, 3, 640, 640)
    print("Input:", x.shape)
    for i, layer in enumerate(vgg_model.features):
        x = layer(x)
        print(f"Layer {i:02d} ({layer.__class__.__name__}): {x.shape}")
    # [B, 512, H/16, W/16]

if __name__ == '__main__':
    test_feature_map_each_layer()
