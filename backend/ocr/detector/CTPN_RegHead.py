import torch
import torch.nn as nn


'''
4.2-实现回归头
'''

class CTPN_RegHead(nn.Module):
    def __init__(self, in_channels=256, num_anchors=10):
        super(CTPN_RegHead, self).__init__()

        self.conv = nn.Conv2d(
            in_channels,
            num_anchors * 2,
            kernel_size=1
        )

    def forward(self, x):

        """
        x: [B, 256, H, W]
        return: [B, 2K, H, W]
        """

        return self.conv(x)