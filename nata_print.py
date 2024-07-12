from pprint import pprint

from client import api_test

units = api_test.units()
pprint(units['player'])
print(f"блоков базы {len(units['base'])}")
print(f"зомби в радиусе видимости {len(units['zombies'])}")
print(f"враги в радиусе видимости {len(units['enemyBlocks'])}")

