import os.path
from flask import Blueprint, jsonify, request
from pypinyin import pinyin, lazy_pinyin, Style
from database.db import get_connection


homework_bp = Blueprint('homework', __name__)


@homework_bp.route('/create', methods=['POST'])
def create_homework():
    data = request.get_json(silent=True) or {}

    teacher_name = str(data.get("teacher_name", "")).strip()
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    homework_type = str(data.get("homework_type", "")).strip()
    deadline = data.get("deadline")
    classes = data.get("classes", [])
    print(f"teacher_name: {teacher_name},title:{title},content:{content},homework_type:{homework_type},deadline:{deadline},classes:{classes}")
    if not teacher_name:
        return jsonify({"code": 400, "msg": "teacher_name不能为空"}), 400
    if not title:
        return jsonify({"code": 400, "msg": "title不能为空"}), 400
    if not homework_type:
        return jsonify({"code": 400, "msg": "homework_type不能为空"}), 400
    if not isinstance(classes, list) or not classes:
        return jsonify({"code": 400, "msg": "classes不能为空"}), 400

    conn = None

    insert_homework_sql = """
        INSERT INTO homework (teacher_name, title, content, homework_type, deadline)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING homework_id
    """

    insert_homework_class_sql = """
        INSERT INTO homework_class (homework_id, class_grade, class_no)
        VALUES (%s, %s, %s)
    """

    find_students_sql = """
        SELECT student_name
        FROM student_class
        WHERE class_grade = %s AND class_no = %s
    """

    insert_student_homework_sql = """
        INSERT INTO student_homework (homework_id, student_name, status)
        VALUES (%s, %s, 'pending')
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                insert_homework_sql,
                (teacher_name, title, content, homework_type, deadline if deadline else None)
            )
            homework_id = cursor.fetchone()[0]

            for item in classes:
                class_grade = item.get("class_grade")
                class_no = item.get("class_no")

                if class_grade is None or class_no is None:
                    continue

                cursor.execute(
                    insert_homework_class_sql,
                    (homework_id, class_grade, class_no)
                )

                cursor.execute(find_students_sql, (class_grade, class_no))
                student_rows = cursor.fetchall()

                for row in student_rows:
                    student_name = row[0]
                    cursor.execute(
                        insert_student_homework_sql,
                        (homework_id, student_name)
                    )

        conn.commit()

        return jsonify({
            "code": 200,
            "msg": "发布成功",
            "data": {
                "homework_id": homework_id
            }
        }), 200

    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"create_homework error: {exc}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

    finally:
        if conn is not None:
            conn.close()

@homework_bp.route('/list', methods=['POST'])
def get_teacher_homework_list():
    data = request.get_json(silent=True) or {}
    teacher_name = str(data.get("teacher_name", "")).strip()

    if not teacher_name:
        return jsonify({"code": 400, "msg": "teacher_name不能为空"}), 400

    conn = None
    sql = """
        SELECT
            h.homework_id,
            h.title,
            h.content,
            h.homework_type,
            h.deadline,
            STRING_AGG(hc.class_grade::text || '年级' || hc.class_no::text || '班', ', ' ORDER BY hc.class_grade, hc.class_no) AS class_text
        FROM homework h
        LEFT JOIN homework_class hc
            ON h.homework_id = hc.homework_id
        WHERE h.teacher_name = %s
        GROUP BY h.homework_id, h.title, h.content, h.homework_type, h.deadline
        ORDER BY h.homework_id DESC
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (teacher_name,))
            rows = cursor.fetchall()

        homework_list = []
        for row in rows:
            homework_list.append({
                "homework_id": row[0],
                "title": row[1],
                "content": row[2] or "",
                "homework_type": row[3],
                "deadline": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
                "class_text": row[5] or ""
            })

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": homework_list
        }), 200

    except Exception as exc:
        print(f"get_teacher_homework_list error: {exc}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

    finally:
        if conn is not None:
            conn.close()

@homework_bp.route('/detail', methods=['POST'])
def get_homework_detail():
    data = request.get_json(silent=True) or {}
    homework_id = data.get("homework_id")

    if homework_id is None:
        return jsonify({"code": 400, "msg": "homework_id不能为空"}), 400

    conn = None
    sql = """
        SELECT
            h.homework_id,
            h.title,
            h.content,
            h.homework_type,
            h.deadline,
            STRING_AGG(hc.class_grade::text || '年级' || hc.class_no::text || '班', ', ' ORDER BY hc.class_grade, hc.class_no) AS class_text
        FROM homework h
        LEFT JOIN homework_class hc
            ON h.homework_id = hc.homework_id
        WHERE h.homework_id = %s
        GROUP BY h.homework_id, h.title, h.content, h.homework_type, h.deadline
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (homework_id,))
            row = cursor.fetchone()

        if not row:
            return jsonify({
                "code": 404,
                "msg": "作业不存在"
            }), 200

        detail = {
            "homework_id": row[0],
            "title": row[1],
            "content": row[2] or "",
            "homework_type": row[3],
            "deadline": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
            "class_text": row[5] or ""
        }

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": detail
        }), 200

    except Exception as exc:
        print(f"get_homework_detail error: {exc}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

    finally:
        if conn is not None:
            conn.close()


@homework_bp.route('/status', methods=['POST'])
def get_homework_status():
    data = request.get_json(silent=True) or {}
    homework_id = data.get("homework_id")

    if homework_id is None:
        return jsonify({"code": 400, "msg": "homework_id不能为空"}), 400

    conn = None
    sql = """
        SELECT
            sh.student_name,
            u.real_name,
            sh.status,
            sh.score,
            sh.submitted_at
        FROM student_homework sh
        LEFT JOIN users u
            ON sh.student_name = u.user_name
        WHERE sh.homework_id = %s
        ORDER BY sh.student_name
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (homework_id,))
            rows = cursor.fetchall()

        status_list = []
        for row in rows:
            status_list.append({
                "student_name": row[0],
                "real_name": row[1] if row[1] else row[0],
                "status": row[2],
                "score": row[3],
                "submitted_at": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else ""
            })

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": status_list
        }), 200

    except Exception as exc:
        print(f"get_homework_status error: {exc}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

    finally:
        if conn is not None:
            conn.close()

@homework_bp.route('/parent_list', methods=['POST'])
def get_parent_homework_list():
    data = request.get_json(silent=True) or {}
    student_name = str(data.get("student_name", "")).strip()

    if not student_name:
        return jsonify({
            "code": 400,
            "msg": "student_name不能为空"
        }), 400

    conn = None
    sql = """
        SELECT
            sh.homework_id,
            h.title,
            h.content,
            h.homework_type,
            h.deadline,
            sh.status,
            sh.score,
            sh.submitted_at
        FROM student_homework sh
        LEFT JOIN homework h
            ON sh.homework_id = h.homework_id
        WHERE sh.student_name = %s
        ORDER BY h.homework_id DESC
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (student_name,))
            rows = cursor.fetchall()

        homework_list = []
        for row in rows:
            homework_list.append({
                "homework_id": row[0],
                "title": row[1] or "",
                "content": row[2] or "",
                "homework_type": row[3] or "",
                "deadline": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
                "status": row[5] or "未完成",
                "score": row[6],
                "submitted_at": row[7].strftime("%Y-%m-%d %H:%M:%S") if row[7] else ""
            })

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": homework_list
        }), 200

    except Exception as exc:
        print(f"get_parent_homework_list error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()