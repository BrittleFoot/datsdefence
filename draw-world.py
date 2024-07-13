import json
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import fire
import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer

SCREEN = (800, 800)

# Define colors (R, G, B)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

BASE = (0.0, 1.0, 1.0)
BASE_HEAD = (0.0, 0.4, 1.0)

ENEMY = (1.0, 0.0, 0.0)
ENEMY_HEAD = (1.0, 0.4, 0.0)

ZOMBIE = (0.0, 1.0, 0.0)
SPAWNER = (1.0, 1.0, 0.0)

WALL = (1.0, 1.0, 1.0)

BOX_SIZE = 1


def ga(arr, key):
    return arr.get(key) or []


@contextmanager
def window(name):
    imgui.begin(name)
    try:
        yield
    finally:
        imgui.end()


class World:
    def __init__(self, file):
        # Initialize Pygame
        self.file = file
        pygame.init()
        pygame.display.set_caption("ZOMBIEE")
        self.screen = pygame.display.set_mode(
            SCREEN, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        imgui.create_context()
        self.impl = PygameRenderer()

        self.io = imgui.get_io()
        self.io.display_size = SCREEN

        self.init_ui()

        self.loadt = 0
        self.empty = True

    def box(self, x, y):
        x = x * BOX_SIZE / SCREEN[0] * 2 * self.scale - 1
        y = y * BOX_SIZE / SCREEN[1] * 2 * self.scale - 1
        box_width = BOX_SIZE / SCREEN[0] * self.scale * 2
        box_height = BOX_SIZE / SCREEN[1] * self.scale * 2

        return x, y, box_width, box_height

    def draw(self, color, x, y):
        x, y, box_width, box_height = self.box(x, y)
        x += self.offsetX / 200
        y += self.offsetY / 200

        gl.glColor3f(*color)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x + box_width, y)
        gl.glVertex2f(x + box_width, y - box_height)
        gl.glVertex2f(x, y - box_height)
        gl.glEnd()

    def draw_line(self, color, start_x, start_y, end_x, end_y):
        start_x = start_x / SCREEN[0] * 2 * self.scale - 1
        start_y = start_y / SCREEN[1] * 2 * self.scale - 1
        end_x = end_x / SCREEN[0] * 2 * self.scale - 1
        end_y = end_y / SCREEN[1] * 2 * self.scale - 1

        start_x += self.offsetX / 200
        start_y += self.offsetY / 200
        end_x += self.offsetX / 200
        end_y += self.offsetY / 200

        gl.glColor3f(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(start_x, start_y)
        gl.glVertex2f(end_x, end_y)
        gl.glEnd()

    def get_wait(self):
        if self.empty:
            return 0.1

        if "replays/" in self.file:
            return 0.1

        return 2

    def load(self):
        wait = self.get_wait()
        if time.time() - self.loadt < wait:
            return
        self.loadt = time.time()

        snapshots = Path(self.file).read_text().strip().split("\n")

        objects = list(map(json.loads, filter(bool, snapshots)))

        if not objects:
            self.empty = True
            return

        self.worlds = {o["units"]["turn"]: o.get("world") for o in objects}
        self.turns = [o["units"] for o in objects]

        self.turns = sorted(self.turns, key=lambda x: x["turn"])
        self.tmap = {t["turn"]: t for t in self.turns}

        low = min(self.tmap.keys())
        high = max(self.tmap.keys())

        tmp = None
        for turn in range(low, high + 1):
            if turn in self.tmap:
                tmp = self.tmap[turn]
                continue

            self.tmap[turn] = tmp

        if self.realtime:
            self.tdrag = high
            self.uturn = self.tmap[high]

        if self.uturn is None:
            self.tdrag = low
            self.uturn = self.tmap[low]

        self.empty = False

    def init_ui(self):
        self.uturn = None
        self.scale = 5
        self.tdrag = None
        self.turn_id = None
        self.offsetX = 0
        self.offsetY = 0
        self.realtime = True
        self.rquest_base_center = True

    def ui(self):
        if self.empty:
            with window("Config"):
                imgui.text_ansi(f"Empty, waiting for data in {self.file}")
            return

        with window("Config"):
            chngd, self.scale = imgui.drag_float("Scale", self.scale, 0.1, 0.1, 10)
            imgui.text_ansi(f"Offset {self.offsetX}, {self.offsetY}")

            if imgui.button("Center Base") or chngd:
                self.rquest_base_center = True

        with window("Turns"):
            low = min(self.tmap.keys())
            high = max(self.tmap.keys())
            changed, self.tdrag = imgui.drag_int("Turn", self.tdrag, 1, low, high)
            self.tdrag = min(max(low, self.tdrag), high)
            if changed:
                self.realtime = self.tdrag == high

            if self.tdrag in self.tmap:
                self.uturn = self.tmap[self.tdrag]

            imgui.text_ansi(f"Turn: {self.uturn['turn']}")

            _, self.realtime = imgui.checkbox("Realtime", self.realtime)

        with window("Stats"):
            imgui.text_ansi(f"{json.dumps(self.uturn['player'], indent=2)}")

        if imgui.is_mouse_dragging(imgui.BUTTON_MOUSE_BUTTON_RIGHT):
            x, y = imgui.get_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)
            self.offsetX += x / 2
            self.offsetY -= y / 2
            imgui.reset_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)

    def map_collection(self, name, color):
        for e in ga(self.uturn, name):
            c = color
            x, y = e["x"], e["y"]
            if e.get("isHead", False):
                if color == ENEMY:
                    c = ENEMY_HEAD

                elif color == BASE:
                    c = BASE_HEAD

                    if self.rquest_base_center:
                        a, b, _, _ = self.box(x, y)
                        self.offsetX = -a * 200
                        self.offsetY = -b * 200
                        self.rquest_base_center = False

            self.draw(c, x, y)

            if last := e.get("lastAttack"):
                self.draw_line(WHITE, x, y, last["x"], last["y"])

    def map_walls(self):
        wrld = self.worlds.get(self.uturn["turn"])

        if not wrld:
            return

        for e in ga(wrld, "zpots"):
            color = SPAWNER
            if e["type"] == "wall":
                color = WALL

            x, y = e["x"], e["y"]
            self.draw(color, x, y)

    def map(self):
        if self.empty:
            return

        self.map_walls()
        self.map_collection("base", BASE)
        self.map_collection("enemyBlocks", ENEMY)
        self.map_collection("zombies", ZOMBIE)

    def run(self):
        # Main loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.impl.process_event(event)
            self.impl.process_inputs()

            imgui.new_frame()

            # Clear the screen
            gl.glClearColor(*BLACK, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.load()
            # Draw the MAP
            self.map()
            # Render the UI
            self.ui()

            imgui.render()
            self.impl.render(imgui.get_draw_data())
            pygame.display.flip()

        self.impl.shutdown()
        pygame.quit()
        sys.exit()


def draw_world(file: str):
    World(file).run()


if __name__ == "__main__":
    fire.Fire(draw_world)
