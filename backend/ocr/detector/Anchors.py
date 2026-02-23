
import numpy as np

'''
4.3-anchor实现
'''

def generate_anchor_heights():
    # CTPN 常用 10 个 anchor 高度
    return np.array([11, 16, 23, 33, 48, 68, 97, 139, 198, 283])

def generate_anchors(feature_h, feature_w, stride=16):
    heights = generate_anchor_heights()
    anchors = []

    for y in range(feature_h):
        for x in range(feature_w):
            cx = (x + 0.5) * stride
            cy = (y + 0.5) * stride
            for h in heights:
                anchors.append([cx, cy, stride, h])

    return np.array(anchors)  # [N, 4]
