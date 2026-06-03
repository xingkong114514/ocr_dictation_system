
import re
import sys
import psycopg2
db_host = "127.0.0.1"
db_port = 5432
db_name = "ocr"
db_user = "postgres"
db_password = "123456"
txt_file = r"D:/ocr_dictation_system/backend/oneon_.txt"
line_re = re.compile(r"^\s*([1-6][+-])(\d+)\.(\d+)\.(\d+)\.(.+?)\s*$")

def parse_line(line: str, line_no: int):
    m = line_re.match(line)
    if not m:
        raise ValueError(f"第 {line_no} 行格式错误：{line.strip()}，应为 1+8.4.9.喝水.")
    grade_term = m.group(1)
    unit_no = int(m.group(2))
    section_no = int(m.group(3))
    word_no = int(m.group(4))
    word_text = m.group(5).strip()

    if word_text.endswith("."):
        word_text = word_text[:-1].strip()

    if not word_text:
        raise ValueError(f"第 {line_no} 行词语为空：{line.strip()}")

    return grade_term, unit_no, section_no, word_no, word_text


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            create table if not exists dictation_lesson (
              id bigserial primary key,
              grade_term varchar(2) not null
                check (grade_term ~ '^[1-6][+-]$'),
              unit_no int not null check (unit_no > 0),
              section_no int not null check (section_no > 0),
              created_at timestamptz not null default now(),
              unique (grade_term, unit_no, section_no)
            );
            """
        )
        cur.execute(
            """
            create table if not exists dictation_word (
              id bigserial primary key,
              lesson_id bigint not null references dictation_lesson(id) on delete cascade,
              word_no int not null check (word_no > 0),
              word_text text not null,
              created_at timestamptz not null default now(),
              unique (lesson_id, word_no)
            );
            """
        )
        cur.execute("create index if not exists idx_word_lesson on dictation_word(lesson_id);")
    conn.commit()


def upsert_lesson(cur, grade_term: str, unit_no: int, section_no: int):
    cur.execute(
        """
        insert into dictation_lesson(grade_term, unit_no, section_no)
        values (%s, %s, %s)
        on conflict (grade_term, unit_no, section_no)
        do update set grade_term = excluded.grade_term
        returning id;
        """,
        (grade_term, unit_no, section_no),
    )
    return cur.fetchone()[0]


def upsert_word(cur, lesson_id: int, word_no: int, word_text: str):
    cur.execute(
        """
        insert into dictation_word(lesson_id, word_no, word_text)
        values (%s, %s, %s)
        on conflict (lesson_id, word_no)
        do update set word_text = excluded.word_text;
        """,
        (lesson_id, word_no, word_text),
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

            grade_term, unit_no, section_no, word_no, word_text = parse_line(line, line_no)
            lesson_id = upsert_lesson(cur, grade_term, unit_no, section_no)
            upsert_word(cur, lesson_id, word_no, word_text)
            total += 1

    conn.commit()
    print(f"导入完成：成功 {total} 行，跳过 {skipped} 行")



def myimport(conn, file_path: str):
    with open(file_path, "r", encoding="utf-8-sig") as f, conn.cursor() as cur:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            grade_term, unit_no, section_no, word_no, word_text = parse_line(line, line_no)
            sql='''
            insert into dictation_word(lesson_id, word_no, word_text,unit_id,grade_term)
            values (%s, %s, %s,%s,%s)
            '''
            cur.execute(sql, (section_no, word_no, word_text, unit_no,grade_term))
    conn.commit()

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
        myimport(conn,txt_file)
    except Exception as e:
        print(f"导入失败：{e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
