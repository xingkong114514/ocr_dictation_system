import os.path
from flask import Blueprint, jsonify, request
from database.db import get_connection
import requests
teacher_bp = Blueprint('teacher', __name__)
@teacher_bp.route('/classes', methods=['POST'])
def get_teacher_classes():

    data = request.get_json(silent=True) or {}
    teacher_name = str(data.get("teacher_name", "")).strip()
    if not teacher_name:
        return jsonify({
            "code": 400,
            "msg": "teacher_name不能为空"
        }), 400

    conn = None
    sql = """
          SELECT
            tc.class_grade,
            tc.class_no,
            COUNT(sc.student_name) AS student_count
        FROM teacher_class tc
        LEFT JOIN student_class sc
            ON tc.class_grade = sc.class_grade
           AND tc.class_no = sc.class_no
        WHERE tc.teacher_name = %s
        GROUP BY tc.class_grade, tc.class_no
        ORDER BY tc.class_grade, tc.class_no
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (teacher_name,))
            rows = cursor.fetchall()

        class_list = []
        for row in rows:
            class_grade = row[0]
            class_no = row[1]
            student_count = row[2]
            class_list.append({
                "teacher_name": teacher_name,
                "class_grade": class_grade,
                "class_no": class_no,
                "class_name": f"{class_grade}年级{class_no}班",
                "student_count": student_count
            })

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": class_list
        }), 200

    except Exception as exc:
        print(f"get_teacher_classes error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()
@teacher_bp.route('/class_students', methods=['POST'])
def get_class_students():
    data = request.get_json(silent=True) or {}
    class_grade = data.get("class_grade")
    class_no = data.get("class_no")

    if class_grade is None or class_no is None:
        return jsonify({
            "code": 400,
            "msg": "class_grade和class_no不能为空"
        }), 400

    conn = None
    sql = """
          SELECT sc.student_name, u.real_name, sc.class_grade, sc.class_no
        FROM student_class sc
        LEFT JOIN users u
            ON sc.student_name = u.user_name
        WHERE sc.class_grade = %s
          AND sc.class_no = %s
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (class_grade, class_no))
            rows = cursor.fetchall()

        student_list = []
        for row in rows:
            student_list.append({
                "student_name": row[0],
                "real_name": row[1],
                "class_grade": row[1],
                "class_no": row[2]
            })

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": student_list
        }), 200

    except Exception as exc:
        print(f"get_class_students error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()


@teacher_bp.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json(silent=True) or {}

    student_name = str(data.get("student_name", "")).strip()
    class_grade = data.get("class_grade")
    class_no = data.get("class_no")

    if not student_name:
        return jsonify({
            "code": 400,
            "msg": "student_name不能为空"
        }), 400

    if class_grade is None or class_no is None:
        return jsonify({
            "code": 400,
            "msg": "class_grade和class_no不能为空"
        }), 400

    conn = None
    sql = """
          INSERT INTO student_class (student_name, class_grade, class_no)
          VALUES (%s, %s, %s) \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (student_name, class_grade, class_no))
        conn.commit()

        return jsonify({
            "code": 200,
            "msg": "添加成功"
        }), 200

    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"add_student error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()

@teacher_bp.route('/add_student', methods=['POST'])
def delete_student():
    data = request.get_json(silent=True) or {}
    student_name = data.get("student_name")

    if student_name is None:
        return jsonify({
            "code": 400,
            "msg": "student_name不能为空"
        }), 400

    conn = None
    sql = """
          DELETE \
          FROM student_class
          WHERE student_name = %s \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (student_name,))
            affected_rows = cursor.rowcount
        conn.commit()

        if affected_rows == 0:
            return jsonify({
                "code": 404,
                "msg": "学生不存在"
            }), 200

        return jsonify({
            "code": 200,
            "msg": "删除成功"
        }), 200

    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"delete_student error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()

@teacher_bp.route('/join_class', methods=['POST'])
def join_class():
    data = request.get_json(silent=True) or {}

    teacher_name = str(data.get("teacher_name", "")).strip()
    class_grade = data.get("class_grade")
    class_no = data.get("class_no")

    if not teacher_name:
        return jsonify({
            "code": 400,
            "msg": "teacher_name不能为空"
        }), 400

    if class_grade is None or class_no is None:
        return jsonify({
            "code": 400,
            "msg": "class_grade和class_no不能为空"
        }), 400

    conn = None
    check_sql = """
        SELECT teacher_name
        FROM teacher_class
        WHERE teacher_name = %s AND class_grade = %s AND class_no = %s
    """
    insert_sql = """
        INSERT INTO teacher_class (teacher_name, class_grade, class_no)
        VALUES (%s, %s, %s)
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(check_sql, (teacher_name, class_grade, class_no))
            exists = cursor.fetchone()

            if exists:
                return jsonify({
                    "code": 409,
                    "msg": "该班级已加入，无需重复加入"
                }), 200

            cursor.execute(insert_sql, (teacher_name, class_grade, class_no))

        conn.commit()

        return jsonify({
            "code": 200,
            "msg": "加入班级成功"
        }), 200

    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"join_class error: {exc}")
        return jsonify({
            "code": 500,
            "msg": "服务器内部错误"
        }), 500

    finally:
        if conn is not None:
            conn.close()