import pygame as pg
from copy import copy
from random import randint


class DamagePopUp:

    def __init__(self, screen: pg.Surface, rect:pg.Rect, value:int, dmg_type:str="default"):

        self.screen = screen
        self.font = pg.font.Font("data/database/pixelfont.ttf", 25)
        self.basic_rect = copy(rect)

        colors = {
            "health": (110, 0, 150), 
            "crit": (255, 255, 0), 
            "default": (255, 255, 255)
        }

        self.rendered_txt = self.font.render(str(value), True, colors[dmg_type])

        self.rect = self.rendered_txt.get_rect(center=(rect.centerx+rect.width//2, rect.y+rect.width*2))
        self.init_time = pg.time.get_ticks()
        self.velocity_y = 7

        self.direction = "left" if randint(0, 1) == 0 else "right"

    def update(self, scroll):
        
        self.screen.blit(self.rendered_txt, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        self.rect.y -= self.velocity_y if self.rect.y-scroll[1] > self.basic_rect.y else 0

        self.rect.x += 2 if self.direction == "right" else -2

        if pg.time.get_ticks() - self.init_time > 1000:
            return "kill"
