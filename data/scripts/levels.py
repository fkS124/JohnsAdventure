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
from .utils import resource_path, load, l_path
from .props import PROP_OBJECTS, Chest
from .PLAYER.items import Training_Sword, Knight_Sword

class GameState:

    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        # ------- SCREEN -----------------
        self.display, self.screen = DISPLAY, DISPLAY
        self.W, self.H = self.display.get_size()
        self.dt = 0  # wil be updated in update method

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj

        self.objects = []

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
                all_objects.append(obj_)
        all_objects.append(self.player)
        self.player.centery = self.player.rect.centery
        all_objects
        for obj in sorted(all_objects, key=attrgetter('centery')):
            obj.update(*[getattr(self, arg) for arg in obj.update.__code__.co_varnames[1:obj.update.__code__.co_argcount]])

        """ Collision Algorithm and Entity Updater """
        self.changes = {}  # reset the changes
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

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        super().__init__(DISPLAY, player_instance)

        self.objects = [
            # Wall borders
            Rect(0,0, 1280,133), # Left
            Rect(1270,134,10,586), # Right
            Rect(0,0,1280,133), # Up
            Rect(0,711, 1280,9), # Down
            #################
            npc.Mau((150,530), (300, 100)),
            Rect(10,90, 430,360),
            Rect(5,500, 72, 214),
            Rect(450, 40, 410, 192),
            Rect(36,400, 77,94), 
            Dummy(DISPLAY, (1050, 300)),
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

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        super().__init__(DISPLAY, player_instance)

        self.world = pg.transform.scale(load(resource_path('data/sprites/world/kitchen.png')), (1280,720))  # 1 Kitchen Room
        self.objects = [
            # Wall borders
            Rect(0,0, 1280,133), # Left
            Rect(1270,134,10,586), # Right
            Rect(0,0,1280,133), # Up
            Rect(0,711, 1280,9), # Down
            #################
            npc.Cynthia((570, 220)),
            Rect(20, 250, 250,350),
            Rect(280,300, 64, 256),
            Rect(10,0, 990, 230),
            Rect(1020, 440, 256, 200),
            Chest((910,140), {"items":Training_Sword(), "coins": 50})
        ]

        self.exit_rects = {
            "player_room": (pg.Rect(1054,68,138,119),  "Back to your room?"),
            "johns_garden": (pg.Rect(551, 620, 195, 99), "Go outside?")
        }

        self.spawn = {
            "player_room": (self.exit_rects["player_room"][0].bottomleft+pg.Vector2(75, 0)),
            "johns_garden": (self.exit_rects["johns_garden"][0].topleft+pg.Vector2(0, -200))
        }


class JohnsGarden(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        with open(resource_path('data/database/open_world_pos.json')) as datas:
            positions = json.load(datas)
        with open("data/database/open_world.json") as datas_:
            DATAS = json.load(datas_)
        def get_scale(name):
            return DATAS[name]["sc"]
        jh_pos = positions["john_house"][0]
        jh_siz = (DATAS["john_house"]["w"]*get_scale("john_house"), DATAS["john_house"]["h"]*get_scale("john_house"))

        super().__init__(DISPLAY, player_instance)
        self.world = scale(l_path('data/sprites/world/chapter_1_map.png', alpha=True), 3)
        self.world2 = pg.Surface(self.world.get_size())
        self.world2.fill((0, 100, 0))
        self.objects = [
            PROP_OBJECTS["box"]((200, 1200)),
            PROP_OBJECTS["full_fence"]((jh_pos[0]*3+jh_siz[0]*1.5-537*3, jh_pos[1]*3+300)),
            PROP_OBJECTS["side_fence"]((jh_pos[0]*3+jh_siz[0]*1.5-537*3, jh_pos[1]*3+300)),
            PROP_OBJECTS["half_fence"]((jh_pos[0]*3+jh_siz[0]*1.5-537*3, jh_pos[1]*3+300+764)),
            PROP_OBJECTS["half_fence_reversed"]((jh_pos[0]*3+jh_siz[0]*1.5-537*3+909, jh_pos[1]*3+300+764)),
            PROP_OBJECTS["side_fence"]((jh_pos[0]*3+jh_siz[0]*1.5-537*3+1581, jh_pos[1]*3+300)),
            *[PROP_OBJECTS[object_](
                (pos[0]*get_scale(object_),pos[1]*get_scale(object_)))
                for object_, pos_ in positions.items()
                for pos in pos_
            ]
        ]

        self.exit_rects = {
            "kitchen": (pg.Rect(1829*3+(235*3)//2, 867*3+258*3, 100, 100), "Go back to your house?")
        }
        self.spawn = {
            "kitchen": (self.exit_rects["kitchen"][0].bottomleft)
        }

    def update(self, camera, dt):
        self.screen.blit(self.world2, -camera.offset.xy)
        return super().update(camera, dt)