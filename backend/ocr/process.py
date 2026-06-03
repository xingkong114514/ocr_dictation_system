import os
from ocr._ocr_ import _ocr_
import time
import shutil
import numpy as np
from PIL import Image
from glob import glob


def single_pic_proc(image_file):
    image = np.array(Image.open(image_file).convert('RGB'))
    result, image_framed = _ocr_(image)
    return result,image_framed

def entry(img_path,img_name):
    result_dir = './uploads/result'
    print("dbg1:success")
    result, image_framed = single_pic_proc(img_path)
    output_file = os.path.join(result_dir, img_name.split('/')[-1])
    txt_file = os.path.join(result_dir,img_name.split('/')[-1].split('.')[0] + '.txt')
    print(txt_file)
    txt_f = open(txt_file, 'w')
    Image.fromarray(image_framed).save(output_file)
    print("\nRecognition Result:\n")
    for key in result:
        print(result[key][1])
        txt_f.write(result[key][1] + '\n')
    txt_f.close()
