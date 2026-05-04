import os

from flask import Blueprint, jsonify, send_from_directory

wav_file_bp = Blueprint('wav_file', __name__)

RECORD_ROOT = r"D:\ocr_dictation_system\backend\result"


@wav_file_bp.route('/result/<path:filename>', methods=['GET'])
def get_record_file(filename):
    file_path = os.path.join(RECORD_ROOT, filename)

    if not os.path.exists(file_path):
        return jsonify({
            "code": 404,
            "msg": "file not found"
        }), 404

    return send_from_directory(RECORD_ROOT, filename)