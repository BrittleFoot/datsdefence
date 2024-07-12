import json
import time
from logging import getLogger

from client import ApiClient

logger = getLogger(__name__)


class World:
    def __init__(self, client: ApiClient, test):
        self.test = test
        self.client = client
        self._static = {}
        self.update_static()
        self.units = {}

    def update_static(self):
        if self.test:
            self.world = {
                "zpots": [],
                "realmName": "Test Realm",
            }
            return

        static = self.client.world()
        for zpot in static["zpots"]:
            key = (zpot["x"], zpot["y"])

            if key in self._static:
                continue

            self._static[(zpot["x"], zpot["y"])] = zpot

        self.world = {
            "zpots": list(self._static.values()),
            "realmName": static["realmName"],
        }

    def update(self):
        if self.test:
            with open("test.json", "r") as f:
                self.units = json.load(f)
        else:
            self.units = self.client.units()

        self.units = self.units
        self.update_static()

        return self.units["turn"], self.units["turnEndsInMs"]


class GameLoop:
    """Наследуемся переопределяем loop"""

    def __init__(self, is_test=True, once=False, test=False):
        self.running = False
        self.once = once
        self.client = ApiClient("test" if is_test else "prod")

        self.turn_end_sleep_sec = 0
        self.turn = 0

        self.world = World(self.client, test)

        self.test = test
        if test:
            self.client.command = lambda x: "Its test, sending nothing to server"

    def _start(self):
        self.running = True
        self.start()
        self._loop()

    def _stop(self):
        self.running = False
        self.stop()

    def dump_world(self):
        if self.test:
            return
        realm = self.world.units.get("realmName", "")
        with open(f"info-units-{realm}.log", "a") as f:
            print(json.dumps(self.world.units), file=f)
        with open(f"info-world-{realm}.log", "a") as f:
            print(json.dumps(self.world.world), file=f)

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

                self.dump_world()
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
