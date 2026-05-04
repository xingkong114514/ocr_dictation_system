from flask import Blueprint, jsonify, request

from database.db import get_connection

list_bp = Blueprint('list', __name__)


@list_bp.route('/list', methods=['GET', 'POST'])
def list_texts():
    """
    返回指定年级册次下的单元、课文和每课词数。
    """
    payload = request.get_json(silent=True) or {}
    grade_term = payload.get('grade_term') or request.args.get('grade_term')
    print(grade_term)
    if grade_term =="one_up":
        grade_term = "1+"
    elif grade_term=="one_down":
        grade_term = "1-"
    elif grade_term == "two_up":
        grade_term = "2+"
    elif grade_term=="two_down":
        grade_term = "2-"
    elif grade_term=="three_up":
        grade_term = "3+"
    elif grade_term=="three_down":
        grade_term = "3-"
    elif grade_term=="four_up":
        grade_term = "4+"
    elif grade_term=="four_down":
        grade_term = "4-"
    elif grade_term=="five_up":
        grade_term = "5+"
    elif grade_term=="five_down":
        grade_term = "5-"
    elif grade_term=="six_up":
        grade_term = "6+"
    else:
        grade_term = "6-"

    print(grade_term)

    if not grade_term:
        return jsonify({
            "code": 400,
            "msg": "grade_term is required"
        }), 400

    sql = """
        select
            unit_no,
            lesson_no,
            lesson_title,
            word_count
        from course_catalog
        where grade_term = %s
        order by unit_no, lesson_no
    """
    sqltest='''
    select * from course_catalog
    '''

    conn = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (grade_term,))
            # cursor.execute(sqltest)
            rows = cursor.fetchall()
            # rows = cursor.fetchall()
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
    u_name=["第一单元","第二单元","第三单元","第四单元","第五单元","第六单元","第七单元","第八单元"]
    for unit_no, lesson_no, lesson_title, word_count in rows:
        if unit_no not in unit_map:
            unit_map[unit_no] = {
                "unit_id": f"U{unit_no}",
                "unit_no": unit_no,
                "unit_name": f"{u_name[unit_no-1]}",
                "texts": []
            }

        unit_map[unit_no]["texts"].append({
            "text_id": f"{lesson_no}",
            "lesson_no": lesson_no,
            "title": lesson_title,
            "word_count": word_count
        })

    return jsonify({
        "code": 200,
        "data": list(unit_map.values())
    })
