import json
import re

dig = re.compile(r"^\d+")

with open("info.log", "r") as f, open("out.log", "w") as out:
    buffer = []

    for line in f:
        if buffer:
            buffer.append(line)
            if "}" == line.rstrip():
                j = json.loads("".join(buffer))
                j = {"units": j}
                print(json.dumps(j), file=out)
                buffer = []
            continue

        m = dig.match(line)
        if m:
            buffer.append("{\n")
