import math
from pprint import pprint

import fire

from gameloop import GameLoop


def is_in_radius(tx, ty, x, y, radius):
    return math.sqrt((tx - x) ** 2 + (ty - y) ** 2) <= radius


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


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


def priority(tc):
    coords1, t = tc

    return t["health"]


class IgorLoop(GameLoop):
    def get_attack_sequence(self):
        attacks = []

        targets = list(self.enemies.items()) + list(self.zombies.items())
        targets = sorted(targets, key=priority)

        for (bx, by), base in self.bases.items():
            is_head = base.get("isHead", False)
            dmg = PW_HEAD if is_head else PW_BODY
            rng = 8 if is_head else 5

            bx, by = base["x"], base["y"]

            for (ex, ey), enemy in targets:
                if enemy["health"] <= 0:
                    continue

                if is_in_radius(ex, ey, bx, by, rng):
                    attacks.append(attack(base["id"], ex, ey))
                    enemy["health"] -= dmg
                    print(
                        f"{bx}, {by} :Attacking {ex}, {ey} with enemy={'lastAttack' in enemy}"
                    )
                    break

        return attacks

    def parse_map(self):
        units = self.world.units
        world = self.world.world

        self.player = units["player"]

        self.bases = {
            (block["x"], block["y"]): block for block in getarr(units, "base")
        }

        for base in self.bases.values():
            if base.get("isHead"):
                self.head = base

        self.zombies = {
            (zombie["x"], zombie["y"]): zombie for zombie in getarr(units, "zombies")
        }

        self.enemies = {
            (zombie["x"], zombie["y"]): zombie for zombie in getarr(units, "enemyBlock")
        }

        self.spawners = {
            (wall["x"], wall["y"]): wall
            for wall in world.get("zpots", [])
            if wall["type"] == "default"
        }
        self.walls = {
            (wall["x"], wall["y"]): wall
            for wall in world.get("zpots", [])
            if wall["type"] == "wall"
        }

    def get_build(self):
        commands = []

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

        bases = list(self.bases.keys())
        headx, heady = self.head["x"], self.head["y"]
        bases = sorted(bases, key=lambda x: distance(x[0], x[1], headx, heady))

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
