from pprint import pprint

from client import api_test


command = {
"attack": [
],
"build": [
],
}
# pprint(api_test.rounds())


# pprint(api_test.world())

units = api_test.units()
pprint(units)

for item in units['base']:
    command['attack'].append(
        {
            "blockId": item['id'],
            "target": {
                "x": item['zombies'][0]['x'],
                "y": item['zombies'][0]['x'],
            }}
    )


# ≈

pprint(api_test.command(command))