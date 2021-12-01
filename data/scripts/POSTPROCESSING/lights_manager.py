import pygame as pg
from copy import copy
from math import sqrt


class LightManager:

    def __init__(self, DISPLAY):
        # ------------ DISPLAY ------------------
        self.DISPLAY = DISPLAY
        self.W, self.H = self.DISPLAY.get_size()

        # ------------ OBJECTS -----------------
        self.objects = []

        # ----------- LAYERS -------------------
        self.opacities = {
            "night": 128,
            "day": 0,
            "inside_dark": 180,
            "inside": 50
        }
        self.colors = {
            "night": (0, 7, 20),
            "day": (255, 255, 255),
            "inside_dark": (0, 0, 0),
            "inside": (0, 0, 0)
        }
        self.main_layer = pg.Surface(self.DISPLAY.get_size(), pg.SRCALPHA)

        # -------------- LIGHT SOURCES -----------
        self.lights = []

    def init_level(self, new_level_instance):
        self.lights = []
        for obj in new_level_instance.objects:
            if hasattr(obj, "light_sources"):
                self.lights.extend(obj.light_sources)

    def update(self, current_level):
        # update current objects treatment
        self.objects = copy(current_level.objects)

        # manage lights
        for light in self.lights:
            light.update(self.main_layer, current_level.scroll)

        # blit layer
        self.DISPLAY.blit(self.main_layer, (0, 0))

        # update current layer
        self.main_layer.fill(self.colors[current_level.light_state])
        self.main_layer.set_alpha(self.opacities[current_level.light_state])


class LightSource:
    """Basically drawing a simulated light source

    DRAW HALF CIRCLES : https://stackoverflow.com/questions/41627322/drawing-semi-circles-in-pygame"""

    def __init__(self, pos: pg.Vector2, radius: int, dep_opacity: int, color: tuple[int, int, int]):
        self.radius = radius
        self.pos = pos
        self.n_circles = self.radius // 2
        self.opacity = dep_opacity
        self.color = color

    def get_alpha(self, i):

        alpha = int((sqrt(i/self.n_circles)**4)*self.opacity)
        print(alpha, end=" ")

        return alpha if alpha <= 255 else 255

    def draw_light_circle(self, screen, scroll):
        for i in range(self.n_circles):
            pg.draw.circle(screen, (self.color[0], self.color[1], self.color[2], self.get_alpha(i)),
                           self.pos - scroll, int(self.radius - self.radius * i / self.n_circles)
                           )
        print("")


    def update(self, screen, scroll):
        self.draw_light_circle(screen, scroll)
