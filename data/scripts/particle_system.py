import pygame as pg
from copy import copy
from random import randint, choice, gauss
from .particles_templates import Particle, ParticleManager
from .utils import scale


class DustManager(ParticleManager):

    def __init__(self, intensity: int, player_instance, display):
        super(DustManager, self).__init__(player_instance)
        self.particle_object = DustParticle
        self.player = player_instance
        self.display = display
        self.color = [255, 255, 255]
        self.size = (intensity // 2, intensity // 2)

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
                        (pl_rect.centerx + (randint(min(val[0]), max(val[0]))),
                         pl_rect.bottom - randint(min(val[1]), max(val[1]))),
                        self.darker(self.display.get_at(
                            (int(self.last_player_pos[0] - self.player.camera.offset.x),
                             int(self.last_player_pos[1] + 1 - self.player.camera.offset.y))
                        ), 20),
                        400
                    )
            except Exception as e:
                print(e)
            return True
        return False


class DustParticle(Particle):

    def __init__(self, size: tuple[int, int], pos: pg.Vector2, color: tuple[int, int, int], last_time, camera):
        super().__init__(
            image=pg.Surface(size),
            pos=pos,
            last_time=last_time,
            camera=camera
        )
        self.image.fill(color)
        self.dy = 1

    def behavior(self):
        if pg.time.get_ticks() - self.begin_time < self.last_time // 2:
            self.rect.y -= self.dy
        else:
            self.rect.y += self.dy


class SmokeManager(ParticleManager):
    def __init__(self, pos, size, player_instance):
        super(SmokeManager, self).__init__(player_instance)
        self.particle_object = SmokeParticle
        self.player = player_instance
        self.colors = [
            (150, 150, 150),
            (152, 152, 152),
            (154, 154, 154),
            (156, 156, 156),
        ]
        self.pos = pos
        self.size = size
        self.height = 1600
        self.duration = [4000, 4500]
        self.last_len = len(self.particles)
        for i in range(4):
            rad = int(gauss(*self.size))
            self.add_particles(rad, pg.Vector2(pos) - pg.Vector2(20, rad * 1.5), choice(self.colors), self.height,
                               randint(*self.duration))

    def trigger_check(self) -> bool:
        if self.last_len != len(self.particles):
            return True
        return False

    def logic(self) -> bool:

        if self.trigger_check():
            rad = int(gauss(*self.size))
            self.add_particles(rad, pg.Vector2(self.pos) - pg.Vector2(35, rad * 1.3), choice(self.colors), self.height,
                               randint(*self.duration))

        return True


class SmokeParticle(Particle):

    def __init__(self, radius: int, pos: pg.Vector2, color: tuple[int, int, int], max_height: int, last_time, camera):
        super().__init__(
            image=pg.Surface((radius // 2, radius // 2), pg.SRCALPHA),
            pos=pos,
            last_time=last_time,
            camera=camera
        )
        self.dep_pos = pos
        pg.draw.circle(self.image, color, (radius // 4, radius // 4), radius // 4)
        self.image = scale(self.image, 4.5)
        self.image.set_alpha(180)
        self.dx = 1
        self.dy = 1
        self.max_height = max_height
        self.delay = pg.time.get_ticks()
        self.l = choice([True, False])

    def behavior(self):
        self.rect.y -= self.dy
        self.image.set_alpha(180 - ((pg.time.get_ticks() - self.begin_time) / self.last_time) * 180)
        if pg.time.get_ticks() - self.delay > 200:
            self.l = not self.l
            self.delay = pg.time.get_ticks()
        if self.l:
            self.rect.x -= gauss(self.dx, 1)
        else:
            self.rect.x += gauss(self.dx, 1)

    def render(self, screen):
        update = super().render(screen)
        if pg.Vector2(self.pos).distance_to(pg.Vector2(self.dep_pos)) > self.max_height:
            return "kill"
        return update


PARTICLE_EFFECTS = {
    "smoke": SmokeManager,
    "dust": DustManager
}
