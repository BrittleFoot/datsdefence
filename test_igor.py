from gameloop import GameLoop


class MyLoop(GameLoop):
    def loop_body(self):
        print(self.turn)


MyLoop(is_test=True).just_run_already()
