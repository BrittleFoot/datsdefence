import json
import sys
import time
from pathlib import Path

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer

SCREEN = (1324, 1068)

# Define colors (R, G, B)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

BASE = (0.735, 0.735, 0.735)

ENEMY = (1.0, 0.0, 0.0)
ZOMBIE = (0.0, 1.0, 0.0)
SPAWNER = (0.0, 0.0, 1.0)
WALL = WHITE

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

    def load(self):
        if time.time() - self.loadt < 2:
            return
        self.loadt = time.time()

        self.turns = list(
            map(json.loads, filter(bool, Path(self.file).read_text().split("\n")))
        )
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

    def init_ui(self):
        self.uturn = None
        self.scale = 4
        self.tdrag = None
        self.turn_id = None
        self.offsetX = 0
        self.offsetY = 0
        self.realtime = False

    def ui(self):
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
            self.draw(color, e["x"], e["y"])

    def map(self):
        units = self.uturn

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


World("out2.ljson").run()
