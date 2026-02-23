from flask import Blueprint, jsonify

record_bp = Blueprint('record', __name__)


@record_bp.route('/list', methods=['GET'])
def record_list():
    """
    获取听写历史记录
    """
    return jsonify({
        "code": 200,
        "data": []
    })
