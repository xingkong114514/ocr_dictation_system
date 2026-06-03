from psycopg2.extras import Json
from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection
from urllib.parse import quote
from fastspeech.synthesize_all import gen
import json
from datetime import date
import os
from fastspeech.synthesize_all import gen
custom_dictation_bp = Blueprint('custom_dictation', __name__)

@custom_dictation_bp.route('/custom_dictation', methods=['GET', 'POST'])
def custom_dictation():

    data = request.get_json()
    open_id = data.get("open_id", "")
    content = data.get("content", "")
    words = data.get("words", [])
    print("open_id:", open_id)
    print("content:", content)
    print("words:", words)
    insert_into_user_question(open_id, words)
    unit_map = {}
    for i in range(len(words)):
        unit_map[i]={
            "id": i,
            "text": words[i],
            "pinyin": pinyin(words[i]),
            "audio_url": f"https://www.u1322614.nyat.app:32476/api/wav_file/result/{quote(words[i])}.wav"
        }
        if not os.path.exists(f"./result/{words[i]}.wav"):
            gen(words[i])

    return jsonify({
        "code": 200,
        "msg": "success",
        "data":list(unit_map.values())
    })

def insert_into_user_question(open_id,content):
    conn = None
    sql = """
          INSERT INTO user_question (open_id, content, create_time)
          VALUES (%s, %s, %s) \
          """

    content = {
        "content": content
    }
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    open_id,
                    Json(content, dumps=lambda x: json.dumps(x, ensure_ascii=False)),
                    date.today()
                )
            )
        conn.commit()
        return True
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"insert_into_user_question error: {exc}")
        return False
    finally:
        if conn is not None:
            conn.close()