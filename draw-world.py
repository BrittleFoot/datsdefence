import json
import sys
import time
from pathlib import Path

import fire
import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer

SCREEN = (1324, 1068)

# Define colors (R, G, B)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

BASE = (0.0, 1.0, 1.0)
BASE_HEAD = (0.0, 0.4, 1.0)

ENEMY = (1.0, 0.0, 0.0)
ENEMY_HEAD = (1.0, 0.4, 0.0)

ZOMBIE = (0.0, 1.0, 0.0)
SPAWNER = (1.0, 1.0, 0.0)

WALL = (1.0, 0.0, 1.0)

BOX_SIZE = 1


def ga(arr, key):
    return arr.get(key) or []


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

    def draw(self, color, x, y):
        x = x * BOX_SIZE / SCREEN[0] * 2 * self.scale - 1 + self.offsetX / 200
        y = y * BOX_SIZE / SCREEN[1] * 2 * self.scale - 1 + self.offsetY / 200
        box_width = BOX_SIZE / SCREEN[0] * self.scale * 2
        box_height = BOX_SIZE / SCREEN[1] * self.scale * 2

        gl.glColor3f(*color)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x + box_width, y)
        gl.glVertex2f(x + box_width, y - box_height)
        gl.glVertex2f(x, y - box_height)
        gl.glEnd()

    def get_wait(self):
        if self.empty:
            return 0.1

        if self.file.startswith("replay"):
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
        self.offsetX = 150
        self.offsetY = -150
        self.realtime = True

    def ui(self):
        if self.empty:
            imgui.begin("Config")
            imgui.text_ansi(f"Empty, waiting for data in {self.file}")
            imgui.end()
            return

        imgui.begin("Config")
        _, self.scale = imgui.drag_float("Scale", self.scale, 0.1, 0.1, 10)
        imgui.text_ansi(f"Offset {self.offsetX}, {self.offsetY}")
        if imgui.button("Reset Offset"):
            self.offsetX = 0
            self.offsetY = 0

        imgui.end()

        imgui.begin("Turns", True)

        low = min(self.tmap.keys())
        high = max(self.tmap.keys())
        changed, self.tdrag = imgui.drag_int("Turn", self.tdrag, 1, low, high)
        if changed:
            self.realtime = self.tdrag == high

        self.uturn = self.tmap[self.tdrag]

        imgui.text_ansi(f"Turn: {self.uturn['turn']}")

        _, self.realtime = imgui.checkbox("Realtime", self.realtime)

        imgui.end()

        if imgui.is_mouse_dragging(imgui.BUTTON_MOUSE_BUTTON_RIGHT):
            x, y = imgui.get_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)
            self.offsetX += x
            self.offsetY -= y
            imgui.reset_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)

    def map_collection(self, name, color):
        for e in ga(self.uturn, name):
            c = color
            if e.get("isHead", False):
                if color == ENEMY:
                    c = ENEMY_HEAD
                elif color == BASE:
                    c = BASE_HEAD

            self.draw(c, e["x"], e["y"])

    def map(self):
        if self.empty:
            return

        self.map_collection("base", BASE)
        self.map_collection("enemyBlocks", ENEMY)
        self.map_collection("zombies", ZOMBIE)
        # self.map_collection("spawners", SPAWNER)
        # self.map_collection("walls", WALL)

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
