import pygame as pg
from .utils import *
from .damage_popups import DamagePopUp
from math import ceil


class Enemy:

    class Dummie:

        def __init__(self, screen:pg.Surface, pos:tuple[int, int], hp:int=100):

            self.attackable = True
            self.screen = screen

            self.img = scale(load("data/sprites/dummie_alpha.png", alpha=True), 4)
            self.x, self.y = pos
            self.Rect = self.img.get_rect(topleft=pos)

            self.hp = hp
            self.MAX_HP = hp

            self.endurance = 5

            self.damages_texts = []

        def deal_damage(self, value:int):
            self.hp -= ceil(value - self.endurance)
            # -> crit : dmg_type="crit" -> health ; dmg_type="health" ...
            self.damages_texts.append(DamagePopUp(self.screen, self.Rect, ceil(value-self.endurance), dmg_type="default")) 
            if self.hp <= 0:
                self.attackable = False
                self.hp = 0

        def update(self, scroll):
            
            self.screen.blit(self.img, (self.x-scroll[0], self.y-scroll[1]))
            pos = self.x-scroll[0], self.y-scroll[1]

            for dmg_txt in self.damages_texts:
                kill = dmg_txt.update(scroll)
                if kill == "kill":
                    self.damages_texts.remove(dmg_txt)

            self.Rect = self.img.get_rect(topleft=pos)
            
            if self.MAX_HP != self.hp:
                pg.draw.rect(self.screen, (0, 0, 0), [pos[0], pos[1]-20, self.img.get_width(), 15])
                pg.draw.rect(self.screen, (255, 0, 0), [pos[0], pos[1]-20, int((self.img.get_width()/self.MAX_HP)*self.hp), 15])