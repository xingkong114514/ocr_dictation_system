import os.path

from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection
register_bp = Blueprint('register', __name__)

APPID="wx19b13196eb152c7c"
SECRET="283ae3b1ecbf3a0fd9c277edb592c516"
@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    0:admin
    1:teacher
    2:student
    """
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    real_name = str(data.get("real_name", "")).strip()
    role=str(data.get("role", "")).strip()
    if role=="teacher":
        role=1
    else:
        role=2
    insert_into_users(username, password, real_name, role)
    return jsonify({
        "code": 200,
        "msg": "success"
    })

def insert_into_users(username, password, real_name, role):
    conn = None
    sql = """
        INSERT INTO USERS (user_name, password, real_name, role)
        VALUES (%s, %s, %s, %s)
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (username, password, real_name, role))
        conn.commit()
        return True
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"insert_into_record error: {exc}")
        return False
    finally:
        if conn is not None:
            conn.close()