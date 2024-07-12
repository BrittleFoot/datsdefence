import json
import re

dig = re.compile(r"^\d+")

with open("info1.log", "r") as f, open("out2.log", "w") as out:
    buffer = []

    for line in f:
        if buffer:
            buffer.append(line)
            if "}" == line.rstrip():
                print("".join(buffer))
                print(json.dumps(json.loads("".join(buffer))), file=out)
                buffer = []
            continue

        m = dig.match(line)
        if m:
            buffer.append("{\n")
