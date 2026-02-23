from flask import Blueprint, request, jsonify

ocr_bp = Blueprint('ocr', __name__)


@ocr_bp.route('/recognize', methods=['POST'])
def recognize():
    """
    OCR 识别接口
    小程序上传图片 -> 返回识别文字
    """
    if 'image' not in request.files:
        return jsonify({
            "code": 400,
            "msg": "No image file"
        })

    image = request.files['image']

    # TODO: 调用 OCR service
    text = "示例识别文字"

    return jsonify({
        "code": 200,
        "msg": "OCR success",
        "data": {
            "text": text
        }
    })
