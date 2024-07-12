from client import ApiClient


class GameLoop:
    """Наследуемся переопределяем loop"""

    def __init__(self, is_test: bool):
        self.running = False
        self.client = ApiClient("test" if is_test else "prod")

    def _start(self):
        self.running = True
        self.start()
        self._loop()

    def _stop(self):
        self.running = False
        self.stop()

    def _loop(self):
        try:
            while self.running:
                self.loop_body()
        except Exception as e:
            raise e
        except KeyboardInterrupt:
            return
        finally:
            self.stop()

    ###########################
    # RUN THIS
    def just_run_already(self):
        self._start()

    #############################################
    #### Override this methods in your class ####

    def start(self):
        pass

    def stop(self):
        pass

    def loop_body(self):
        print("Nothiing to do")
