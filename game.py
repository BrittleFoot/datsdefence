import math
from pprint import pprint

import fire

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


def attack(blockId, x, y):
    return {
        "blockId": blockId,
        "target": {
            "x": x,
            "y": y,
        },
    }


def getarr(dict, key):
    v = dict.get(key, [])
    if v is None:
        return []
    return v


PW_HEAD = 40
PW_BODY = 10


class IgorLoop(GameLoop):
    def get_attack_sequence(self):
        attacks = []
        units = self.world.units

        for (bx, by), base in self.bases.items():
            is_head = base.get("isHead", False)
            dmg = PW_HEAD if is_head else PW_BODY

            shoot = False

            bx, by = base["x"], base["y"]

            for (ex, ey), enemy in self.enemies:
                if enemy["health"] <= 0:
                    continue

                if is_in_radius(ex, ey, bx, by):
                    attacks.append(attack(base["id"], ex, ey))
                    enemy["health"] -= dmg
                    shoot = True
                    break

            if shoot:
                continue

            for (zx, zy), zombie in self.zombies:
                if zombie["health"] <= 0:
                    continue

                if is_in_radius(zx, zy, bx, by):
                    attacks.append(attack(base["id"], ex, ey))
                    zombie["health"] -= dmg
                    shoot = True
                    break

        return attacks

    def parse_map(self):
        units = self.world.units
        world = self.world.world

        self.player = units["player"]

        self.bases = {(block["x"], block["y"]) for block in getarr(units, "base")}
        self.zombies = {
            (zombie["x"], zombie["y"]) for zombie in getarr(units, "zombies")
        }
        self.enemies = {
            (zombie["x"], zombie["y"]) for zombie in getarr(units, "enemyBlock")
        }

        self.spawners = {
            (wall["x"], wall["y"])
            for wall in world.get("zpots", [])
            if wall["type"] == "default"
        }
        self.walls = {
            (wall["x"], wall["y"])
            for wall in world.get("zpots", [])
            if wall["type"] == "wall"
        }

    def get_build(self):
        commands = []

        units = self.world.units
        print("units", units)

        gold = self.player["gold"]

        built = set()
        invalid = set()

        for e in self.bases:
            invalid.add(e)

        for x, y in self.zombies:
            invalid.add((x, y))

        for x, y in self.enemies:
            invalid.add((x, y))
            invalid |= set(circle(x, y))

        # This two following blocks could be not working

        for x, y in self.spawners:
            invalid.add((x, y))
            invalid |= set(cross(x, y))

        for x, y in self.walls:
            invalid.add((x, y))
            invalid |= set(cross(x, y))

        for x0, y0 in self.bases:
            if gold == 0:
                break

            for x, y in cross(x0, y0):
                if (x, y) in invalid or (x, y) in built:
                    print("skip", x, y)
                    continue

                commands.append(build(x, y))
                built.add((x, y))
                gold -= 1

                if gold == 0:
                    break

        return commands

    def loop_body(self):
        self.parse_map()

        build_commands = self.get_build()
        attack_commands = self.get_attack_sequence()

        commands = {
            "build": build_commands,
            "attack": attack_commands,
        }

        print(">>>>>>>>>")
        pprint(commands)

        print("<<<<<<<<<")
        pprint(self.client.command(commands))

        print("=========")


class CLI:
    def test(self):
        IgorLoop(is_test=True).just_run_already()

    def replay(self, file: str, interactive: bool = False):
        IgorLoop(is_test=True, replay=file, interactive=interactive).just_run_already()


if __name__ == "__main__":
    fire.Fire(CLI())
