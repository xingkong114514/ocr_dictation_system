import struct
import numpy as np

class DGRLParser:
    def __init__(self, dgrl_path):
        self.path = dgrl_path
        self.lines = []  # 存所有行的信息

    def read_int(self, f):
        return struct.unpack('<i', f.read(4))[0]

    def read_short(self, f):
        return struct.unpack('<h', f.read(2))[0]

    def read_bytes(self, f, n):
        return f.read(n)

    def parse(self):
        with open(self.path, 'rb') as f:
            # ---------- 文件头 ----------
            header_size = self.read_int(f)
            format_code = f.read(8).strip(b'\x00').decode()
            illustration = f.read(header_size - 36).decode(errors='ignore')

            code_type = f.read(20).strip(b'\x00').decode()
            code_length = self.read_short(f)
            bits_per_pixel = self.read_short(f)

            # ---------- 整页图像 ----------
            image_height = self.read_int(f)
            image_width = self.read_int(f)
            line_number = self.read_int(f)

            print(f'[INFO] {line_number} lines, image size = {image_width}x{image_height}')
            print(f'[INFO] Encoding = {code_type}, char bytes = {code_length}')

            # ---------- 行记录 ----------
            for _ in range(line_number):
                line = {}

                # 字符数
                char_number = self.read_int(f)

                # 标签
                label_bytes = f.read(code_length * char_number)
                label = self.decode_label(label_bytes, code_type, code_length)
                line['label'] = label

                # 行位置
                top = self.read_int(f)
                left = self.read_int(f)
                line['top'] = top
                line['left'] = left

                # 行尺寸
                height = self.read_int(f)
                width = self.read_int(f)
                line['height'] = height
                line['width'] = width

                # 行图像
                if bits_per_pixel == 8:
                    img_bytes = f.read(height * width)
                    bitmap = np.frombuffer(img_bytes, dtype=np.uint8)
                    bitmap = bitmap.reshape((height, width))
                else:
                    byte_width = (width + 7) // 8
                    img_bytes = f.read(height * byte_width)
                    bitmap = np.frombuffer(img_bytes, dtype=np.uint8)

                line['image'] = bitmap
                self.lines.append(line)

        return self.lines

    def decode_label(self, raw, code_type, code_length):
        # 去掉 0xFF
        raw = bytes(b for b in raw if b != 0xFF)

        try:
            if 'GB' in code_type.upper():

                return raw.decode('gbk', errors='ignore')
            elif 'ASCII' in code_type.upper():
                return raw.decode('ascii', errors='ignore')
            else:
                return raw.decode(errors='ignore')
        except:
            return ''

parser = DGRLParser('./data/HWDB2.0Train/001-P16.dgrl')
lines = parser.parse()

print(lines[0]['label'])
print(lines[0]['image'].shape)