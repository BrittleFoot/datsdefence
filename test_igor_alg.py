import math
from pprint import pprint

from gameloop import GameLoop


def is_in_radius(zombie_x, zombie_y, center_x, center_y, radius=5):
    return math.sqrt(abs(zombie_x - center_x)) + math.sqrt(
        abs(zombie_y - center_y)
    ) <= math.sqrt(radius)


def cross(x, y):
    yield x - 1, y
    yield x, y - 1
    yield x + 1, y
    yield x, y + 1


def circle(x, y):
    yield x - 1, y - 1
    yield x - 1, y
    yield x - 1, y + 1
    yield x, y - 1
    # yield x, y
    yield x, y + 1
    yield x + 1, y
    yield x + 1, y - 1
    yield x + 1, y + 1


def build(x, y):
    return {
        "x": x,
        "y": y,
    }


def getarr(dict, key):
    v = dict.get(key, [])
    if v is None:
        return []
    return v


class IgorLoop(GameLoop):
    def loop_body(self):
        command = {
            "attack": [],
            "build": [],
        }

        units = self.world.raw_data
        # pprint(units)

        base_x = []
        base_y = []

        for base_block in getarr(units, "base"):
            for zombie in getarr(units, "zombies"):
                # if base_block['x'] +5 <= zombie['x'] <= base_block['x'] -5 \
                #         and base_block['y'] +5 <= zombie['y'] <= base_block['y'] -5:
                if "isHead" in base_block:
                    isHead = True
                else:
                    isHead = False

                if zombie["health"] < 40 and isHead:
                    continue

                if (
                    is_in_radius(
                        zombie["x"],
                        zombie["y"],
                        base_block["x"],
                        base_block["y"],
                        isHead,
                    )
                    and zombie["health"] > 0
                ):
                    command["attack"].append(
                        {
                            "blockId": base_block["id"],
                            "target": {
                                "x": zombie["x"],
                                "y": zombie["y"],
                            },
                        }
                    )
                    if isHead:
                        zombie["health"] = zombie["health"] - 40
                    else:
                        zombie["health"] = zombie["health"] - 10
                    break

            base_x.append(base_block["x"])
            base_y.append(base_block["y"])

        build_commands = get_build(self)

        commands = {
            "build": build_commands,
            "attack": command["attack"],
        }

        print(">>>>>>>>>")
        pprint(commands)

        print("<<<<<<<<<")
        pprint(self.client.command())

        print("=========")


def get_build(self: GameLoop):
    commands = []

    units = self.world.units
    world = self.world.world

    gold = units["player"]["gold"]

    bases = {(block["x"], block["y"]) for block in getarr(units, "base")}
    zombies = {(zombie["x"], zombie["y"]) for zombie in getarr(units, "zombies")}
    enemy = {(zombie["x"], zombie["y"]) for zombie in getarr(units, "enemyBlock")}

    spawner = {
        (wall["x"], wall["y"])
        for wall in world.get("zpots", [])
        if wall["type"] == "default"
    }
    walls = {
        (wall["x"], wall["y"])
        for wall in world.get("zpots", [])
        if wall["type"] == "wall"
    }

    built = set()
    invalid = set()

    for e in bases:
        invalid.add(e)

    for x, y in zombies:
        invalid.add((x, y))

    for x, y in enemy:
        invalid.add((x, y))
        invalid |= set(circle(x, y))

    for x, y in spawner:
        invalid.add((x, y))
        invalid |= set(cross(x, y))

    for x, y in walls:
        invalid.add((x, y))
        invalid |= set(cross(x, y))

    for x0, y0 in bases:
        if gold == 0:
            break

        for x, y in cross(x0, y0):
            if (x, y) in invalid or (x, y) in built:
                continue

            commands.append(build(x, y))
            built.add((x, y))
            gold -= 1

            if gold == 0:
                break


IgorLoop(is_test=True).just_run_already()