import os.path
from flask import Blueprint, jsonify, request
from database.db import get_connection
import requests
parent_bp = Blueprint('parent', __name__)
@parent_bp.route('/class', methods=['POST'])
def get_parent_class():
    data = request.get_json(silent=True) or {}
    student_name = str(data.get("student_name", "")).strip()
    if not student_name:
        return jsonify({
            "code": 400,
            "msg": "student_name不能为空"
        }), 400

    conn = None
    sql = """
          SELECT student_name, class_grade, class_no
          FROM student_class
          WHERE student_name = %s LIMIT 1 \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (student_name,))
            row = cursor.fetchone()

        if not row:
            return jsonify({
                "code": 404,
                "msg": "未查询到班级信息"
            }), 200

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": {
                "student_name": row[0],
                "class_grade": row[1],
                "class_no": row[2]
            }
        }), 200

    except Exception as exc:
        print(f"get_parent_class error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()