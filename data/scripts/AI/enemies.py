import pygame as pg
from ..utils import load, get_sprite, scale
from .damage_popups import DamagePopUp
from math import ceil


class Enemy:

    class Dummie:

        def __init__(self, screen:pg.Surface, pos:tuple[int, int], hp:int=100):

            self.attackable = True
            self.screen = screen
            
            self.sheet = load("data/sprites/dummy.png", alpha=True)
            self.idle = scale(get_sprite(self.sheet, 0, 0, 34, 48), 4)
            self.hit_anim = [scale(get_sprite(self.sheet, i * 34, 48, 34, 48), 4) for i in range(4)]
            self.x, self.y = pos
            self.Rect = self.idle.get_rect(topleft=pos)

            self.hp = hp
            self.MAX_HP = hp

            self.endurance = 5

            self.damages_texts = []

            self.id_anim = 0
            self.hitted = False
            self.delay = 0

        def deal_damage(self, value:int, crit:bool, endurance_ignorance:bool=False):
            self.hp -= ceil(value - self.endurance) if not endurance_ignorance else ceil(value)
            if self.hitted:
                self.id_anim = 0
            self.hitted = True
            # -> crit : dmg_type="crit" -> health ; dmg_type="health" ...
            if not endurance_ignorance:
                self.damages_texts.append(DamagePopUp(self.screen, self.Rect, ceil(value-self.endurance), dmg_type=("default" if not crit else "crit"))) 
            else:
                self.damages_texts.append(DamagePopUp(self.screen, self.Rect, ceil(value), dmg_type="health"))
            if self.hp <= 0:
                self.attackable = False
                self.hp = 0

        def update(self, scroll):
            
            if not self.hitted:
                self.screen.blit(self.idle, (self.x-scroll[0], self.y-scroll[1]))
            else:
                if pg.time.get_ticks() - self.delay > 100:
                    if self.id_anim + 1 < len(self.hit_anim):
                        self.id_anim += 1
                        self.delay = pg.time.get_ticks()
                    else:
                        self.hitted = False
                        self.id_anim = 0
                cur_frame = self.hit_anim[self.id_anim]
                self.screen.blit(cur_frame, (self.x-scroll[0], self.y-scroll[1]))
            pos = self.x-scroll[0], self.y-scroll[1]

            for dmg_txt in self.damages_texts:
                kill = dmg_txt.update(scroll)
                if kill == "kill":
                    self.damages_texts.remove(dmg_txt)

            self.Rect = self.idle.get_rect(topleft=pos)
            
            if self.MAX_HP != self.hp:
                pg.draw.rect(self.screen, (0, 0, 0), [pos[0], pos[1]-20, self.idle.get_width(), 15])
                pg.draw.rect(self.screen, (255, 0, 0), [pos[0], pos[1]-20, int((self.idle.get_width()/self.MAX_HP)*self.hp), 15])