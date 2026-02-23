import torch
import torch.nn as nn
from CTPN_FeatureExtractor import CTPN_FeatureExtractor
from CTPN_Head import CTPN_Head

'''
4.5 整个CTPN
'''
class CTPN(nn.Module):
    def __init__(self):
        super(CTPN, self).__init__()
        self.features = CTPN_FeatureExtractor()
        self.head = CTPN_Head(num_anchors=10)

    def forward(self, x):
        feat = self.features(x)
        cls, reg = self.head(feat)
        return cls, reg


if __name__ == "__main__":
    model = CTPN()
    x = torch.randn(1, 3, 640, 640)
    cls, reg = model(x)
    print(cls.shape, reg.shape)