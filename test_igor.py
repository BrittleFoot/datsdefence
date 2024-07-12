from pprint import pprint

from client import api_test
from gameloop import GameLoop

pprint(api_test.rounds())


class MyLoop(GameLoop):
    def loop_body(self):
        print("something to do")


MyLoop(is_test=True).just_run_already()
