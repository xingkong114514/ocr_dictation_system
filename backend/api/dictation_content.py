import os.path

from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection
from urllib.parse import quote
from fastspeech.synthesize_all import gen

dictation_content_bp = Blueprint('dictation_content', __name__)


@dictation_content_bp.route('/dictation_content', methods=['GET', 'POST'])
def get_dictation_content():
    """
    返回指定课文听写内容
    """
    payload = request.get_json(silent=True) or {}
    unit_id=payload.get('unit_id') or request.args.get('unit_id')
    lesson_id=payload.get('lesson_id') or request.args.get('lesson_id')
    print(unit_id,lesson_id)
    sql='''
    select word_no, word_text from dictation_word where unit_id=%s and lesson_id=%s
    '''
    try:
        conn=get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (unit_id, lesson_id))
            rows = cursor.fetchall()
            print(rows)
    except Exception as exc:
        return jsonify({
            "code": 500,
            "msg": f"database query failed: {exc}"
        }), 500
    finally:
        if conn is not None:
            conn.close()

    unit_map = {}
    for i in range(len(rows)):
        unit_map[i]={
            "id": rows[i][0],
            "id": rows[i][0],
            "text": rows[i][1],
            "pinyin": pinyin(rows[i][1]),
            "audio_url": f"https://www.u1322614.nyat.app:32476/api/wav_file/result/{quote(rows[i][1])}.wav"
        }
        if not os.path.exists(f"./result/{rows[i][1]}.wav"):
            gen(rows[i][1])
    print(list(unit_map.values()))
    return jsonify({
        "code": 200,
        "data": list(unit_map.values())
    })
