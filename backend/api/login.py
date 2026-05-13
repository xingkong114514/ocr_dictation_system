import os.path

from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection
from urllib.parse import quote
from fastspeech.synthesize_all import gen
import requests
login_bp = Blueprint('login', __name__)

APPID="wx19b13196eb152c7c"
SECRET="283ae3b1ecbf3a0fd9c277edb592c516"
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    返回指定课文听写内容
    """
    data = request.get_json(silent=True) or {}
    code = data.get("code")
    print(f"code:{code}")
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": APPID,
        "secret": SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    r = requests.get(url, params=params)
    wx_data = r.json()

    openid = wx_data.get("openid", "")
    session_key = wx_data.get("session_key", "")

    if not openid:
        return jsonify({
            "code": 2,
            "msg": "wechat login failed",
            "wx_result": wx_data
        }), 500
    return jsonify({
        "code": 200,
        "msg": "success",
        "openid": openid
    })

@login_bp.route('/teacher', methods=['GET', 'POST'])
def teacher_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    role = str(data.get("role", "")).strip()
    print(f"username:{username}, password:{password}, role:{role}")
    if not username:
        return jsonify({
            "code": 400,
            "msg": "用户名不能为空"
        }), 400
    if not password:
        return jsonify({
            "code": 400,
            "msg": "密码不能为空"
        }), 400
    conn = None
    sql = """
          SELECT user_name, password,real_name
          FROM users
          WHERE user_name = %s \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql,(username,))
            user = cursor.fetchone()

        if not user:
            return jsonify({
                "code": 401,
                "msg": "用户名或密码错误"
            }), 200

        db_username = user[0]
        db_password = user[1]
        db_real_name = user[2]
        print(f"db_username:{db_username}, db_password:{db_password}")
        print(str(password) != str(db_password))
        if str(password) != str(db_password):
            return jsonify({
                "code": 401,
                "msg": "用户名或密码错误"
            }), 200

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "username": db_username,
                "role": role,
                "real_name": db_real_name
            }
        }), 200

    except Exception as exc:
        print(f"login error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()

@login_bp.route('/parent', methods=['GET', 'POST'])
def parent_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    role = str(data.get("role", "")).strip()
    print(f"username:{username}, password:{password}, role:{role}")
    if not username:
        return jsonify({
            "code": 400,
            "msg": "用户名不能为空"
        }), 400
    if not password:
        return jsonify({
            "code": 400,
            "msg": "密码不能为空"
        }), 400
    conn = None
    sql = """
          SELECT user_name, password,real_name
          FROM users
          WHERE user_name = %s \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql,(username,))
            user = cursor.fetchone()

        if not user:
            return jsonify({
                "code": 401,
                "msg": "用户名或密码错误"
            }), 200

        db_username = user[0]
        db_password = user[1]
        db_real_name = user[2]
        print(f"db_username:{db_username}, db_password:{db_password}")
        print(str(password) != str(db_password))
        if str(password) != str(db_password):
            return jsonify({
                "code": 401,
                "msg": "用户名或密码错误"
            }), 200

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "username": db_username,
                "role": role,
                "real_name": db_real_name
            }
        }), 200

    except Exception as exc:
        print(f"login error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()