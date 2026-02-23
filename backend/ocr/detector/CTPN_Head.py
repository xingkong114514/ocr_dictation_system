from torch import nn
import torch
from CTPN_ClsHead import CTPN_ClsHead
from CTPN_RegHead import CTPN_RegHead


'''
4.4- 整个CTPN头拼起来
'''
class CTPN_Head(nn.Module):
    def __init__(self, num_anchors=10):
        super(CTPN_Head, self).__init__()
        self.cls_head = CTPN_ClsHead(256, num_anchors)
        self.reg_head = CTPN_RegHead(256, num_anchors)

    def forward(self, x):
        """
        x: [B, 256, H, W]
        """
        cls = self.cls_head(x)
        reg = self.reg_head(x)
        return cls, reg