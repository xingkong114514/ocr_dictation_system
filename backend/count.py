from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
WORDS_FILE = BASE_DIR / "onedown_.txt"
COURSE_FILE = BASE_DIR / "course_one_down.txt"


def read_lines(file_path):
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.readlines()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"failed to decode {file_path}")


def count_words_by_lesson(words_lines):
    counts = {}

    for line in words_lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split(".", 3)
        if len(parts) < 4:
            continue

        unit_id, lesson_id = parts[0], parts[1]
        key = f"{unit_id}.{lesson_id}"
        counts[key] = counts.get(key, 0) + 1

    return counts



def main():
    words_lines = read_lines(WORDS_FILE)
    course_lines = read_lines(COURSE_FILE)
    counts=0
    pre_l=1
    tmp=[]
    contents=[]
    for i in words_lines:
        i.split(".")
        unit_id = i.split(".")[0]
        lesson_id = i.split(".")[1]
        if int(lesson_id)==pre_l:
            counts+=1
        else:
            tmp.append(counts)
            counts=1
        pre_l=int(lesson_id)
    print(tmp)
    print(len(tmp))
    tmp.append(4)

    for i in range(len(course_lines)):
        grade_term=course_lines[i].split(".")[0]
        unit_id =course_lines[i].split(".")[1]
        lesson_id = course_lines[i].split(".")[2]
        title = course_lines[i].split(".")[3]
        contents.append(f"{grade_term}.{unit_id}.{lesson_id}.{tmp[i]}.{title}")
    print(contents)
    with open("course_one_down.txt", "w", encoding="utf-8") as f:
        for item in contents:
            f.write(item)


    # counts = count_words_by_lesson(words_lines)
    # updated_lines = update_course_file(course_lines, counts)
    #
    # with open(COURSE_FILE, "w", encoding="utf-8") as file:
    #     file.writelines(updated_lines)
    #
    # print("course_one_down.txt updated successfully.")


if __name__ == "__main__":
    main()
