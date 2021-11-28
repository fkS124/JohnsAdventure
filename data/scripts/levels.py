import pygame as pg
from pygame import Rect
from copy import copy
from operator import attrgetter
import json

#from .PLAYER.items import Chest
from .PLAYER.player import *
from .PLAYER.inventory import *
from .AI.enemies import Dummy
from .AI import npc
from .utils import resource_path, load, l_path, flip_vertical, flip_horizontal
from .props import Chest
from .PLAYER.items import Training_Sword, Knight_Sword




class GameState:

    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(self, DISPLAY:pg.Surface, player_instance, prop_objects):

        # ------- SCREEN -----------------
        self.display, self.screen = DISPLAY, DISPLAY
        self.W, self.H = self.display.get_size()
        self.dt = 0  # wil be updated in update method

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj

        self.objects = []
        self.scroll = self.player.camera.offset.xy
        # Get the prop object dict, (basically all the objects generated from open_world.json)
        self.prop_objects = prop_objects

        # This might be the reason why players blit at top left for a nano second when you boot the game
        self.world = pg.Surface((1, 1))  # set default values for world -> supposed to be replaced

        # eg. -> "next_state_name" : pg.Rect(0, 0, 100, 100)
        self.exit_rects = {}  # the rects that lead to exit the current room

        # ----------- COLLISION SYSTEM ---------

        self.points_side = {  # -> lambda functions to get the coordinates of the colliding points
            "left": lambda rect, vel: [
                rect.topleft + pg.Vector2(vel[0], vel[1]),
                rect.midleft - pg.Vector2(-vel[0], 0),
                rect.bottomleft - pg.Vector2(-vel[0], vel[1])
            ],
            "right": lambda rect, vel: [
                rect.topright + pg.Vector2(-vel[0], vel[1]),
                rect.midright - pg.Vector2(vel[0], 0),
                rect.bottomright - pg.Vector2(vel[0], vel[1])
            ],
            "up": lambda rect, vel: [
                rect.topright - pg.Vector2(-vel[0], vel[1]),
                rect.midtop - pg.Vector2(0, vel[1]),
                rect.topleft - pg.Vector2(vel[0], vel[1])
            ],
            "down": lambda rect, vel: [
                rect.bottomright + pg.Vector2(vel[0], vel[1]),
                rect.midbottom + pg.Vector2(0, vel[1]),
                rect.bottomleft + pg.Vector2(-vel[0], vel[1])
            ]
        }

        self.spawn = {}
        # previous_state : coords

        # camera script :
        self.cam_index = -1
        self.ended_script = False
        self.camera_script = []
        """
        ** = optional
        [
        {
            "pos": (x, y),
            "duration": (int) ms, -> (can be null -> will just use func look_at)
            ** -> "text": str,  (can be empty) 
            ** -> "wainting_end": (int) ms,
            ** -> "next_cam_status": cam_status
        },
        {
            ... -> same shape : will be played directly after it
        }
        ]
        """
        self.offset_map = pg.Vector2(0, 0)

    def check(self, moving_object, col_obj, side):
        """Given a side of the moving object,
        this function detects the collision between
        the moving object and the collider.
        
        It handles the change of dictionary of the moving object.
        
        During the whole func, we use copy to get rects. It's not always useful, 
        but it's necessary sometimes, so to prevent from eventual assignement bugs
        we do it by default."""

        vel = copy(moving_object.velocity)  # gets velocity of the moving object
        obj_rect = copy(moving_object.rect)  # gets rect from the moving object
        obj_rect.topleft-=self.scroll  # applying scroll

        # apply a few modifications from the original player's rect to fit better to the collision system
        if type(moving_object) is Player: 
            obj_rect.topleft -= pg.Vector2(15, -70)
            obj_rect.w -= 70
            obj_rect.h -= 115

        if type(col_obj) is not pg.Rect:
            col_rect = copy(col_obj.rect)
            if hasattr(col_obj, "IDENTITY"):
                if col_obj.IDENTITY in ["NPC", "PROP"]:
                    col_rect.topleft -= self.scroll  # apply scroll to NPCs because it's not applied
            # apply a few modifications from the original player's rect to fit better to the collision system
            if type(col_obj) is Player:
                col_rect.topleft -= self.scroll
                col_rect.topleft -= pg.Vector2(15, -70)
                col_rect.w -= 70
                col_rect.h -= 115
        else:
            col_rect = copy(col_obj)  # if it's a rect, just copy it
            col_rect.topleft -= self.scroll

        if hasattr(col_obj, "d_collision"):
            col_rect.topleft += pg.Vector2(*col_obj.d_collision[:2])
            col_rect.size = col_obj.d_collision[2:]
  
        # pg.draw.rect(self.screen, (0, 255, 0), col_rect, 1)   ------ DO NOT ERASE : USEFUL FOR DEBUGGING -----

        # colliding points
        points = self.points_side[side](obj_rect, vel)

        changed = False  # -> gets if a change has been done
        for point in points:
            # pg.draw.circle(self.screen, (0, 255, 255), point, 5)   ------ DO NOT ERASE : USEFUL FOR DEBUGGING -----
            if col_rect.collidepoint(point):
                changed = True
                moving_object.move_ability[side] = False 
        if not changed:
            moving_object.move_ability[side] = True  # if no change have been done, resets the value
        if not moving_object.move_ability[side]:
            return "kill"  
            # -> tell the "parent script" to break the loop because a collision has already occured on this side

    def collision_system(self, obj_moving, objects_to_collide):

        """Basically the function that handles every object and every direction
        of the collide system."""

        for direction in ["left", "right", "down", "up"]:
            for obj in objects_to_collide:
                check = self.check(obj_moving, obj, direction)
                if check == "kill":  # a collision has occured on this side, no need to check more, so break
                    if hasattr(obj_moving, "switch_directions"):
                        obj_moving.switch_directions(blocked_direction=direction)  # switch NPCs direction for eg.
                    break

    def update(self, camera, dt):

        # update the game values
        self.player.rooms_objects = self.objects 
        self.dt = dt

        """world_rect = self.world.get_rect()
        # display background                         # TODO : fix this zoom effect pls (not urgent)
        self.display.blit(
            
            pg.transform.scale(self.world, 
            #(world_rect.x + self.player.camera.fov.x * 2, world_rect.x + self.player.camera.fov.y)
            ), 
            -camera.offset.xy
        )"""
        self.screen.blit(self.world, -camera.offset.xy-self.offset_map)
        
        self.scroll = camera.offset.xy

        all_objects = []
        for obj_ in self.objects:
            if type(obj_) is not pg.Rect:
                if hasattr(obj_, 'custom_center'):
                    obj_.centery = obj_.rect.y+obj_.custom_center
                else:
                    obj_.centery = obj_.rect.centery
                    if hasattr(obj_, "sort"):
                        if not obj_.sort:
                            obj_.centery = 0
                all_objects.append(obj_)
        all_objects.append(self.player)
        self.player.centery = self.player.rect.centery
        for obj in sorted(all_objects, key=attrgetter('centery')):
            obj.update(*[getattr(self, arg)
                for arg in obj.update.__code__.co_varnames[1:obj.update.__code__.co_argcount]]
            )

        """ Collision Algorithm and Entity Updater """
        for obj in self.objects:
            """
            method.__code__.co_varnames -> ("arg1", "arg2", "var1", "var2", "var...") of the method
            so we remove self argument (useless) using [1:x]
            and we stop when we reach arguments' count gotten by : method.__code__.co_argcount
            get all the arguments of the func in a list -> the arguments must be found inside this class (GameState)
            for eg. : def update(self, screen, scroll)
            self is ignored, screen and scroll are found by getattr(self, "screen") and getattr(self, "scroll")
            """

            if hasattr(obj, "move_ability"):
                objects = copy(self.objects)  # gets all objects
                objects.remove(obj)  # remove the object that we are currently checking for collisions
                objects.append(self.player)  # add the player in the object list bc it's still a collider 
                for obj_ in copy(objects):
                    if hasattr(obj_, "IDENTITY"):
                        if obj_.IDENTITY == "PROP":
                            if not obj_.collidable:
                                objects.remove(obj_)
                self.collision_system(obj, objects)  # handle collisions
        
        # handle collisions for the player
        objects = copy(self.objects)
        for obj_ in copy(objects):
            if hasattr(obj_, "IDENTITY"):
                if obj_.IDENTITY == "PROP":
                    if not obj_.collidable:
                        objects.remove(obj_)
        self.collision_system(self.player, objects)

        # MUST BE REWORKED -> supposed to track if the player is interacting with exit rects
        for exit_state, exit_rect in self.exit_rects.items():
            
            exit_rect = pg.Rect(exit_rect[0].x, exit_rect[0].y, *exit_rect[0].size), exit_rect[1]
            itr_box = p.Rect(
                *(self.player.rect.topleft-pg.Vector2(17, -45)),
                self.player.rect.w // 2, self.player.rect.h // 2
            )

            if itr_box.colliderect(exit_rect[0]):
                match self.player.InteractPoint:
                    case 1:
                        # Open UI interaction
                        self.player.is_interacting = True
                        self.player.npc_text = exit_rect[1]
                    case 2:
                        # Send the player to next level
                        self.player.is_interacting = False
                        self.player.npc_text = ''
                        return exit_state

