from datetime import datetime

from flask import Blueprint, jsonify, request

from database.db import get_connection



record_bp = Blueprint('record', __name__)


def format_timestamp(time_value):

    if time_value is None:
        return ""

    try:
        timestamp = int(str(time_value).strip())
        if len(str(abs(timestamp))) >= 13:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OSError, OverflowError):
        return str(time_value)


@record_bp.route('/record', methods=['GET', 'POST'])
def record_list():

    payload = request.get_json(silent=True) or {}
    open_id = payload.get('open_id') or request.args.get('open_id')
    user_name= payload.get('user_name')
    print(f"open_id:{open_id}, user_name:{user_name}")


    sql = """
        select time, result,chapter,source
        from record
        where user_name = %s
        order by time desc
    """

    conn = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_name,))
            rows = cursor.fetchall()
    except Exception as exc:
        return jsonify({
            "code": 500,
            "msg": f"database query failed: {exc}"
        }), 500
    finally:
        if conn is not None:
            conn.close()

    data = []
    for time_value, result, chapter,source in rows:
        chapter=chapter.split(".")
        grade_term=chapter[0]
        unit_id=chapter[1]
        lesson_id=chapter[2]
        if grade_term == "1+":
            grade_term = "一上"
        elif grade_term == "1-":
            grade_term = "一下"
        elif grade_term == "2+":
            grade_term = "二上"
        elif grade_term == "2-":
            grade_term = "二下"
        elif grade_term == "3+":
            grade_term = "三上"
        elif grade_term == "3-":
            grade_term = "三下"
        elif grade_term == "4+":
            grade_term = "四上"
        elif grade_term == "4-":
            grade_term ="四下"
        elif grade_term == "5+":
            grade_term = "五上"
        elif grade_term == "5-":
            grade_term = "五下"
        elif grade_term == "6+":
            grade_term = "六上"
        elif grade_term == "6-":
            grade_term = "六下"
        else:
            grade_term ="用户自定义"
        if source=="homework":
            grade_term ="教师作业"
        if source=="wrong":
            grade_term = "错词本"

        data.append({
            "time": format_timestamp(time_value),
            "result": result,
            "grade_term": grade_term,
            "unit_id": unit_id,
            "lesson_id": lesson_id,
        })

    return jsonify({
        "code": 200,
        "data": data
    })
