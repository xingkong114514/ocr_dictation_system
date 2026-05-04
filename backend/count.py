from collections import defaultdict

result = defaultdict(int)

with open("./oneon_.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split(".")
        if len(parts) < 4:
            continue

        prefix = parts[0]       # 例如 1+1
        lesson_id = parts[1]    # 课文
        word_id = parts[2]      # 词序号
        word = parts[3]         # 词语

        grade = prefix[:2]      # 1+
        unit_id = prefix[2:]    # 1

        result[(grade, unit_id, lesson_id)] += 1

for (grade, unit_id, lesson_id), count in sorted(
    result.items(),
    key=lambda x: (x[0][0], int(x[0][1]), int(x[0][2]))
):
    print(f"{unit_id}-{lesson_id}-{count}-")
