#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
from collections import defaultdict
from contextlib import contextmanager

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer

from itypes import Color, Vec2
from texture import get_texture_cached


@contextmanager
def window(name, **kwargs):
    imgui.begin(name, **kwargs)
    try:
        yield
    finally:
        imgui.end()


SIZE = 16
HSIZE = SIZE // 2


def snap(vec):
    return ((Vec2(*vec) + HSIZE) // SIZE) * SIZE


def ongrid(grid_coords):
    return Vec2(*grid_coords) * SIZE


class Brush:
    def __init__(self, world: "DrawWorld"):
        self.draw_list = imgui.get_window_draw_list()
        self.x0, self.y0 = imgui.get_window_position()
        self.zero = Vec2(self.x0, self.y0)
        self.world = world

    def square(self, center, color: Color = Color(1, 1, 1, 0.8)):
        a = center - self.world.size / 2
        b = center + self.world.size / 2

        self.draw_list.add_rect_filled(
            *(self.zero + a),
            *(self.zero + b),
            imgui.get_color_u32_rgba(*color),
        )

    def image(
        self,
        center,
        name,
        color: Color = Color(1, 1, 1, 1),
        offset_percent=Vec2(0, 0),
        scale_percent=Vec2(1, 1),
    ):
        size = scale_percent * self.world.size
        a = Vec2(*center) - size / 2 + offset_percent * size
        b = Vec2(*center) + size / 2 + offset_percent * size

        texture = get_texture_cached(name)

        start = self.zero + a
        end = self.zero + b

        self.draw_list.add_image(
            texture.texture_id,
            tuple(start),
            tuple(end),
            col=imgui.get_color_u32_rgba(*color),
        )


key_handlers = defaultdict(list)


def key_handler(key, mod=0):
    def decorator(func):
        key_handlers[(key, mod)].append(func)
        return func

    return decorator


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
        self.scale_speed = 0.1
        self.scale_max = 10

        self.scale = 2
        self.offset = Vec2(0, 0)

        self.window_pos = Vec2(0, 0)
        self.window_size = Vec2(0, 0)
        self.window_mouse_pos = Vec2(0, 0)

    @property
    def vscale(self):
        return Vec2(self.scale, self.scale)

    @property
    def size(self):
        return SIZE * self.scale

    @property
    def soffset(self):
        """Scaled offset"""
        return self.offset * self.scale

    def get_win_mouse_pos(self):
        mouse = Vec2(*imgui.get_mouse_pos())
        zero = Vec2(*imgui.get_window_position())

        return mouse - zero

    def handle_system_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                key = (event.key, event.mod)
                if key in key_handlers:
                    for handler in key_handlers[key]:
                        handler(self)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.zoom_wheel(event)

            self.impl.process_event(event)
        self.impl.process_inputs()

    def clear_render(self):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        pygame.display.flip()

    def zoom_wheel(self, event):
        if event.button == pygame.BUTTON_WHEELDOWN:
            self.zoom_out()
        if event.button == pygame.BUTTON_WHEELUP:
            self.zoom_in()

    @key_handler(pygame.K_MINUS)
    def zoom_out(self):
        if self.scale < self.scale_speed * 2:
            return

        return self.zoom(-self.scale_speed * self.scale / 2)

    @key_handler(pygame.K_EQUALS)
    def zoom_in(self):
        if self.scale >= self.scale_max:
            return

        return self.zoom(self.scale_speed * self.scale / 2)

    def zoom(self, speed):
        self.scale = max(self.scale_speed, min(self.scale_max, self.scale + speed))

        mouse = self.window_mouse_pos - self.window_pos
        self.offset = self.offset + mouse * (1 / self.scale - 1 / (self.scale - speed))

    def snap(self, vec):
        offset_snap = (self.soffset) % self.size
        centered_vec = Vec2(*vec) + self.size / 2 - offset_snap
        return (centered_vec // self.size) * self.size + offset_snap

    def fromgrid(self, grid_coords):
        return Vec2(*grid_coords) * self.size + self.soffset

    def main(self):
        while 1:
            self.handle_system_events()

            imgui.new_frame()

            if imgui.is_mouse_dragging(imgui.BUTTON_MOUSE_BUTTON_RIGHT):
                x, y = imgui.get_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)
                self.offset = self.offset + Vec2(x, y) * (1 / self.scale)
                imgui.reset_mouse_drag_delta(imgui.BUTTON_MOUSE_BUTTON_RIGHT)

            flags = (
                imgui.WINDOW_NO_TITLE_BAR
                # | imgui.WINDOW_NO_RESIZE
                | imgui.WINDOW_NO_MOVE
            )
            with window("Battlefield", flags=flags):
                self.window_pos = Vec2(*imgui.get_window_position())
                self.window_size = Vec2(*imgui.get_window_size())
                self.window_mouse_pos = Vec2(*imgui.get_mouse_pos())

                brush = Brush(self)
                brush.square(self.fromgrid((0, 0)), (1, 0, 0, 1))
                brush.square(self.fromgrid((1, 1)), (1, 0, 0, 1))
                brush.square(self.fromgrid((2, 2)), (1, 0, 0, 1))

                brush.image(self.fromgrid((5, 5)), "snowman_happy")
                brush.image(self.fromgrid((5, 6)), "snowman_angry")

                x, y = self.get_win_mouse_pos()

                cursor_params = {
                    "name": "cursor",
                    "offset_percent": Vec2(0.5, 0.5),
                    "scale_percent": Vec2(2, 2),
                }
                brush.image(Vec2(x, y), color=(1, 1, 1, 0.1), **cursor_params)
                brush.square(self.snap((x, y)), (0.3, 0.4, 0.9, 0.15))
                brush.image(self.snap((x, y)), **cursor_params)

            with window("Controls"):
                _, self.scale = imgui.drag_float("Scale", self.scale, 0.1, 0.1, 10)
                imgui.same_line()
                if imgui.button("Reset Scale"):
                    self.scale = 2

                imgui.text_ansi(f"Offset: {self.offset}")
                imgui.text_ansi(f"Snap: {(self.soffset) % self.size}")
                imgui.same_line()
                if imgui.button("Reset Offset"):
                    self.offset = Vec2(0, 0)

            ###############################
            self.clear_render()


if __name__ == "__main__":
    DrawWorld().main()
