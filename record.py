from gameloop import GameLoop


class RecordLoop(GameLoop):
    def loop_body(self):
        print(f"Recording turn {self.turn}")


RecordLoop().just_run_already()
