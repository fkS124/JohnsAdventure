from math import ceil
import pygame as pg
from .enemy import Enemy
from ..utils import resource_path


class Dummy(Enemy):

    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100,
                 xp_drop=105):
        super().__init__(level_instance, screen, pos, player, hp=100, xp_drop=210,
                         custom_rect=[8 * 4 + 2, 34 + 17, (24 - 8) * 4, 34 * 4], enemy_type="static")
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
        self.damage = 10


class ShadowDummy(Enemy):
    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100,
                 xp_drop=105):
        # OC formula
        # calc_intensity = ceil(damage * health ) / xp_drop (this process must be automated instead of passed in
        # __init__)

        calc_intensity = ceil(12 * hp / xp_drop)  # 12 will be re-written else where later

        super().__init__(level_instance, screen, pos, player, hp=100, xp_drop=210, custom_rect=[10, 25, 29 * 3, 24 * 3],
                         enemy_type="shadow", intensiveness=calc_intensity, vel=2)
        self.load_animation(
            resource_path("data/sprites/shadow_dummie.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 29, 24, 1, 4],
            walk_d_coo=[0, 25, 29, 24, 5, 4],
            walk_l_coo=[0, 0, 29, 24, 5, 4],
            walk_r_coo=[0, 25, 29, 24, 5, 4],
            walk_u_coo=[0, 0, 29, 24, 5, 4],
            attack_d_coo=[0, 50, 29, 24, 5, 4],
            attack_l_coo=[0, 50, 29, 24, 5, 4],
            attack_r_coo=[0, 75, 29, 24, 5, 4],
            attack_u_coo=[0, 75, 29, 24, 5, 4],

        )
        self.custom_center = 250
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4
        self.damage = 10


class Guardian(Enemy):
    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100,
                 xp_drop=160):
        super().__init__(
            level_instance, screen, pos, player,
            hp=100,
            xp_drop=210,
            custom_rect=[25 * 5 + 10, 50, 29 * 2, 45 * 2 + 25],
            enemy_type="normal",
            vel=1,
            up_hitbox=(18 * 4, 34 * 4),
            down_hitbox=(18 * 4, 34 * 4),
            left_hitbox=(34 * 4, 18 * 4),
            right_hitbox=(34 * 4, 18 * 4),
        )

        self.health_bar_width = 45 * 2

        self.load_animation(
            resource_path("data/sprites/guardian_sheet.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 67, 34, 1, 5],
            walk_d_coo=[0, 0, 67, 34, 5, 5],
            walk_l_coo=[0, 0, 67, 34, 5, 5],
            walk_r_coo=[0, 0, 67, 34, 5, 5],
            walk_u_coo=[0, 0, 67, 34, 5, 5],
            attack_d_coo=[0, 34, 67, 34, 5, 5],
            attack_l_coo=[0, 34, 67, 34, 5, 5],
            attack_r_coo=[0, 34, 67, 34, 5, 5],
            attack_u_coo=[0, 34, 67, 34, 5, 5],
            flip_anim=True
        )
        self.custom_center = 250
        self.xp_drop = self.xp_available = xp_drop
        self.damage = 5


class Goblin(Enemy):
    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player: object, hp: int = 100,
                 xp_drop=160):
        super().__init__(
            level_instance, screen, pos, player, hp=100, xp_drop=210,
            custom_rect=[15, 35, 17 * 2, 25 * 2 + 10],
            enemy_type="normal",
            vel=2,
            up_hitbox=(17 * 4, 15 * 4),
            down_hitbox=(17 * 4, 15 * 4),
            left_hitbox=(15 * 4, 18 * 4),
            right_hitbox=(15 * 4, 17 * 4),
        )

        self.load_animation(
            resource_path("data/sprites/goblin_template.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 17, 25, 1, 4],
            walk_d_coo=[0, 0, 17, 25, 5, 4],
            walk_l_coo=[0, 0, 17, 25, 5, 4],
            walk_r_coo=[0, 0, 17, 25, 5, 4],
            walk_u_coo=[0, 0, 17, 25, 5, 4],
            attack_d_coo=[0, 25, 17, 25, 5, 4],
            attack_l_coo=[0, 25, 17, 25, 5, 4],
            attack_r_coo=[0, 25, 17, 25, 5, 4],
            attack_u_coo=[0, 25, 17, 25, 5, 4],
            flip_anim=True
        )

        self.damage = 2
        self.custom_center = 250
        self.xp_drop = self.xp_available = xp_drop

# Soon REDACTED
