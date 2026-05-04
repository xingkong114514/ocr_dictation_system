import psycopg2
from db import get_connection

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
conn = None
grade_term="1+"
conn = get_connection()
with conn.cursor() as cursor:
    cursor.execute(sql, (grade_term,))
    rows = cursor.fetchall()
print(rows)