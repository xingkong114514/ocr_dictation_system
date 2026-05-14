import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask import Blueprint
from ocr.process import entry
from database.db import get_connection
from datetime import datetime
from datetime import date
from psycopg2.extras import Json
import json
import time
app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
upload_result_bp = Blueprint('upload_result', __name__)
@upload_result_bp.route("/upload_result", methods=["GET","POST"])
def upload_result():
    source = request.form.get("source", "").strip()
    if source == "homework":
        file = request.files.get("file")
        open_id = request.form.get("openid")
        user_name = request.form.get("user_name")
        lesson_id=None
        unit_id=None
        grade_term=None
        items = request.form.get("items")
        dictation_payload = request.form.get("dictation_payload")
        custom_items = json.loads(dictation_payload)['custom_items']
        homework_id = json.loads(dictation_payload)['unit_id'].split("-")[1]
        print(f"homework_id:{homework_id},source:{source},lesson_id:{lesson_id},unit_id:{unit_id},grade_term:{grade_term},open_id:{open_id},user_name:{user_name},items:{items},dictation_payload:{dictation_payload}")
    elif source == "custom": # homework和custom都有dictation_payload
        file = request.files.get("file")
        open_id = request.form.get("openid")
        user_name = request.form.get("user_name")
        lesson_id = request.form.get("lesson_id")
        unit_id = request.form.get("unit_id")
        grade_term = request.form.get("grade_term")
        items = request.form.get("items")
        dictation_payload = request.form.get("dictation_payload")
        print(f"source:{source},lesson_id:{lesson_id},unit_id:{unit_id},grade_term:{grade_term},open_id:{open_id},user_name:{user_name},items:{items},dictation_payload:{dictation_payload}")
    else:# 课程听写 source为lesson且dictation_payload为None
        file = request.files.get("file")
        open_id = request.form.get("openid")
        user_name = request.form.get("user_name")
        lesson_id = request.form.get("lesson_id")
        unit_id = request.form.get("unit_id")
        grade_term = request.form.get("grade_term")
        items = request.form.get("items")
        dictation_payload = request.form.get("dictation_payload")
        print(f"source:{source},lesson_id:{lesson_id},unit_id:{unit_id},grade_term:{grade_term},open_id:{open_id},user_name:{user_name},items:{items},dictation_payload:{dictation_payload}")

    #dictation_payload=None
    print(dictation_payload is None)
    if source=="lesson":
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
    else:
        lesson_id = -1
        unit_id = -1
        grade_term = "None"

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
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    safe_name = f"{year}_{month}_{day}_{hour}_{minute}_{second}.jpg"

    if not safe_name:
        safe_name = "upload_image.jpg"

    save_name = f"{unit_id}_{lesson_id}_{safe_name}"
    save_path = os.path.join(UPLOAD_DIR, save_name)
    file.save(save_path)
    print(save_path)
    entry(save_path,img_name=save_name)

    if dictation_payload is None:
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
        print(unit_map)
    else:
        unit_map = {}
        custom_items = json.loads(dictation_payload)['custom_items']
        print("custom_items:",custom_items)
        for i in range(len(custom_items)):
            id=custom_items[i]["id"]
            text=custom_items[i]["text"]
            unit_map[i] = {
                "id": id,
                "text": text
            }

    with open(os.path.join("uploads","result", save_name.split(".")[0]+".txt"), "r",encoding="gbk") as f:
        content=f.readlines()
    result=compare_content_with_unit_map(content, unit_map)
    output=process(result)
    timestamp_ms = int(time.time() * 1000)
    print(timestamp_ms)
    chapter=f'{grade_term}.{unit_id}.{lesson_id}'
    if source=="homework":
        insert_into_record(timestamp_ms,open_id,user_name,output,chapter,source,homework_id)
        update_score(timestamp_ms,user_name,result,homework_id)
    else:
        insert_into_record(timestamp_ms, open_id, user_name, output, chapter,source,-1)
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

def compare_content_with_unit_map(content, unit_map):
    """
    content 中的识别结果与 unit_map 中的答案做匹配

    参数:
        content: str
            后端文字识别结果，例如 "天地你他"
        unit_map: dict
            标准答案，例如:
            {
                0: {'id': 1, 'text': '天'},
                1: {'id': 2, 'text': '地'},
                2: {'id': 3, 'text': '人'},
                3: {'id': 4, 'text': '你'},
                4: {'id': 5, 'text': '我'},
                5: {'id': 6, 'text': '他'}
            }
    返回:
        dict，包含:
        - matched_strings: 匹配成功的字符串列表
        - matched_count: 匹配成功数量
        - unmatched_strings: 匹配失败的字符串列表
        - unmatched_count: 匹配失败数量
    """

    matched_strings = []
    unmatched_strings = []

    if not isinstance(content, str):
        content = str(content)

    for _, value in unit_map.items():
        text = value.get('text', '')
        if text in content:
            matched_strings.append(text)
        else:
            unmatched_strings.append(text)

    return {
        'matched_strings': matched_strings,
        'matched_count': len(matched_strings),
        'unmatched_strings': unmatched_strings,
        'unmatched_count': len(unmatched_strings)
    }

def process(result):
    """
    将 compare_content_with_unit_map 的结果转换为:
    {
        "日": 1,
        "月": 1,
        "照": 0
    }
    其中 1 表示匹配成功，0 表示未匹配
    """
    output = {}

    for text in result.get('matched_strings', []):
        output[text] = 1

    for text in result.get('unmatched_strings', []):
        output[text] = 0

    return output

def insert_into_record(timestamp_ms, open_id, user_name,output, chapter,source,homework_id):
    """
    向 record 表插入一条记录
    参数:
        year: int
        month: int
        day: int
        open_id: str
        output: dict
            例如 {"日": 1, "月": 1, "照": 0}
        chapter: str
            例如 "1+.1.2"
    """
    conn = None
    sql = """
        INSERT INTO record (time, open_id,user_name, result, chapter,source,homework_id)
        VALUES (%s, %s,%s, %s, %s,%s,%s)
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (timestamp_ms, open_id, user_name,Json(output, dumps=lambda x: json.dumps(x, ensure_ascii=False)), chapter,source,homework_id))
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

def update_score(timestamp_ms, user_name, result, homework_id):
    count=0
    score=0
    for key, value in result.items():
        count+=1
        if value==1:
            score+=1
    score=(score/count)*100
    update_score_sql = """
                       UPDATE student_homework
                       SET score  = %s,
                           status = '已完成',
                           submitted_at=CURRENT_TIMESTAMP
                       WHERE homework_id = %s \
                         AND student_name = %s \
                       """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(update_score_sql, (score,homework_id, user_name))
        conn.commit()
        return jsonify({
            "code": 200,
            "msg": "分数更新成功"
        })
    except Exception as exc:
        conn.rollback()
        print(f"update score error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "分数更新失败"
        }), 500
    finally:
        if conn:
            conn.close()
