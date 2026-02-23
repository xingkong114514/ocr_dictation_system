from torch import nn
import torch

from backbone import vgg
from SlidingWindow import SlidingWindow
from CTPN_RNN import CTPN_RNN

'''
1.2.3顺序连接
'''

class CTPN_FeatureExtractor(nn.Module):
    def __init__(self):
        super(CTPN_FeatureExtractor, self).__init__()
        self.vgg = vgg("myvgg")
        self.slide = SlidingWindow()
        self.rnn = CTPN_RNN()

    def forward(self, x):
        x = self.vgg(x)
        x = self.slide(x)
        x = self.rnn(x)
        return x


if __name__ == "__main__":
    model = CTPN_FeatureExtractor()
    x = torch.randn(1, 3, 640, 640)
    y = model(x)
    print(y.shape)