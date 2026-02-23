import os

# 根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask 基础配置
DEBUG = True
SECRET_KEY = 'ocr-dictation-secret-key'

# 上传文件
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
AUDIO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')

# 图片类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# PostgreSQL
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'dictation_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'