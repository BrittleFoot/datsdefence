from pprint import pprint

from client import api_test

units = api_test.units()
pprint(units['player'])
print(len(units['base']))
print(len(units['zombies']))
