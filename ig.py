#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
from contextlib import contextmanager

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer


@contextmanager
def window(name, **kwargs):
    imgui.begin(name, **kwargs)
    try:
        yield
    finally:
        imgui.end()


SIZE = 8
HSIZE = SIZE // 2


SCALE = 1


class Brush:
    def __init__(self, world: "DrawWorld"):
        self.draw_list = imgui.get_window_draw_list()
        self.pos_x, self.pos_y = imgui.get_window_position()
        self.world = world

    def square(self, cx, cy, color):
        top, left = cy - HSIZE, cx - HSIZE
        bottom, right = cy + HSIZE, cx + HSIZE

        r, g, b, a = color
        self.draw_list.add_rect_filled(
            self.pos_x + self.world.scale * left,
            self.pos_y + self.world.scale * top,
            self.pos_x + self.world.scale * right,
            self.pos_y + self.world.scale * bottom,
            imgui.get_color_u32_rgba(r, g, b, a),
        )


class DrawWorld:
    def __init__(self):
        pygame.init()
        size = 1000

        pygame.display.set_mode(
            (size, size), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        imgui.create_context()
        self.impl = PygameRenderer()
        self.io = imgui.get_io()
        self.io.display_size = size, size
        #
        self.init_ui()
        #

    def init_ui(self):
        self.scale = 1

    def get_win_mouse_pos(self):
        x, y = imgui.get_mouse_pos()
        x = x - x % SIZE
        y = y - y % SIZE
        pos_x, pos_y = imgui.get_window_position()

        x = (x - pos_x) / self.scale
        y = (y - pos_y) / self.scale
        return x, y

    def main(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                self.impl.process_event(event)
            self.impl.process_inputs()

            imgui.new_frame()

            with window("Battlefield", flags=imgui.WINDOW_NO_TITLE_BAR):
                brush = Brush(self)
                brush.square(100, 100, (1, 0, 0, 1))
                brush.square(0, 0, (1, 0, 0, 1))

                x, y = self.get_win_mouse_pos()
                brush.square(x, y, (1, 1, 1, 1))

            with window("Controls"):
                _, self.scale = imgui.drag_float("Scale", self.scale, 0.1, 0.1, 10)

            ###############################
            gl.glClearColor(0, 0, 0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            self.impl.render(imgui.get_draw_data())

            pygame.display.flip()


if __name__ == "__main__":
    DrawWorld().main()
