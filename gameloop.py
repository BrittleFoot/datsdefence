import json
import time
from logging import getLogger

from client import ApiClient

logger = getLogger(__name__)


class World:
    def __init__(self, client: ApiClient):
        self.client = client
        self.raw_static = self.client.world()
        self.raw_data = {}
        self.units = self.raw_data
        self.world = self.raw_static

    def update(self):
        self.raw_data = self.client.units()
        self.units = self.raw_data
        return self.raw_data["turn"], self.raw_data["turnEndsInMs"]


class GameLoop:
    """Наследуемся переопределяем loop"""

    def __init__(self, is_test=True, once=False):
        self.running = False
        self.once = once
        self.client = ApiClient("test" if is_test else "prod")

        self.turn_end_sleep_sec = 0
        self.turn = 0

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
                time.sleep(self.turn_end_sleep_sec)

                turn, turn_delta = self.world.update()
                if turn <= self.turn:
                    logger.info(f"Turn {turn} not changed, skipping")
                    continue
                self.turn = turn

                self.turn_end_sleep_sec = turn_delta / 1000

                with open("info.log", "w+", encoding="utf-8") as f:
                    print(json.dumps(f"{self.turn}: {self.world.units}", indent=2), file=f)

                #
                ##
                self.loop_body()
                ##
                #

                if self.once:
                    return

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
