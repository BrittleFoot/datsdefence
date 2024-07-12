import math
from pprint import pprint

from client import api_test
from gameloop import GameLoop


def is_in_radius(zombie_x, zombie_y, center_x, center_y, radius=5):
    return math.sqrt(abs(zombie_x - center_x)) + math.sqrt(
        abs(zombie_y - center_y)
    ) <= math.sqrt(radius)


class IgorLoop(GameLoop):
    def loop_body(self):
        command = {
            "attack": [],
            "build": [],
        }

        units = self.world.raw_data
        pprint(units)

        base_x = []
        base_y = []

        for base_block in units["base"]:
            for zombie in units["zombies"]:
                # if base_block['x'] +5 <= zombie['x'] <= base_block['x'] -5 \
                #         and base_block['y'] +5 <= zombie['y'] <= base_block['y'] -5:
                if is_in_radius(
                    zombie["x"], zombie["y"], base_block["x"], base_block["y"]
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

            base_x.append(base_block["x"])
            base_y.append(base_block["y"])

        gold = units["player"]["gold"]

        world = self.world.world

        base = {(block["x"], block["y"]) for block in units.get("base", [])}
        zombies = {(zombie["x"], zombie["y"]) for zombie in units.get("zombies", [])}
        enemy = {(zombie["x"], zombie["y"]) for zombie in units.get("enemyBlock", [])}
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

        while gold > 0:
            for x in base_x:
                for y in base_y:
                    command["build"].append(
                        {
                            "x": x - 1,
                            "y": y,
                        }
                    )
                    command["build"].append(
                        {
                            "x": x,
                            "y": y - 1,
                        }
                    )
                    command["build"].append(
                        {
                            "x": x + 1,
                            "y": y,
                        }
                    )
                    command["build"].append(
                        {
                            "x": x,
                            "y": y + 1,
                        }
                    )
                    gold -= 4

        return
        pprint(api_test.command(command))


IgorLoop(is_test=True, once=True).just_run_already()
