from pprint import pprint

from client import api_test
from gameloop import GameLoop
import math
import tkinter
# 151
# 153
# 158 148


def is_in_radius(zombie_x,zombie_y, center_x, center_y, isHead):
    if isHead:
        radius = 8
    else:
        radius = 5
    return math.sqrt(abs(zombie_x - center_x))  + math.sqrt(abs(zombie_y - center_y))  <= math.sqrt(radius)



class NataLoop(GameLoop):
    def loop_body(self):
        command = {
            "attack": [
            ],
            "build": [
            ],
        }

        units = self.world.raw_data
        # pprint(units)

        base_x = []
        base_y = []
        head = None

        for base_block in units['base']:
            base_x.append(base_block['x'])
            base_y.append(base_block['y'])

            if units['enemyBlocks']:
                for enemyBlock in units['enemyBlocks']:
                    if 'isHead' in base_block:
                        isHead = True
                        head = f"{base_block['x']},{base_block['y']}"

                    else:
                        isHead = False

                    if enemyBlock['health'] < 40 and isHead:
                        continue

                    if is_in_radius(enemyBlock['x'], enemyBlock['y'], base_block['x'], base_block['y'], isHead) and enemyBlock[
                        'health'] > 0:
                        command['attack'].append(
                            {
                                "blockId": base_block['id'],
                                "target": {
                                    "x": enemyBlock['x'],
                                    "y": enemyBlock['y'],
                                }}
                        )
                        if isHead:
                            enemyBlock['health'] = enemyBlock['health'] - 40
                        else:
                            enemyBlock['health'] = enemyBlock['health'] - 10
                        break

            if units['zombies']:
                for zombie in units['zombies']:
                    # if base_block['x'] +5 <= zombie['x'] <= base_block['x'] -5 \
                    #         and base_block['y'] +5 <= zombie['y'] <= base_block['y'] -5:
                    if 'isHead' in base_block:
                        isHead = True
                    else:
                        isHead = False

                    if zombie['health']<40 and isHead:
                        continue

                    if is_in_radius(zombie['x'], zombie['y'], base_block['x'], base_block['y'],isHead) and zombie['health']>0:
                        command['attack'].append(
                            {
                                "blockId": base_block['id'],
                                "target": {
                                    "x": zombie['x'],
                                    "y": zombie['y'],
                                }}
                        )
                        if isHead:
                            zombie['health'] = zombie['health'] - 40
                        else:
                            zombie['health'] = zombie['health'] - 10
                        break



        gold = units['player']['gold']

        while gold > 4:
            for x in base_x:
                for y in base_y:
                    command['build'].append(
                        {
                            "x": x - 1,
                            "y": y,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x,
                            "y": y - 1,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x + 1,
                            "y": y,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x,
                            "y": y + 1,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x - 1,
                            "y": y + 1 ,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x + 1 ,
                            "y": y - 1,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x + 1,
                            "y": y + 1 ,
                        }
                    )
                    command['build'].append(
                        {
                            "x": x - 1 ,
                            "y": y - 1,
                        }
                    )
                    gold -= 4
                    if gold<5:
                        break



        api_test.command(command)

        pprint(units['player'])
        print(f"блоков базы {len(units['base'])}")
        print(f"зомби в радиусе видимости {len(units['zombies'])}")
        print(f"враги в радиусе видимости {units['enemyBlocks']}")
        print(min(base_x), min(base_y))
        print(max(base_x), max(base_y))
        if head:
            print(f' головной офис у нас тут {head}')
        # print(head)
        print('====')





NataLoop(is_test=True).just_run_already()
