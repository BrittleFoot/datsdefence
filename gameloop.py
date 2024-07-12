import time

from client import ApiClient


def timestamp_ms():
    return time.perf_counter() * 1000  # milliseconds


class World:
    def __init__(self, client: ApiClient):
        self.client = client
        self.raw_static = {}
        self.raw_data = {}

    def update(self):
        self.raw_data = self.client.units()
        self.raw_static = self.client.rounds()


class GameLoop:
    """Наследуемся переопределяем loop"""

    def __init__(self, is_test: bool):
        self.running = False
        self.client = ApiClient("test" if is_test else "prod")

        self.timestamp = timestamp_ms()
        self.turn_end = self.timestamp

        self.world = World(self.client)

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
                if self.timestamp >= self.turn_end:
                    self.turn_end = self.timestamp + 1000

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
