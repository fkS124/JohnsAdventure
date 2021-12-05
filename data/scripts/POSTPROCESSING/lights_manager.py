import pygame as pg
from copy import copy
from math import sqrt, cos, radians, sin
from pygame.gfxdraw import filled_polygon


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
            "inside_dark": 100,
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
        self.light_state = ""

    def init_level(self, new_level_instance):
        self.lights = []
        for obj in new_level_instance.objects:
            if hasattr(obj, "light_sources"):
                self.lights.extend(obj.light_sources)
        print(self.lights)
        self.light_state = new_level_instance.light_state

    def update(self, current_level):
        # update current objects treatment
        self.objects = copy(current_level.objects)

        # manage lights
        for light in self.lights:
            light.update(self.DISPLAY, current_level.scroll, self.main_layer)

        # blit layer
        self.DISPLAY.blit(self.main_layer, (0, 0))

        # update current layer
        self.main_layer.fill(self.colors[current_level.light_state])
        self.main_layer.set_alpha(self.opacities[current_level.light_state])


class LightSource:
    """Basically drawing a simulated light source"""

    def __init__(self, pos: pg.Vector2, radius: int, dep_opacity: int, color: tuple[int, int, int]):
        self.surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        self.radius = radius
        self.pos = pos
        self.n_circles = self.radius // 2
        self.opacity = dep_opacity
        self.color = color
        self.inside_pos = [self.radius, self.radius]

        self.draw_light_circle()

    def get_alpha(self, i):
        # function calculated to manage the growth of alpha -> f(x) = sqrt(x/n_circles)^4 * final_opacity
        alpha = int((sqrt(i/self.n_circles)**4)*self.opacity)
        return alpha if alpha <= 255 else 255

    def draw_light_circle(self):
        for i in range(self.n_circles):
            pg.draw.circle(self.surface, (self.color[0], self.color[1], self.color[2], self.get_alpha(i)),
                           self.inside_pos, int(self.radius - self.radius * i / self.n_circles)
                           )

    def update(self, screen, scroll, LAYER):

        screen.blit(self.surface, self.pos-pg.Vector2(self.radius, self.radius)-scroll)
        pg.draw.circle(LAYER, (0, 0, 0, 0), self.pos-scroll, self.radius)


class PolygonLight:

    def __init__(self,
                 origin: pg.Vector2,
                 height: int,
                 radius: int,
                 dep_angle: int,  # degrees
                 end_angle: int,  # degrees
                 color: tuple[int, int, int],
                 dep_alpha: int
                 ):

        self.pos = origin - pg.Vector2(radius, radius)
        self.origin = origin
        self.height = height
        self.radius = radius
        self.color = color
        self.opacity = dep_alpha
        self.dep_angle = dep_angle
        self.end_angle = end_angle
        self.step = 2
        self.n_circles = self.radius // self.step

        self.surface = pg.Surface((self.radius*2, self.radius*2), pg.SRCALPHA)
        self.start_point = pg.Vector2((self.radius, self.radius))
        self.top_point = self.start_point - pg.Vector2(0, height // 2)
        self.bot_point = self.start_point + pg.Vector2(0, height // 2)

        self.top_edge = pg.Vector2(
            self.radius + self.radius * cos(radians(self.dep_angle)),
            self.radius + self.radius * sin(radians(self.dep_angle))
        )
        self.down_edge = pg.Vector2(
            self.radius + self.radius * cos(radians(self.end_angle)),
            self.radius + self.radius * sin(radians(self.end_angle))
        )
        self.draw_light(self.surface)

    def get_points(self, radius):
        # we take a variable radius, as we will need to generate points according to different radius
        points = []

        for i in range(0, self.dep_angle):
            points.append(pg.Vector2(self.radius+radius*cos(radians(self.dep_angle-i)),
                                     self.radius+radius*sin(radians(self.dep_angle-i))))

        for i in range(0, abs(self.end_angle)):
            points.append(pg.Vector2(self.radius+radius*cos(radians(-i)),
                                     self.radius+radius*sin(radians(-i))))

        return points

    def get_alpha(self, index_circle):
        alpha = int((sqrt(index_circle / self.n_circles) ** 4) * self.opacity)
        return alpha if alpha <= 255 else 255

    def draw_polygon(self, surface, radius, alpha):

        pts = self.get_points(radius)
        pg.draw.polygon(
            surface,
            (self.color[0], self.color[1], self.color[2], alpha),
            [
                self.top_point,
                *pts,
                self.bot_point,
            ]
        )
        pg.draw.polygon(
            surface,
            (self.color[0], self.color[1], self.color[2], alpha),
            [
                self.top_point,
                pts[-1],
                self.start_point
            ]
        )
        pg.draw.polygon(
            surface,
            (self.color[0], self.color[1], self.color[2], alpha),
            [
                self.bot_point,
                pts[0],
                self.start_point
            ]
        )

    def undo_layer(self, layer, pos):
        pts = self.get_points(self.radius)
        for pt in pts:
            pt += pos
        pg.draw.polygon(
            layer,
            (0, 0, 0, 0),
            [

                pos + pg.Vector2(self.radius, self.radius + self.height // 2),
                *pts,
                pos + pg.Vector2(self.radius, self.radius - self.height // 2),
            ]
        )

    def draw_light(self, surface):

        for i in range(0, self.n_circles):
            self.draw_polygon(surface, self.radius-i*self.step, self.get_alpha(i))

    def update(self, screen, scroll, LAYER):
        self.undo_layer(LAYER, self.pos-scroll)
        screen.blit(self.surface, self.pos - scroll)


class LightTypes:

    light_types = {
        "polygon_light": PolygonLight,
        "light_sources": LightSource
    }

    def __init__(self):
        pass

    def get_light_object(self, light_name, info, scale):

        args = []
        for key, item in info.items():
            item_ = copy(item)
            if key == "pos":
                item_[0] *= scale
                item_[1] *= scale
            elif key == "radius" or key == "height":
                item_ *= scale

            args.append(item_)

        return self.light_types[light_name](*args)
