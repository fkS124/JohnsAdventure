"""

This script contains the Enemy Parent class

enemies.py is the enemy objects in the game

"""

from os import DirEntry
from types import coroutine
import pygame as pg
from random import choice
from copy import copy
from ..utils import load, get_sprite, scale, resource_path, flip_vertical
from .damage_popups import DamagePopUp
from ..PLAYER.player import Player
from ..particle_system import SmokeManager, DustManager, Shadow_Manager
from math import ceil, pi, cos, sin, tan, atan, degrees, sqrt, atan2

vec = pg.math.Vector2


class Enemy:
    """Designed to be the parent class of every enemy.
    
    It should help creating new enemies, faster.
    
    There are a lot of docstrings to ease the comprehension of it, 
    as it can be a bit complicated sometimes."""

    def __init__(self, level_instance, screen: pg.Surface, pos: tuple[int, int], player, hp: int = 100,
                 xp_drop=int, custom_rect=None, enemy_type="normal", intensiveness=0, vel: int = 1,
                 up_hitbox=(0, 0), down_hitbox=(0, 0),
                 right_hitbox=(0, 0), left_hitbox=(0, 0),
                 ):

        self.IDENTITY = "ENEMY"
        self.level = level_instance
        self.scroll = self.level.scroll
        self.BASE_VEL = vel
        self.vel = {
            "left": pg.Vector2(-1, 0).normalize() * self.BASE_VEL,
            "right": pg.Vector2(1, 0).normalize() * self.BASE_VEL,
            "down": pg.Vector2(0, 1).normalize() * self.BASE_VEL,
            "up": pg.Vector2(0, -1).normalize() * self.BASE_VEL
        }

        self.tp_V = pg.Vector2(0, 0)
        self.enemy_type = enemy_type

        self.sheet = load(resource_path("data/sprites/dummy.png"), alpha=False)
        self.attackable = True
        self.screen = screen
        self.idle = scale(get_sprite(self.sheet, 0, 0, 34, 48), 4)
        self.hit_anim = [scale(get_sprite(self.sheet, i * 34, 48, 34, 48), 4) for i in range(4)]
        self.x, self.y = pos
        self.rect = self.idle.get_rect(topleft=pos)

        self.dead = False  # dead or not
        self.attackable = True  # if false, player can't damage the enemy
        if custom_rect is not None:
            self.d_collision = custom_rect

        # COORDINATES MANAGEMENT
        self.pos = pos
        self.x, self.y = pos

        # LIFE
        self.hp = self.MAX_HP = self.show_hp = hp
        self.xp_available = xp_drop
        self.xp_drop = xp_drop
        self.endurance = 0
        self.show_life_bar = True

        self.dmg = 0  # I will config this later
        self.just_attacked = 0
        self.attacking_delay = 1500  # the N ms you were talking about

        # How powerful the enemy is
        self.intensiveness = intensiveness

        self.player = player
        # SHADOW PARTICLES
        if enemy_type == "shadow":
            # Initialize Shadow Particles only if they are shadow monsters
            self.aura_particles = Shadow_Manager(self.intensiveness, self.player, self.screen, self)

        self.particle_scroller = None

        # DAMAGE POPUPS
        self.damages_texts = []

        # ANIMATION
        self.current_sprite = None
        # self.rect = None
        self.id_anim = self.delay = 0
        self.hitted = False
        self.idling = False
        self.hitbox_rect = None
        self.status = ""  # Chasing, Roaming, Attacking

        self.delay_after_getting_stuck = 1500
        self.time_got_stuck = 0
        self.got_stuck = False
        self.chase_available = True

        # IMAGES & SPRITES MANAGEMENT

        # defines if the part is animated, useful for managing animation
        self.animating = {
            "hit": [False, "hitted", "hit_anim", "single"],
            "walk": [False, "moving", "walk_anim_manager", "loop"],
            "attack": [False, "attacking", "attack_anim_manager", "single"],
            "idle": [False, "idling", "idle", "loop"],
            "death": [False, "dead", "death_anim", "single"],
        }
        # FORM EXPLANATION : "state": [animating (T or F), "variable_of_animation_name", "animation_var_name" or
        # "dict_managing_anim", "loop" or "single"] "state" -> eg.: "hit" for the hit animation (default False)
        # animating -> tell if an animation is loaded and has to be played "variable_of_animation_name" -> name of
        # the variable that track if this currently has to be animated -> eg. : walking = True or False for walking
        # animation "animation_var_name" -> basically where the animation is stored or where the dict that manages it
        # is stored (dicts are useful for multiple directions) "loop" if the animation has to be played in a loop,
        # "single" otherwise

        # set some default values that will be replaced later
        self.sheet = pg.Surface((10, 10))
        self.idle = self.hit_anim = self.death_anim = self.walk_right = self.walk_left = self.walk_down = self.walk_up \
            = self.attack_right = self.attack_left = self.attack_down = self.attack_up = []

        # MOVEMENT
        self.moving = False
        self.velocity = pg.Vector2(1, 1)
        self.direction = "right"
        self.walk_anim_manager = {
            "right": self.walk_right,
            "left": self.walk_left,
            "down": self.walk_down,
            "up": self.walk_up
        }

        self.move_ability = {
            "left": True,
            "right": True,
            "up": True,
            "down": True
        }

        # KNOCK BACK
        # Only moving enemy objects will be able to get knocked
        self.knockable = True if self.enemy_type != "static" else False
        self.knocked_back = False  # true if currently affected by a knock back
        self.knock_back_duration = 0  # duration in ms of the knock back movement
        self.start_knock_back = 0  # time of starting the knock back
        self.knock_back_vel = pg.Vector2(0, 0)  # movement vel
        self.knock_back_friction = pg.Vector2(0, 0)  # slowing down
        self.knock_back_vel_y = 0  # jumpy effect vel
        self.health_bar_width = None

        # ATTACK
        self.attacking = False  # currently attacking -> True
        self.attack_anim_manager = {  # dict to store all the animations
            "right": self.attack_right,
            "left": self.attack_left,
            "down": self.attack_down,
            "up": self.attack_up
        }
        self.damage = 0
        self.hitbox_data = {
            "up": up_hitbox,
            "down": down_hitbox,
            "left": left_hitbox,
            "right": right_hitbox,
        }

    def load_animation(self,
                       sheet_path: str,
                       idle: str = "None",
                       hit_anim: str = "None",
                       walk_anim: str = "None",
                       death_anim: str = "None",
                       attack_anim: str = "None",
                       idle_coo=None,  # idle sprites
                       hit_coo=None,  # hit sprites
                       walk_l_coo=None,  # left
                       walk_r_coo=None,  # right
                       walk_u_coo=None,  # up
                       walk_d_coo=None,  # downs
                       death_coo=None,  # death sprites
                       attack_l_coo=None,
                       attack_r_coo=None,
                       attack_u_coo=None,
                       attack_d_coo=None,
                       flip_anim=False,  # I am too lazy to manually edit the drawings just for left side
                       ):

        """
        coordinates form : [x, y, width, height, iterations, scale]
        eg.: [0 (left), 0 (top), 34 (34 px width), 48 (48 px height), 5 (5 sprites), 4 (scale original sprite by 4)]
        
        Function to setup the enemy's animation, usually called in __init__ method of the child
        class, after the super class's init.

        eg.:

        class NewEnemy(Enemy):
            def __init__(self):
                super().__init__(self, screen, pos, hp)
                self.load_animation(...)
        
        """

        # update sheet
        self.sheet = load(sheet_path)

        if idle in ["static", "animated"] and idle_coo is not None:  # check if there is an animation passed as an arg
            self.animating["idle"][0] = True  # specify that there is an idle animation
            self.idle = self.load_sheet(idle_coo)  # load it

        if hit_anim in ["static", "animated"] and hit_coo is not None:
            self.animating["hit"][0] = True
            self.hit_anim = self.load_sheet(hit_coo)

        if walk_anim in ["static", "animated"] and None not in [walk_d_coo, walk_l_coo, walk_r_coo, walk_u_coo]:
            self.animating["walk"][0] = True
            self.walk_down = self.load_sheet(walk_d_coo)
            self.walk_right = self.load_sheet(walk_r_coo)
            self.walk_up = self.load_sheet(walk_u_coo)
            self.walk_left = self.load_sheet(walk_l_coo, flip_anim)

        if death_anim in ["static", "animated"] and death_coo is not None:
            self.animating["death"][0] = True
            self.death_anim = self.load_sheet(death_coo)

        if attack_anim in ["static", "animated"] and None not in [attack_d_coo, attack_l_coo, attack_r_coo,
                                                                  attack_u_coo]:
            self.animating["attack"][0] = True
            self.attack_down = self.load_sheet(attack_d_coo)
            self.attack_right = self.load_sheet(attack_r_coo)
            self.attack_up = self.load_sheet(attack_u_coo)
            self.attack_left = self.load_sheet(attack_l_coo, flip_anim)

        # updates the animations in the dicts
        self.walk_anim_manager = {
            "right": self.walk_right,
            "left": self.walk_left,
            "down": self.walk_down,
            "up": self.walk_up
        }

        self.attack_anim_manager = {  # dict to store all the animations
            "right": self.attack_right,
            "left": self.attack_left,
            "down": self.attack_down,
            "up": self.attack_up
        }

    def load_sheet(self, coo, flip=False):

        """Load an animation sequence (of sprites) on a sprites,
        you obviously have to pass the coordinates of the sprites."""

        x, y, width, height = coo[:4]
        if coo[-1] != 0:  # check for scale
            if not flip:
                return [scale(get_sprite(self.sheet, x + width * i, y, width, height), coo[-1]) for i in range(coo[-2])]
            else:
                return [
                    flip_vertical(scale(get_sprite(self.sheet, x + width * i, y, width, height), coo[-1]))
                    for i in range(coo[-2])
                ]
        else:
            if not flip:
                return [get_sprite(self.sheet, x + width * i, y, width, height) for i in range(coo[-2])]
            else:
                return [flip_vertical(get_sprite(self.sheet, x + width * i, y, width, height)) for i in range(coo[-2])]

    def animate(self):

        """Animate the enemy considering all its states, it's designed to be generic,
        reusable and modifiable."""

        for key in self.animating:

            if self.animating[key][0]:  # check if an animation is loaded
                val = self.animating[key]
                if getattr(self, val[1]):
                    animation = getattr(self, val[2])
                    if type(animation) is dict:
                        animation = animation[self.direction]

                    if pg.time.get_ticks() - self.delay > 100:
                        match val[-1]:
                            case "loop":
                                self.id_anim = (self.id_anim + 1) % len(animation)
                            case "single":
                                if self.id_anim + 1 < len(animation):
                                    self.id_anim += 1
                        self.delay = pg.time.get_ticks()
                        self.current_sprite = animation[self.id_anim]

                        # Update Enemy's rect
        self.rect = self.current_sprite.get_rect(topleft=self.pos)

    def deal_damage(self, value: int, crit: bool, endurance_ignorance: bool = False, knock_back: dict = None):

        """Deal damages to its own instance, also triggers animations of hits,
        include critics and endurance ignorance."""

        self.hp -= ceil(value - self.endurance) if not endurance_ignorance else ceil(value)
        if self.hitted:
            self.id_anim = 0

        self.hitted = True
        # -> crit : dmg_type="crit" -> health ; dmg_type="health" ...
        if not endurance_ignorance:
            self.damages_texts.append(DamagePopUp(self.screen, self.rect, ceil(value - self.endurance),
                                                  dmg_type=("default" if not crit else "crit")))
        else:
            self.damages_texts.append(DamagePopUp(self.screen, self.rect, ceil(value), dmg_type="health"))

        if self.hp <= 0:
            self.attackable = False
            self.dead = True
            self.hp = 0

        if knock_back is not None:
            self.knocked_back = True
            self.knock_back_vel = knock_back["vel"]
            self.knock_back_vel_y = knock_back["vel"].length() // 4
            self.knock_back_duration = knock_back["duration"]
            self.knock_back_friction = knock_back["friction"]
            self.start_knock_back = pg.time.get_ticks()

    def shadow_highlight(self, screen, pos, frame):
        """ A cruel evil with monstrous power.
            Gives objects and rested monsters life.
        Args:
            screen (pygame.Surface): main window of the game
            scroll (int tuple): the camera scroller offset
        """

        # Note : once the outline is looking lit, add some particles behind the outline

        # object_name.name_particle.update(object_name.screen)

        # Show the Particles
        self.aura_particles.update(screen)

        outline = pg.mask.from_surface(frame).to_surface()
        outline.set_colorkey((0, 0, 0))  # Pixel Perfect cutting
        outline.set_alpha(125)  # Removes a bit of opacity

        # Draw Shadow Entity on top of the cut surface.
        pg.draw.polygon(outline, pg.Color("#6c25be"), pg.mask.from_surface(frame).outline())
        thickness = 4

        screen.blits([
            (outline, pos + pg.Vector2(thickness, 0)),
            (outline, pos + pg.Vector2(-thickness, 0)),
            (outline, pos + pg.Vector2(0, -thickness)),
            (outline, pos + pg.Vector2(0, thickness))
        ])

    def life_bar(self, scroll):

        """Draw a life bar if the enemy is not at its max hp"""
        if self.MAX_HP != self.hp:
            width = self.current_sprite.get_width() if self.health_bar_width is None else self.health_bar_width

            curr_x = self.pos[0] if self.health_bar_width is None else self.pos[0] + 15  # we need / 3 here

            # Outline
            pg.draw.rect(
                self.screen,
                (0, 0, 0),
                [
                    curr_x,
                    self.pos[1] - 12,
                    width, 10
                ],
                border_radius=25
            )

            # Health Bar
            pg.draw.rect(self.screen, (255, 0, 0),
                         [
                             curr_x,
                             self.pos[1] - 11,
                             int((width / self.MAX_HP) * self.show_hp) - 2, 8
                         ],
                         border_radius=25)

            # pg.draw.rect(self.screen, (255,255,255), self.rect, 1)

    def update_dmg_popups(self, scroll):

        """Update all the damages popups, including the removing."""

        for dmg_txt in self.damages_texts:
            kill = dmg_txt.update(scroll)
            if kill == "kill":
                self.damages_texts.remove(dmg_txt)

    def update_states(self):

        """Defines the priorities of states, for eg, if the enemy is dead,
        it forbid any actions for the enemy. It helps for animation coordination
        and fix bugs."""

        if self.dead:
            try:
                self.end_instance()
            except Exception as e:
                print(e)
            self.show_life_bar = False
            self.moving = False
            self.attacking = False
            return

        if self.attacking:
            if pg.time.get_ticks() - self.just_attacked > self.attacking_delay:
                self.attacking = False
                self.moving = True
                self.idling = False
            else:
                self.moving = False
                self.idling = False
            return

        if self.moving:
            self.idling = False
        else:
            self.idling = True

    def switch_directions(self, last_direction="none", blocked_direction="none"):
        directions = ["left", "right", "up", "down"]
        if last_direction != "none":
            directions.remove(last_direction)
            if blocked_direction == "none" and blocked_direction in directions:
                directions.remove(blocked_direction)
        self.direction = choice(directions)

    def check_for_hit(self, dt, p_rect):
        """

            Dealing damage to the player.

        """

        if self.current_sprite is not None:
            enemy_s = self.current_sprite.get_width(), self.current_sprite.get_height()
            hit_d = self.hitbox_data

            hit_dict = {
                "up": pg.Rect(
                    self.rect.midtop,
                    hit_d['up']
                ),

                "down": pg.Rect(
                    self.rect.midbottom,
                    hit_d['down']
                ),

                "left": pg.Rect(
                    self.rect.midright - vec(enemy_s[0] + enemy_s[0] // 2, 0),
                    hit_d['left']
                ),

                "right": pg.Rect(
                    self.rect.midright - vec(enemy_s[0] // 2, 0),
                    hit_d['right']
                ),
            }

            pg.draw.rect(self.screen, (255, 0, 0), hit_dict[self.direction])

            if hit_dict[self.direction].colliderect(p_rect):
                self.player.health_target = self.player.health - self.damage

    def move(self, dt):

        if self.got_stuck:
            if pg.time.get_ticks() - self.time_got_stuck > self.delay_after_getting_stuck:
                self.chase_available = True
                self.got_stuck = False
            else:
                self.chase_available = False
        else:
            self.chase_available = True

        # enemy rect
        col_rect = copy(self.rect)
        col_rect.topleft += self.scroll
        col_rect.topleft += pg.Vector2(*self.d_collision[:2])
        col_rect.size = self.d_collision[2:]

        # Update rect data for hit detection ( wrong practice but the damage is huge )
        self.hitbox_rect = col_rect
        self.hitbox_rect.topleft -= self.scroll

        # pg.draw.rect(self.screen, (255, 255, 255), self.hitbox_rect)
        # pg.draw.rect(self.screen, (200, 200, 200), col_rect)

        # get player's rect
        pl_rect = copy(self.player.rect)
        pl_rect.topleft -= pg.Vector2(15, -70) + self.scroll
        pl_rect.w -= 70
        pl_rect.h -= 115

        # pg.draw.rect(self.screen, (100, 200, 200), pl_rect)

        # ___ CHECK ENEMY TYPE ____
        if self.enemy_type != "static":

            enemy_speed = self.BASE_VEL

            # -------- BOUND CHECKING ------

            GET_DISTANCE = vec(col_rect.center).distance_to(vec(pl_rect.center))

            # Enemy must not be in the attacking state to move around
            if not self.attacking:
                if GET_DISTANCE >= 300:
                    self.status, self.moving = "ROAMING", True
                    if self.move_ability[self.direction]:
                        match self.direction:
                            case "down":
                                self.y += enemy_speed
                            case "up":
                                self.y -= enemy_speed
                            case "right":
                                self.x += enemy_speed
                            case "left":
                                self.x -= enemy_speed
                    else:
                        self.switch_directions(self.direction)

                # CHASE THE PLAYER
                elif GET_DISTANCE > 90:  # I need to switch this up by enemy's.attack_distance
                    self.moving, self.status = True, "CHASING"
                    try:
                        self.tp_V = (
                                (
                                  vec(self.player.rect.center) - vec(self.rect.center + self.scroll)
                                ).normalize() * self.BASE_VEL
                        )
                        self.direction = "left" if self.tp_V[0] < 0 else "right"
                        self.x += self.tp_V[0] if self.move_ability[self.direction] else 0
                        self.y += self.tp_V[1] if self.move_ability[
                            sec_dir := "up" if self.tp_V[1] < 0 else "down"] else 0

                        if not (self.move_ability[self.direction] and self.move_ability[sec_dir]):
                            self.got_stuck = True
                            self.time_got_stuck = pg.time.get_ticks()
                            self.switch_directions(self.direction, sec_dir)
                            match self.direction:
                                case "down":
                                    self.y += enemy_speed
                                case "up":
                                    self.y -= enemy_speed
                                case "right":
                                    self.x += enemy_speed
                                case "left":
                                    self.x -= enemy_speed
                    except ValueError:
                        pass

                # HIT THE PLAYER
                else:
                    self.status = "ATTACKING"
                    self.moving, self.attacking, self.idling = False, True, False
                    self.just_attacked = pg.time.get_ticks()
                    self.id_anim = 0
                    enemy_speed = 0
                    # Attack John!
                    self.check_for_hit(dt, pl_rect)
                    self.moving = True
            else:
                self.moving = False

            """
            
            BUG: when enemy overlaps with any green rect, it's stuck forever inside the rect
            
            output of self.direct when enemy overlaps any rect
            
            none up
            none down
            none right
            none left
            
            I believe this issue, a death screen and the cave level are left (hopefully) :pleading_eyes:
            
            """
            print(self.direction)

    def behavior(self, dt):
        self.move(dt)

    def logic(self, dt):

        """Here we pass all the behavior of the enemy, movement,
        attacks, spells..."""

        self.behavior(dt)
        self.update_states()
        self.animate()

    def update(self, scroll, dt):
        self.scroll = scroll

        """We gather all the methods needed to make the enemy work here.
        We pass the scroll."""

        # update the life bar if it's shown
        if self.show_life_bar:
            if self.show_hp >= self.hp:
                self.show_hp -= dt * 16 * abs((self.show_hp - self.hp) // 3 + 1)
                # I believe I add the scratch here

            # Show the UI
            self.life_bar(scroll)

        # update the damage pop ups
        self.update_dmg_popups(scroll)

        # update the pos of the enemy
        self.pos = self.x - scroll[0], self.y - scroll[1]
        # apply the knock back
        if self.knocked_back and self.knockable:

            if pg.time.get_ticks() - self.start_knock_back > self.knock_back_duration:
                self.knocked_back = False

            if pg.time.get_ticks() - self.start_knock_back > self.knock_back_duration / 2:
                self.y += self.knock_back_vel_y * dt * 25
            else:
                self.y -= self.knock_back_vel_y * dt * 25  # will later be changed to player's crit damage / endurance

            self.x += self.knock_back_vel[0] * dt * 25
            self.y += self.knock_back_vel[1] * dt * 25
            self.knock_back_vel -= self.knock_back_friction

        # print(self.direction, self.moving, self.idling, self.move_ability)
        # call logic method
        self.logic(dt)

        # ___SHADOW TYPE MONSTERS GET A OUTLINE/PARTICLES__
        if self.enemy_type == "shadow":
            self.particle_scroller = self.x + 60, self.y + 40
            self.shadow_highlight(self.screen, self.pos, self.current_sprite)

        self.screen.blit(self.current_sprite, self.pos)
