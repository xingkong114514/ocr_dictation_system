# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import os
import struct
from pathlib import Path

import cv2 as cv
import numpy as np
# from tqdm import tqdm

def turn(ar):
    ar= [hex(i) for i in ar]
    # print(ar)

def cal(ar):
    result = int.from_bytes(ar, byteorder='little')
    # print(f"十进制: {result}")
    # print(f"十六进制: 0x{result:08x}")
    return result

def turn_china(ar):
    result = []
    i = 0
    while i < len(ar) - 1:
        byte1 = ar[i]
        byte2 = ar[i + 1]

        if byte2 == 0:
            # UTF-16 LE ASCII 字符
            result.append(chr(byte1))
            i += 2
        else:
            # GB2312 汉字（两个字节）
            try:
                char = bytes([byte1, byte2]).decode('gb2312')
                result.append(char)
                i += 2
            except UnicodeDecodeError:
                # 如果解码失败，跳过（此处应该不会发生）
                i += 1


    return ''.join(result)
def read_from_dgrl(dgrl):
    if not os.path.exists(dgrl):
        print('DGRL not exis!')
        return

    dir_name, base_name = os.path.split(dgrl)
    label_dir = dir_name+'_label'
    image_dir = dir_name+'_images'
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    with open(dgrl, 'rb') as f:
        # 读取表头尺寸
        header_size = np.fromfile(f, dtype='uint8', count=4)
        # print(header_size)
        header_size = sum([j << (i*8) for i, j in enumerate(header_size)])
        print(header_size)
        temp=np.fromfile(f, dtype='uint8', count=header_size-4)
        # print(temp)
        temp=[hex(i) for i in temp]
        # print(temp)



        # 读取图像尺寸信息，提取图像中行数量
        height=np.fromfile(f, dtype='uint8', count=4)
        # turn(height)
        height=cal(height)
        print(height)


        width = np.fromfile(f, dtype='uint8', count=4)
        # turn(width)
        width=cal(width)

        print(width)

        line_num = np.fromfile(f, dtype='uint8', count=4)
        turn(line_num)
        line_num = cal(line_num)
        print('图像尺寸:\n')
        print(height, width, line_num)

        code_length=2
        # 读取每一行的信息
        for k in range(line_num):
            print(k+1)

            # 读取该行的字符数量
            char_num = np.fromfile(f, dtype='uint8', count=4)

            char_num = sum([j << (i*8) for i, j in enumerate(char_num)])
            print('字符数量:', char_num)

            # 读取该行的标注信息
            label = np.fromfile(f, dtype='uint8', count=code_length*char_num)

            label=turn_china(label)
            print('合并后：', label)

            # 读取该行的位置和尺寸
            pos_size = np.fromfile(f, dtype='uint8', count=16)
            y = cal(pos_size[:4])
            x = cal(pos_size[4:8])
            h = cal(pos_size[8:12])
            w = cal(pos_size[12:])
            print(x, y, w, h)


            # 读取该行的图片
            bitmap = np.fromfile(f, dtype='uint8', count=h*w)
            bitmap = np.array(bitmap).reshape(h, w)

            # 保存信息
            label_file = os.path.join(
                label_dir, base_name.replace('.dgrl', '_'+str(k)+'.txt'))
            with open(label_file, 'w', encoding='gb2312') as f1:
                f1.write(label)
            bitmap_file = os.path.join(
                image_dir, base_name.replace('.dgrl', '_'+str(k)+'.jpg'))
            cv.imwrite(bitmap_file, bitmap)


if __name__ == '__main__':
    # dgrl_paths = Path('./data/HWDB2.0Train').iterdir()
    # dgrl_paths = list(dgrl_paths)
    # for dgrl_path in tqdm(dgrl_paths):
    #     print(dgrl_path)
    #     read_from_dgrl(dgrl_path)
    #     break
    from datetime import datetime

    now = datetime.now()

    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    min = now.minute
    sec = now.second

    print(year, month, day, hour, min, sec)

