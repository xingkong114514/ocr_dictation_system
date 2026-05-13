from database.db import get_connection


def insert_course_catalog_from_txt(file_path):
    conn = None
    sql = """
        INSERT INTO course_catalog (grade_term, unit_no, lesson_no, word_count, lesson_title)
        VALUES (%s, %s, %s, %s, %s)
    """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(".", 4)
                    if len(parts) != 5:
                        print(f"格式错误，跳过: {line}")
                        continue

                    grade_term, unit_id, lesson_id, word_count, lesson_title = parts

                    cursor.execute(
                        sql,
                        (grade_term, int(unit_id), int(lesson_id), int(word_count), lesson_title)
                    )

        conn.commit()
        print("插入完成")
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"插入失败: {exc}")
    finally:
        if conn is not None:
            conn.close()

def insert_into_dictation_word(file_path):
    conn = None
    sql = """
          INSERT INTO dictation_word (lesson_id, word_no, word_text,unit_id,grade_term)
          VALUES (%s, %s, %s,%s,%s) \
          """

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(".", 4)
                    if len(parts) != 5:
                        print(f"格式错误，跳过: {line}")
                        continue

                    grade_term,unit_id,lesson_id, word_no, word_text = parts

                    cursor.execute(
                        sql,
                        (lesson_id, int(word_no), word_text,int(unit_id),grade_term)
                    )

        conn.commit()
        print("插入完成")
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        print(f"插入失败: {exc}")
    finally:
        if conn is not None:
            conn.close()
if __name__ == '__main__':
    insert_into_dictation_word("./onedown_.txt")