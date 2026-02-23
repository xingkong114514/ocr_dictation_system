import cv2
import numpy as np
import torch

from PIL import Image

import matplotlib.pyplot as plt
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    # 灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 高斯滤波
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    img = cv2.cvtColor(binary, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = np.array(img)
    img = img.astype(np.float32)
    img -= np.array([123.68, 116.779, 103.939])
    # 交换HWC
    img = torch.from_numpy(img).permute(2, 0, 1)


    return img

if __name__ == '__main__':
    img=preprocess_image("../images/2.jpg")
    # img = cv2.imread("../images/2.jpg")

    plt.title("img")
    plt.imshow(img)
    plt.show()
    # cv2.imshow("1",img)
    # cv2.waitKey()
