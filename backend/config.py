import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
SECRET_KEY = 'ocr-dictation-secret-key'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
AUDIO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DB_HOST = '127.0.0.1'
DB_PORT = 5432
DB_NAME = 'ocr'
DB_USER = 'postgres'
DB_PASSWORD = '123456'