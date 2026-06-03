import os.path

from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection
from urllib.parse import quote
from fastspeech.synthesize_all import gen

dictation_content_bp = Blueprint('dictation_content', __name__)


@dictation_content_bp.route('/dictation_content', methods=['GET', 'POST'])
def get_dictation_content():

    payload = request.get_json(silent=True) or {}
    unit_id=payload.get('unit_id') or request.args.get('unit_id')
    lesson_id=payload.get('lesson_id') or request.args.get('lesson_id')
    grade_term=payload.get('grade_term') or request.args.get('grade_term')
    if grade_term == "一上":
        grade_term = "1+"
    elif grade_term == "一下":
        grade_term = "1-"
    elif grade_term == "二上":
        grade_term = "2+"
    elif grade_term == "二下":
        grade_term = "2-"
    elif grade_term == "三上":
        grade_term = "3+"
    elif grade_term == "三下":
        grade_term = "3-"
    elif grade_term == "四上":
        grade_term = "4+"
    elif grade_term == "四下":
        grade_term = "4-"
    elif grade_term == "五上":
        grade_term = "5+"
    elif grade_term == "五下":
        grade_term = "5-"
    elif grade_term == "六上":
        grade_term = "6+"
    else:
        grade_term = "6-"
    print(unit_id,lesson_id)
    sql='''
    select word_no, word_text from dictation_word where unit_id=%s and lesson_id=%s and grade_term=%s
    '''
    try:
        conn=get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (unit_id, lesson_id,grade_term))
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
