import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask import Blueprint
from ocr.process import entry
from database.db import get_connection
app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
upload_result_bp = Blueprint('upload_result', __name__)
@upload_result_bp.route("/upload_result", methods=["GET","POST"])
def upload_result():
    file = request.files.get("file")
    lesson_id = request.form.get("lesson_id")
    unit_id = request.form.get("unit_id")
    grade_term = request.form.get("grade_term")
    if grade_term =="一上":
        grade_term = "1+"
    elif grade_term=="一下":
        grade_term = "1-"
    elif grade_term == "二上":
        grade_term = "2+"
    elif grade_term=="二下":
        grade_term = "2-"
    elif grade_term=="三上":
        grade_term = "3+"
    elif grade_term=="三下":
        grade_term = "3-"
    elif grade_term=="四上":
        grade_term = "4+"
    elif grade_term=="四下":
        grade_term = "4-"
    elif grade_term=="五上":
        grade_term = "5+"
    elif grade_term=="五下":
        grade_term = "5-"
    elif grade_term=="六上":
        grade_term = "6+"
    else:
        grade_term = "6-"
    # items=request.form.get("items")
    # print(items)

    if file is None:
        return jsonify({
            "code": 400,
            "msg": "没有接收到文件"
        }), 400

    if file.filename == "":
        return jsonify({
            "code": 400,
            "msg": "文件名为空"
        }), 400

    original_name = file.filename
    safe_name = secure_filename(original_name)

    if not safe_name:
        safe_name = "upload_image.jpg"

    save_name = f"{unit_id}_{lesson_id}_{safe_name}"
    save_path = os.path.join(UPLOAD_DIR, save_name)
    file.save(save_path)
    print(save_path)
    entry(save_path,img_name=save_name)

    sql = ''' \
          select word_no, word_text \
          from dictation_word \
          where unit_id = %s \
            and lesson_id = %s\
              and grade_term = %s\
        '''
    try:
        conn = get_connection()
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
        unit_map[i] = {
            "id": rows[i][0],
            "text": rows[i][1],
        }

    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "lesson_id": lesson_id,
            "unit_id": unit_id,
            "grade_term": grade_term,
            "original_name": original_name,
            "saved_name": save_name,
            "saved_path": save_path
        }
    })