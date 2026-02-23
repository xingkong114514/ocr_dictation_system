import torch
import torch.nn as nn

'''
2.生成3*3滑窗
'''

class SlidingWindow(nn.Module):
    def __init__(self, in_channels=512, out_channels=512):
        super(SlidingWindow, self).__init__()

        # 3×3 滑窗，本质是 3×3 卷积
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            padding=1
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        """
        x: [B, 512, H, W]
        """
        x = self.relu(self.conv(x))
        return x
