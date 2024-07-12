from pprint import pprint

from client import api_test
from test_igor import MyLoop
import math
import tkinter
# 151
# 153
# 158 148
command = {
            "attack": [
            ],
            "build": [
            ],
        }

def is_in_radius(zombie_x,zombie_y, center_x, center_y, radius=5):
    return math.sqrt(zombie_x - center_x)  + math.sqrt(zombie_y - center_y)  <= math.sqrt(radius)


units = api_test.units()
pprint(units)

base_x = []
base_y = []

for base_block in units['base']:
    for zombie in units['zombies']:
        # if base_block['x'] +5 <= zombie['x'] <= base_block['x'] -5 \
        #         and base_block['y'] +5 <= zombie['y'] <= base_block['y'] -5:
        if is_in_radius(zombie['x'] , zombie['y'], base_block['x'], base_block['y']):
            command['attack'].append(
            {
                "blockId": base_block['id'],
                "target": {
                    "x": zombie['x'],
                    "y": zombie['y'],
                }}
        )

    base_x.append(base_block['x'])
    base_y.append(base_block['y'])



for i in range(units['player']['gold']):
    for x in base_x:
        for y in base_y:
            command['build'].append(
                {
                    "x": x-1,
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

pprint(api_test.command(command))