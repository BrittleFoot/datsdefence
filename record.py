from pprint import pprint

from gameloop import GameLoop


class RecordLoop(GameLoop):
    def loop_body(self):
        pprint(self.units["player"])
        print(f"Recording turn {self.turn}")


RecordLoop().just_run_already()
