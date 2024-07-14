import math
import time
from collections import defaultdict
from pprint import pprint

import fire

from client import ApiClient
from drawworld import DrawWorld
from gameloop import GameLoop


def is_in_radius(tx, ty, x, y, radius):
    return math.sqrt((tx - x) ** 2 + (ty - y) ** 2) <= radius


def get_distance(tx, ty, x, y, radius):
    return math.sqrt((tx - x) ** 2 + (ty - y) ** 2)


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def cross(x, y, radius=1):
    yield x - radius, y
    yield x, y - radius
    yield x + radius, y
    yield x, y + radius


def circle(x, y, radius=1):
    yield x - radius, y - radius
    yield x - radius, y
    yield x - radius, y + radius
    yield x, y - radius
    # yield x, y
    yield x, y + radius
    yield x + radius, y
    yield x + radius, y - radius
    yield x + radius, y + radius


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


SQUARE = 8


def priority(tc):
    coords1, t = tc

    return t["health"]


def enemy_priority(tc):
    coords1, t, distance = tc

    if t.get("isHead", False):
        return 0

    if t["health"] > 0:
        return distance / t["health"]

    return 100


def zombie_rebalance_priority(tc):
    coords1, enemy, dstnc = tc

    if enemy.get("type", False) == "chaos_knight":
        return 8 * enemy["health"] * dstnc

    if enemy.get("type", False) == "juggernaut":
        return 4 * enemy["health"] * dstnc

    if enemy.get("type", False) == "liner":
        return 1 * enemy["health"] * dstnc

    return 20 * enemy["health"] * dstnc


class IgorLoop(GameLoop):
    def get_attack_sequence(self):
        attacks = []

        for (bx, by), base in self.bases.items():
            is_head = base.get("isHead", False)
            dmg = PW_HEAD if is_head else PW_BODY
            rng = 8 if is_head else 5
            bx, by = base["x"], base["y"]
            ####
            key = (bx // SQUARE, by // SQUARE)
            zombie_targets = list(self.zsquares[key])
            used = {key}
            for x, y in circle(bx, by, radius=8):
                key = (x // SQUARE, y // SQUARE)
                if key in used:
                    continue
                zombie_targets.extend(self.zsquares[key])

            key = (bx // SQUARE, by // SQUARE)
            enemies = list(self.esquares[key])
            used = {key}
            for x, y in circle(bx, by, radius=8):
                key = (x // SQUARE, y // SQUARE)
                if key in used:
                    continue
                enemies.extend(self.esquares[key])

            #####
            # enemies, zombie_targets
            #####

            head_unit = self.head
            zombie_targets = [
                (
                    (ex, ey),
                    enemy,
                    get_distance(ex, ey, head_unit["x"], head_unit["y"], 1),
                )
                for (ex, ey), enemy in zombie_targets
            ]
            zombie_targets = sorted(zombie_targets, key=zombie_rebalance_priority)

            enemy_targets = enemies
            enemy_targets = [
                ((ex, ey), enemy, get_distance(ex, ey, bx, by, rng))
                for (ex, ey), enemy in enemy_targets
                if enemy["health"] > 0 and is_in_radius(ex, ey, bx, by, rng)
            ]
            enemy_targets = sorted(enemy_targets, key=enemy_priority, reverse=True)

            targets = enemy_targets + zombie_targets

            for (ex, ey), enemy, _ in targets:
                if enemy["health"] <= 0:
                    continue

                if is_in_radius(ex, ey, bx, by, rng):
                    attacks.append(attack(base["id"], ex, ey))
                    enemy["health"] -= dmg
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
            (zombie["x"], zombie["y"]): zombie
            for zombie in getarr(units, "enemyBlocks")
        }

        self.zsquares = defaultdict(list)
        for (x, y), z in self.zombies.items():
            self.zsquares[(x // SQUARE, y // SQUARE)].append(((x, y), z))

        self.esquares = defaultdict(list)
        for (x, y), e in self.enemies.items():
            self.esquares[(x // SQUARE, y // SQUARE)].append(((x, y), e))

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

                if ((x + y * 2) % 5) == 0:
                    continue

                commands.append(build(x, y))
                built.add((x, y))
                gold -= 1

                if gold == 0:
                    break

        return commands

    def start(self):
        self.ui = DrawWorld(self.relpay, self)

    def update_ui(self):
        if self.ui.realtime and self.relpay:
            self.ui.tdrag = self.world.units.get("turn", 0)

        self.ui.file = self.replay_file()
        self.ui.step()

    def stop(self):
        print("stop")
        self.ui.exit()

    def loop_body(self):
        print("srart")
        t = time.perf_counter()
        self.parse_map()
        self.ui.timers["parse_map"] = time.perf_counter() - t
        print("parsed")

        t = time.perf_counter()
        build_commands = self.get_build()
        self.ui.timers["build"] = time.perf_counter() - t
        print("builded")
        #
        t = time.perf_counter()
        attack_commands = self.get_attack_sequence()
        self.ui.timers["attack"] = time.perf_counter() - t
        print("attacked")

        commands = {
            "build": build_commands,
            "attack": attack_commands,
        }

        print(">>>>>>>>>")
        if self.move_head:
            commands["moveBase"] = self.move_head
            self.move_head = None

        print(" BUILDS:", len(commands.get("build", [])))
        print("ATTACKS:", len(commands.get("attack", [])))

        if "moveBase" in commands:
            print(f"Moving base to {commands['moveBase']}!!")

        print("<<<<<<<<<")
        execured = self.client.command(commands)
        # print("ERRORS:", len(execured.get("errors", [])))

        print("=========")


class CLI:
    def wait(self, env: str):
        try:
            while True:
                p = ApiClient(env).participate()
                pprint(p)

                wtime = p["startsInSec"]

                time.sleep(min(wtime, 5))

        except Exception as e:
            if "NOT" in str(e):
                print(e)
                return False

            if "realm" in str(e):
                print(e)
                return False

        return True

    def test(self):
        if not self.wait("test"):
            return
        IgorLoop(is_test=True).just_run_already()

    def prod(self):
        if not self.wait("prod"):
            return

        IgorLoop(is_test=False).just_run_already()

    def replay(self, file: str, interactive: bool = False):
        IgorLoop(is_test=True, replay=file, interactive=interactive).just_run_already()


if __name__ == "__main__":
    fire.Fire(CLI())
