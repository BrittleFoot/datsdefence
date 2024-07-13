import json
import time
from logging import getLogger
from os import environ, path

from client import ApiClient

logger = getLogger(__name__)


class World:
    def __init__(self, client: ApiClient, replay):
        self.client = client
        self._static_cache = {}
        self.world = {}
        self.units = {}

        self.replay = replay
        self.replayf = None

        if replay:
            self.replayf = open(replay, "r")

    def join_static(self, a, b):
        core = {
            "realmName": a.get("realmName") or b.get("realmName"),
            "zpots": [z for z in a.get("zpots", [])],
        }

        for zpot in b.get("zpots", []):
            key = (zpot["x"], zpot["y"])

            if key in self._static_cache:
                continue

            self._static_cache[(zpot["x"], zpot["y"])] = zpot
            core["zpots"].append(zpot)

        return core

    def update(self):
        func = self.next_real
        if self.replay:
            func = self.next_replay

        self.units, self.world = func()

        return self.units["turn"], self.units["turnEndsInMs"]

    def next_real(self):
        units = self.client.units()
        world = self.client.world()
        world = self.join_static(self.world, world)

        return units, world

    def next_replay(self):
        nxt = self.replayf.readline()
        if not nxt:
            raise StopIteration("End of replay")

        snap = json.loads(nxt)

        replay_units, replay_world = snap["units"], snap.get("world", {})
        replay_world = self.join_static(self.world, replay_world)

        return replay_units, replay_world


class GameLoop:
    """Наследуемся переопределяем loop"""

    def __init__(self, is_test=True, once=False, replay: str = None):
        self.running = False
        self.once = once
        self.relpay = replay

        self.client = ApiClient("test" if is_test else "prod")

        self.turn_end_sleep_sec = 0
        self.turn = 0

        self.world = World(self.client, replay)

        if replay:
            self.client.command = (
                lambda x: "This is a replay, sending nothing to server"
            )

    def _start(self):
        self.running = True
        self.start()
        self._loop()

    def _stop(self):
        self.running = False
        self.stop()

    def dump_world(self):
        realm = self.world.units.get("realmName", "")
        uname = environ.get("USER", "denchec")
        name = f"{uname}-{realm}.ljson"

        full = path.join("data", name)
        if self.relpay:
            full = path.join("data", "replays", name)

        with open(full, "a") as f:
            print(
                json.dumps(
                    {"units": self.world.units, "world": self.world.world},
                ),
                file=f,
            )

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
                if self.relpay:
                    # Speed up replay
                    self.turn_end_sleep_sec /= 10

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
