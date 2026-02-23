from flask import Blueprint, request, jsonify

dictation_bp = Blueprint('dictation', __name__)


@dictation_bp.route('/start', methods=['POST'])
def start_dictation():
    """
    开始听写
    """
    return jsonify({
        "code": 200,
        "msg": "Dictation started"
    })


@dictation_bp.route('/submit', methods=['POST'])
def submit_dictation():
    """
    提交听写结果
    """
    return jsonify({
        "code": 200,
        "msg": "Dictation submitted"
    })
