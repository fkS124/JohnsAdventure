import pygame as pg
from copy import copy
from random import randint
from .particles_templates import Particle, ParticleManager


class DustManager(ParticleManager):

    def __init__(self, intensity:int, player_instance, display):
        super(DustManager, self).__init__(player_instance)
        self.particle_object = DustParticle
        self.player = player_instance
        self.display = display
        self.color = [255, 255, 255]
        self.size = (intensity//2, intensity//2)

        self.last_player_pos = copy(self.player.rect.midbottom)

    def trigger_check(self) -> bool:
        if self.get_pl_rect().midbottom != self.last_player_pos:
            return True
        return False

    def darker(self, color, degree):
        col = list(copy(color))
        for px in range(len(col)):
            col[px] -= degree
            if col[px] < 0:
                col[px] = 0
        return col

    def get_pl_rect(self):
        pl_rect = copy(self.player.rect)
        pl_rect.topleft -= pg.Vector2(15, -70)
        pl_rect.w -= 70
        pl_rect.h -= 115
        return pl_rect

    def logic(self) -> bool:
        if self.trigger_check():
            match self.player.direction:
                case "left":
                    val = [(0, 40), (0, 20)]
                case "right":
                    val = [(0, -40), (0, 20)]
                case "up":
                    val = [(-20, 20), (0, -40)]
                case "down":
                    val = [(-20, 20), (0, 40)]
            pl_rect = self.get_pl_rect()
            self.last_player_pos = copy(pl_rect.midbottom)


            try:
                for i in range(1):
                    self.add_particles(
                        self.size,
                        (pl_rect.centerx+(randint(min(val[0]), max(val[0]))), pl_rect.bottom-randint(min(val[1]), max(val[1]))),
                        self.darker(self.display.get_at(
                            (int(self.last_player_pos[0]-self.player.camera.offset.x),
                             int(self.last_player_pos[1]+1-self.player.camera.offset.y))
                        ), 10),
                        400
                    )
            except Exception as e:
                print(e)

class DustParticle(Particle):

    def __init__(self, size:tuple[int,int], pos:pg.Vector2, color:tuple[int,int,int], last_time, camera):
        super().__init__(
            image=pg.Surface(size),
            pos=pos,
            last_time=last_time,
            camera=camera
        )
        self.image.fill(color)
        self.dy = 1

    def behavior(self):
        if pg.time.get_ticks()-self.begin_time<self.last_time//2:
            self.rect.y -= self.dy
        else:
            self.rect.y += self.dy