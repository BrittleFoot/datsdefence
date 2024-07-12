from pprint import pprint

from client import api_test
from test_igor import MyLoop


# 151
# 153
# 158 148
class NataLoop(MyLoop):
    def loop_body(self):
        command = {
            "attack": [
            ],
            "build": [
            ],
        }


        units = api_test.units()
        pprint(units)

        base_x = []
        base_y = []

        for base_block in units['base']:
            for zombie in units['zombies']:
                if base_block['x'] +5 < zombie['x'] < base_block['x'] -5 \
                        and base_block['y'] +5 < zombie['y'] < base_block['y'] -5:
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



test_loop = NataLoop()
test_loop.just_run_already()