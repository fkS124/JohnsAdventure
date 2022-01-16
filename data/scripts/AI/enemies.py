from math import ceil
import pygame as pg
from .enemy import Enemy
from ..utils import resource_path


class Dummy(Enemy):

    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100, xp_drop=105):
        super().__init__(level_instance, screen, pos, player, hp=100, xp_drop=210,
                         custom_rect=[8 * 4, 34 * 4, (24 - 8) * 4, (47 - 34) * 4], enemy_type="static")
        self.load_animation(
            resource_path("data/sprites/dummy.png"),
            idle="static",
            hit_anim="animated",
            idle_coo=[0, 0, 34, 48, 1, 4],
            hit_coo=[0, 48, 34, 48, 4, 4]
        )
        self.custom_center = 250
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4


class ShadowDummy(Enemy):
    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100, xp_drop=105):
        # OC formula
        # calc_intensity = ceil(damage * health ) / xp_drop (this process must be automated instead of passed in
        # __init__)

        calc_intensity = ceil(12 * hp / xp_drop)  # 12 will be re-written else where later

        super().__init__(level_instance, screen, pos, player, hp=100, xp_drop=210, custom_rect=[10, 25, 29 * 3, 24 * 3],
                         enemy_type="shadow", intensiveness=calc_intensity, vel=5)
        self.load_animation(
            resource_path("data/sprites/shadow_dummie.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            idle_coo=[0, 0, 29, 24, 1, 4],
            walk_d_coo=[0, 25, 29, 24, 4, 4],
            walk_l_coo=[0, 0, 29, 24, 4, 4],
            walk_r_coo=[0, 25, 29, 24, 4, 4],
            walk_u_coo=[0, 0, 29, 24, 4, 4]
        )
        self.custom_center = 250
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4
