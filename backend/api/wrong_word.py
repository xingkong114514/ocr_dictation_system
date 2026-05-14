import os.path
from flask import Blueprint, jsonify, request
from database.db import get_connection

wrong_word_bp = Blueprint('wrong_word', __name__)


@wrong_word_bp.route('/wrong_word', methods=['POST'])
def wrong_word():
    """
    返回指定课文听写内容
    """
    data = request.get_json(silent=True) or {}
    open_id = str(data.get("open_id", "")).strip()
    user_name = str(data.get("user_name", "")).strip()
    print(f"{open_id}, {user_name}")
    if not open_id and not user_name:
        return jsonify({
            "code": 400,
            "msg": "open_id和user_name不能同时为空"
        }), 400

    conn = None
    sql = """
          SELECT result
          FROM record
          WHERE user_name = %s
          """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_name,))
            rows = cursor.fetchall()

            word_list = []
            for row in rows:
                real_data=row[0]
                print(real_data)
                print(type(real_data))
                for key, value in real_data.items():
                    if value==0:
                        word_list.append(key)
            result = []
            for x in word_list:
                if x not in result:
                    result.append(x)

            sql='''
            insert into wrong_word (user_name,word)
                values(%s,%s)
                ON CONFLICT DO NOTHING
            '''
            for i in result:
                cursor.execute(sql, (user_name,i))
            conn.commit()
            sql = """
                  SELECT word
                  FROM wrong_word
                  WHERE user_name = %s \
                  """
            cursor.execute(sql, (user_name,))
            rows = cursor.fetchall()
            word_list = []
            for row in rows:
                word_list.append(row[0])



        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": word_list
        }), 200

    except Exception as exc:
        print(f"get_wrong_word_list error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()

@wrong_word_bp.route('/add', methods=['POST'])
def add_wrong_word():
    data = request.get_json(silent=True) or {}

    open_id = str(data.get("open_id", "")).strip()
    user_name = str(data.get("user_name", "")).strip()
    wrong_words = data.get("wrong_words") or data.get("words") or []
    print(f"{open_id}, {user_name}, {wrong_words}")
    if not open_id and not user_name:
        return jsonify({
            "code": 400,
            "msg": "open_id和user_name不能同时为空"
        }), 400

    if not isinstance(wrong_words, list) or not wrong_words:
        return jsonify({
            "code": 400,
            "msg": "wrong_words不能为空"
        }), 400

    clean_words = []
    for word in wrong_words:
        text = str(word).strip()
        if text and text not in clean_words:
            clean_words.append(text)

    if not clean_words:
        return jsonify({
            "code": 400,
            "msg": "没有可加入的词语"
        }), 400

    conn = None
    sql = """
          INSERT INTO wrong_word (user_name, word)
          VALUES (%s, %s)
              ON CONFLICT (user_name, word) DO NOTHING
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            for word in clean_words:
                cursor.execute(sql, (user_name, word))

        conn.commit()

        return jsonify({
            "code": 200,
            "msg": "加入成功",
            "data": {
                "count": len(clean_words),
                "words": clean_words
            }
        }), 200

    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"add_wrong_word error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()