class PlayerRoom(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance, prop_objects):

        super().__init__(DISPLAY, player_instance, prop_objects)

        self.objects = [
            # Wall borders
            Rect(0, 0, 1280, 133),  # Left
            Rect(1270, 134, 10, 586),  # Right
            Rect(0, 0, 1280, 133),  # Up
            Rect(0, 711, 1280, 9),  # Down
            # Interactable objects
            npc.Mau((150, 530), (300, 100)),
            Dummy(DISPLAY, (1050, 300)),
            # Colliders
            Rect(10, 90, 430, 360),
            Rect(5, 500, 72, 214),
            Rect(450, 40, 410, 192),
            Rect(36, 400, 77, 94),
        ]

        self.world = pg.transform.scale(l_path('data/sprites/world/Johns_room.png'), (1280, 720))

        self.exit_rects = {
            "kitchen": (pg.Rect(1008,148,156,132), "Go down?")
        }

        self.spawn = {
            "kitchen": (self.exit_rects["kitchen"][0].bottomleft+pg.Vector2(0, 50))
        }

        self.camera_script = [
            {
                "pos": (self.screen.get_width()//2-120, self.screen.get_height()//2-20), 
                "duration": 0, 
                "text": f"Hello Player. Welcome to John's Adventure.",
                "waiting_end": 4000,
            },
            {
                "pos": (1100, 225),
                "duration": 1000,
                "waiting_end": 1000,
                "text": "Your quest is waiting for you downstairs."
            },
            {
                "pos": (self.screen.get_width()//2-120, self.screen.get_height()//2-20),
                "duration": 750,
                "waiting_end": 250,
                "next_cam_status": "follow"
            }
        ]


class Kitchen(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance, prop_objects):

        super().__init__(DISPLAY, player_instance, prop_objects)

        # Kitchen background
        self.world = pg.transform.scale(load(resource_path('data/sprites/world/kitchen.png')), (1280, 720))
        self.objects = [
            # Wall borders
            Rect(0, 0, 1280, 133),  # Left
            Rect(1270, 134, 10, 586),  # Right
            Rect(0, 0, 1280, 133),  # Up
            Rect(0, 711, 1280, 9),  # Down
            # Interactable objects
            npc.Cynthia((570, 220)),
            Chest((910, 140), {"items": Training_Sword(), "coins": 50}),
            # Colliders
            Rect(20, 250, 250, 350),
            Rect(280, 300, 64, 256),
            Rect(10, 0, 990, 230),
            Rect(1020, 440, 256, 200),
        ]

        self.exit_rects = {
            "player_room": (pg.Rect(1054, 68, 138, 119), "Back to your room?"),
            "johns_garden": (pg.Rect(551, 620, 195, 99), "Go outside?")
        }

        self.spawn = {
            "player_room": (self.exit_rects["player_room"][0].bottomleft + pg.Vector2(75, 0)),
            "johns_garden": (self.exit_rects["johns_garden"][0].topleft + pg.Vector2(0, -200))
        }


class JohnsGarden(GameState):

    """Open world state of the game -> includes john's house, mano's hut, and more..."""

    def __init__(self, DISPLAY:pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects)

        # Get the positions and the sprites' informations from the json files
        with open(resource_path('data/database/open_world_pos.json')) as pos, \
            open(resource_path("data/database/open_world.json")) as infos:
            self.positions, self.sprite_info = json.load(pos), json.load(infos)
        self.get_scale = lambda name: self.sprite_info[name]["sc"]  # func to get the scale of a sprite

        # John's house position and size
        jh_pos = self.positions["john_house"][0]
        jh_siz = (self.sprite_info["john_house"]["w"] * self.get_scale("john_house"),
                  self.sprite_info["john_house"]["h"] * self.get_scale("john_house"))
        jh_sc = self.get_scale("john_house")

        # Mano's hut position and scale
        mano_pos = self.positions["manos_hut"][0]
        mano_sc = self.get_scale("manos_hut")

        # horizontal road width
        hr_r_width = self.sprite_info["hori_road"]["w"]*self.sprite_info["hori_road"]["sc"]
        hhr_r_width = self.sprite_info["hori_road_half"]["w"] * self.sprite_info["hori_road_half"]["sc"]
        hr_s_width = self.sprite_info["hori_sides"]["w"] * self.sprite_info["hori_sides"]["sc"]
        hr_s_height = self.sprite_info["hori_sides"]["h"] * self.sprite_info["hori_sides"]["sc"]
        vr_r_height = self.sprite_info["ver_road"]["h"]*self.sprite_info["ver_road"]["sc"]

        self.objects = [
            self.prop_objects["box"]((200, 1200)),
            # Fences of john's house (values are calculated for scale = 3 considering this won't change)
            self.prop_objects["full_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 300)),
            self.prop_objects["side_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 300)),
            self.prop_objects["half_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 1064)),
            self.prop_objects["half_fence_reversed"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 702, jh_pos[1] * 3 + 1064)),
            self.prop_objects["side_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 30, jh_pos[1] * 3 + 300)),
            # All the objects contained in open_world_pos.json
            *[self.prop_objects[object_](
                (pos[0]*self.get_scale(object_),pos[1]*self.get_scale(object_)))
                for object_, pos_ in self.positions.items()
                for pos in pos_
            ],
            # Mano's hut custom collisions
            pg.Rect(mano_pos[0] * mano_sc, (mano_pos[1] + 292) * mano_sc, 41 * mano_sc, 35 * mano_sc),
            pg.Rect((mano_pos[0] + 31) * mano_sc, (mano_pos[1] + 292) * mano_sc, 11 * mano_sc, 52 * mano_sc),
            pg.Rect((mano_pos[0] + 240) * mano_sc, (mano_pos[1] + 292) * mano_sc, 11 * mano_sc, 52 * mano_sc),
            pg.Rect((mano_pos[0] + 240) * mano_sc, (mano_pos[1] + 292) * mano_sc, 41 * mano_sc, 35 * mano_sc),
            pg.Rect((mano_pos[0] + 41) * mano_sc, (mano_pos[1] + 324) * mano_sc, 75 * mano_sc, 4 * mano_sc),
            pg.Rect((mano_pos[0] + 165) * mano_sc, (mano_pos[1] + 324) * mano_sc, 75 * mano_sc, 4 * mano_sc),
            pg.Rect((mano_pos[0] + 116) * mano_sc, (mano_pos[1] + 322) * mano_sc, 6 * mano_sc, 20 * mano_sc),
            pg.Rect((mano_pos[0] + 159) * mano_sc, (mano_pos[1] + 322) * mano_sc, 6 * mano_sc, 20 * mano_sc),
            # Roads
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc, (jh_pos[1] + 361 - 82) * jh_sc),
                             n_road=1, start_type="ver_dirt"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc, (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc),
                             n_road=6, start_type="hori_sides", type_r="hori_road", end_type="hori_road_half"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width,
                                        (jh_pos[1] + 361 - 82) * jh_sc), start_type="ver_dirt", end_type="ver_sides",
                             n_road=2),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc), n_road=3, type_r="hori_road",
                             end_type="Vhori_sides"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc + hr_s_height), n_road=4,
                             type_r="ver_road", end_type="Vver_turn"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 3,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc + hr_s_height + 3 * vr_r_height),
                             n_road=3, type_r="hori_road"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc - 3 * vr_r_height),
                             n_road=3, type_r="ver_road"),
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc - 3 * vr_r_height - 33*3),
                             n_road=5, type_r="hori_road", start_type="hori_turn", end_type="Vhori_end"),
        ]

        self.exit_rects = {
            "kitchen": (pg.Rect((jh_pos[0]+846-728)*jh_sc, (jh_pos[1]+341-82)*jh_sc, 100, 60) , "Go back to your house?"),
            # pg.Rect(1829*3-200, 888*3+500, 100, 100) -> debug (spawn to manos hut roof)
            "manos_hut": (pg.Rect((mano_pos[0]+568-428)*mano_sc, (mano_pos[1]+337-43)*mano_sc, 100, 50),
                          "Enter Mano's hut ?")
        }
        self.spawn = {
            "kitchen": self.exit_rects["kitchen"][0].bottomleft,
            "manos_hut": self.exit_rects["manos_hut"][0].bottomleft
        }

    def build_road(self, start_pos:tuple[int, int], n_road:int, type_r:str="",
                   start_type:str="", end_type:str="", types:list=[]):
        roads = []
        current_pos = list(start_pos)
        default = type_r if type_r != "" else "ver_road"
        if types == []:
            for i in range(n_road):
                if end_type != "" and i == n_road-1:
                    road = end_type
                elif start_type != "" and i == 0:
                    road = start_type
                else:
                    road = default
                new_road = self.get_new_road_object(road, current_pos)
                roads.append(new_road)
                if "hori" in road:
                    current_pos[0] += new_road.current_frame.get_width()
                else:
                    current_pos[1] += new_road.current_frame.get_height()
        else:
            for index, road in enumerate(types):
                new_road = self.get_new_road_object(road, current_pos)
                if "hori" in road:
                    current_pos[0] += new_road.current_frame.get_width()
                else:
                    current_pos[1] += new_road.current_frame.get_height()
                roads.append(new_road)
        print("Successfully generated", len(roads))
        return roads

    def get_new_road_object(self, name, pos):
        direction = "H" if "hori" in name else "V"  # get the direction
        flip = {"H":"H" in name, "V":"V" in name}  # determine the axis to flip
        if flip["V"] and flip["H"]:
            name = name[2:]  # removing the useless letters to avoid KeyError
        elif flip["V"] and not flip["H"] or flip["H"] and not flip["V"]:
            name = name[1:]  # removing the useless letters to avoid KeyError
        road_obj = self.prop_objects[name](pos)  # get the object

        # apply the flip
        if flip["H"]:
            road_obj.idle[0] = flip_horizontal(road_obj.idle[0])
        if flip["V"]:
            road_obj.idle[0] = flip_vertical(road_obj.idle[0])

        return road_obj

    def update(self, camera, dt):
        pg.draw.rect(self.screen, [0, 100, 0], [0, 0, self.W, self.H])
        return super().update(camera, dt)


class ManosHut(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance, prop_objects):

        super().__init__(DISPLAY, player_instance, prop_objects)

        # Mano's hut inside ground
        self.world = pg.transform.scale(l_path('data/sprites/world/manos_hut.png'), (1280, 720))
        sc_x = 1280/453
        sc_y = 720/271
        self.objects = [
            # Wall borders
            Rect(0, 0, 10, 720),  # Left
            Rect(1270, 134, 10, 586),  # Right
            Rect(0, 0, 1280, 133),  # Up
            Rect(0, 711, 1280, 9),  # Down
            # Furnitures
            self.prop_objects["m_hut_bed"]((381*sc_x, 47*sc_y)),
            self.prop_objects["m_hut_sofa"]((97*sc_x, 88*sc_y)),
            self.prop_objects["m_hut_table"]((163*sc_x, 37*sc_y)),
            self.prop_objects["m_hut_fireplace"]((5*sc_x, (193-236)*sc_y))
        ]

        self.spawn = {
            "johns_garden": (1280//2, 720//2)
        }

        self.exit_rects = {
            "johns_garden": (pg.Rect(1280 // 2, 720*3//4, 150, 150), "Go back to open world ?")
        }