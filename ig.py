#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
from contextlib import contextmanager
from typing import NamedTuple

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer

import keys
from texture import get_texture_cached


@contextmanager
def window(name, **kwargs):
    imgui.begin(name, **kwargs)
    try:
        yield
    finally:
        imgui.end()


class Color(NamedTuple):
    r: float
    g: float
    b: float
    a: float


SIZE = 16
HSIZE = SIZE // 2


class Brush:
    def __init__(self, world: "DrawWorld"):
        self.draw_list = imgui.get_window_draw_list()
        self.x0, self.y0 = imgui.get_window_position()
        self.world = world

    def square(self, cx, cy, color: Color = Color(1, 1, 1, 0.8)):
        top, left = cy - HSIZE, cx - HSIZE
        bottom, right = cy + HSIZE, cx + HSIZE

        self.draw_list.add_rect_filled(
            self.x0 + self.world.scale * left,
            self.y0 + self.world.scale * top,
            self.x0 + self.world.scale * right,
            self.y0 + self.world.scale * bottom,
            imgui.get_color_u32_rgba(*color),
        )

    def image(self, cx, cy, name, color: Color = Color(1, 1, 1, 1)):
        top, left = cy - HSIZE, cx - HSIZE
        bottom, right = cy + HSIZE, cx + HSIZE

        texture = get_texture_cached(name)

        self.draw_list.add_image(
            texture.texture_id,
            (self.x0 + self.world.scale * left, self.y0 + self.world.scale * top),
            (
                self.x0 + self.world.scale * right,
                self.y0 + self.world.scale * bottom,
            ),
            col=imgui.get_color_u32_rgba(*color),
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
        pos_x, pos_y = imgui.get_window_position()

        x = (x - pos_x) / self.scale
        y = (y - pos_y) / self.scale
        return x, y

    def print_pressed_keys(self):
        """
        Print the indexes of the keys that are currently pressed

        Imgui doesn't have a way to get the keys that are currently pressed
        Manual mapping required see 'keys.py'
        """
        indexes = map(lambda a: a[0] * a[1], enumerate(self.io.keys_down))
        pressed_indexes = list(filter(bool, indexes))
        if pressed_indexes:
            print(pressed_indexes)
        return pressed_indexes

    def handle_system_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            self.impl.process_event(event)
        self.impl.process_inputs()

    def clear_render(self):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        pygame.display.flip()

    def main(self):
        while 1:
            self.handle_system_events()

            self.print_pressed_keys()

            if imgui.is_key_pressed(keys.KEY_MINUS, repeat=True):
                self.scale -= 0.1

            if imgui.is_key_pressed(keys.KEY_PLUS, repeat=True):
                self.scale += 0.1

            imgui.new_frame()

            flags = (
                imgui.WINDOW_NO_TITLE_BAR
                | imgui.WINDOW_NO_RESIZE
                | imgui.WINDOW_NO_MOVE
            )
            with window("Battlefield", flags=flags):
                brush = Brush(self)
                brush.square(100, 100, (1, 0, 0, 1))
                brush.square(0, 0, (1, 0, 0, 1))

                brush.square(149, 150, (1, 0, 0, 1))
                brush.image(150, 150, "snowman_angry")

                x, y = self.get_win_mouse_pos()
                brush.square(x, y, (1, 1, 1, 1))

            with window("Controls"):
                _, self.scale = imgui.drag_float("Scale", self.scale, 0.1, 0.1, 10)

            ###############################
            self.clear_render()


if __name__ == "__main__":
    DrawWorld().main()
