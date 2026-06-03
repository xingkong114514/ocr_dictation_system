
import re
import sys
import psycopg2

db_host = "127.0.0.1"
db_port = 5432
db_name = "ocr"
db_user = "postgres"
db_password = "123456"
txt_file = r"D:/ocr_dictation_system/backend/course.txt"

line_re = re.compile(r"^\s*([1-6][+-])-(\d+)-(\d+)-(\d+)-(.+?)\s*$")


def parse_line(line: str, line_no: int):
    m = line_re.match(line)
    if not m:
        raise ValueError(
            f"第 {line_no} 行格式错误：{line.strip()}，应为 1+-1-2-20-金木水火土"
        )

    grade_term = m.group(1).strip()
    unit_no = int(m.group(2))
    lesson_no = int(m.group(3))
    word_count = int(m.group(4))
    lesson_title = m.group(5).strip()

    if not lesson_title:
        raise ValueError(f"第 {line_no} 行课文名称为空：{line.strip()}")

    return grade_term, unit_no, lesson_no, word_count, lesson_title


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            create table if not exists course_catalog (
              id bigserial primary key,
              grade_term varchar(2) not null
                check (grade_term ~ '^[1-6][+-]$'),
              unit_no int not null check (unit_no > 0),
              lesson_no int not null check (lesson_no > 0),
              word_count int not null default 0 check (word_count >= 0),
              lesson_title text not null,
              created_at timestamptz not null default now(),
              unique (grade_term, unit_no, lesson_no)
            );
            """
        )
    conn.commit()


def upsert_course(cur, grade_term, unit_no, lesson_no, word_count, lesson_title):
    cur.execute(
        """
        insert into course_catalog(
          grade_term,
          unit_no,
          lesson_no,
          word_count,
          lesson_title
        )
        values (%s, %s, %s, %s, %s)
        on conflict (grade_term, unit_no, lesson_no)
        do update set
          word_count = excluded.word_count,
          lesson_title = excluded.lesson_title;
        """,
        (grade_term, unit_no, lesson_no, word_count, lesson_title),
    )


def import_txt(conn, file_path: str):
    total = 0
    skipped = 0

    with open(file_path, "r", encoding="utf-8-sig") as f, conn.cursor() as cur:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()

            if not line or line.startswith("#"):
                skipped += 1
                continue

            grade_term, unit_no, lesson_no, word_count, lesson_title = parse_line(line, line_no)
            upsert_course(cur, grade_term, unit_no, lesson_no, word_count, lesson_title)
            total += 1

    conn.commit()
    print(f"导入完成：成功 {total} 行，跳过 {skipped} 行")


def main():
    conn = None
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        )
        create_table(conn)
        import_txt(conn, txt_file)
    except Exception as e:
        print(f"导入失败：{e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
