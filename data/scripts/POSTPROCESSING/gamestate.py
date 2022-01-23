import random

import pygame as pg
from pygame import Rect
from copy import copy
from operator import attrgetter
import json
from random import gauss

from ..PLAYER.player import *
from ..PLAYER.inventory import *
from ..utils import resource_path, load, l_path, flip_vertical, flip_horizontal
from ..AI.death_animator import DeathManager
from .lights_manager import LightManager


def get_cutscene_played(id_: str):
    with open(resource_path('data/database/cutscenes.json'), "r") as data:
        return json.load(data)[id_]


class GameState:
    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects, id_: str, light_state="day"):
        self.id = id_

        # ------- SCREEN -----------------
        self.display, self.screen = DISPLAY, DISPLAY
        self.W, self.H = self.display.get_size()
        self.dt = 0  # wil be updated in update method

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj
        self._PLAYER_VEL = copy(self.player.DEFAULT_VEL)

        self.objects = []
        self.scroll = self.player.camera.offset.xy
        # Get the prop object dict, (basically all the objects generated from open_world.json)
        self.prop_objects = prop_objects

        # This might be the reason why players blit at top left for a nano second when you boot the game
        self.world = pg.Surface((1, 1))  # set default values for world -> supposed to be replaced

        # eg. -> "next_state_name" : pg.Rect(0, 0, 100, 100)
        self.exit_rects = {}  # the rects that lead to exit the current room

        # dead objects animations
        self.death_anim_manager = DeathManager(self.screen, self.player.camera)

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
        self.ended_script = get_cutscene_played(self.id)
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

        # Light system
        self.light_state = light_state
        self.lights_manager = LightManager(self.screen)
        self.additional_lights = []

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
        obj_rect.topleft -= self.scroll  # applying scroll

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
        self.player.base_vel = copy(self._PLAYER_VEL)
        self.dt = dt

        # blit the background
        self.screen.blit(self.world, -camera.offset.xy - self.offset_map)

        # get the scroll value and update it
        self.scroll = camera.offset.xy

        # store all the objects, and then will sort them according to their centery
        all_objects = []
        # register the objects that will be removed on next frame
        to_remove = []
        for obj_ in self.objects:
            # the point of this loop is to set an argument on each objects' centery in order to sort them
            # this sort is useful for the perspective

            if type(obj_) is not pg.Rect:  # if the object is a rect, we just ignore it
                # check if the object has a custom center (eg. Dummy)
                if hasattr(obj_, 'custom_center'):
                    # apply the custom center
                    obj_.centery = obj_.rect.y + obj_.custom_center
                else:
                    # just get the centery from the objects' rect
                    obj_.centery = obj_.rect.centery

                    # check if the current object is a non sortable object (eg. roads), set the centery to 0
                    # so it's always under everything
                    if hasattr(obj_, "sort"):
                        if not obj_.sort:
                            obj_.centery = -1000000

                # append the objects in the list
                all_objects.append(obj_)

        # do the same as above, but just in the death animation managers objects
        for obj_2 in self.death_anim_manager.animations:
            obj_2.centery = obj_2.rect.centery
        # add these objects to the list
        all_objects.extend(self.death_anim_manager.animations)

        # append the player to the objects (he needs to be sorted and updated too)
        all_objects.append(self.player)
        self.player.centery = self.player.rect.centery

        # update the objects, by ordering them considering their centery
        for obj in sorted(all_objects, key=attrgetter('centery')):

            # method.__code__.co_varnames -> ("arg1", "arg2", "var1", "var2", "var...") of the method
            # so we remove self argument (useless) using [1:x]
            # and we stop when we reach arguments' count gotten by : method.__code__.co_argcount
            # get all the arguments of the func in a list -> the arguments must be found inside this class (GameState)
            # for eg. : def update(self, screen, scroll)
            # self is ignored, screen and scroll are found by getattr(self, "screen") and getattr(self, "scroll")

            obj.update(*[getattr(self, arg)
                         for arg in obj.update.__code__.co_varnames[1:obj.update.__code__.co_argcount]]
                       )

            # add the dead enemies in the death manager
            if hasattr(obj, "IDENTITY"):
                if obj.IDENTITY == "ENEMY":
                    if obj.dead:
                        to_remove.append(obj)
                        scale = 1 if not hasattr(obj, "scale") else obj.scale
                        self.death_anim_manager.input_death_animation(obj.current_sprite,
                                                                      obj.rect.topleft + self.scroll, scale)

        # remove all the objects that need to be removed from self.objects
        for removing in to_remove:
            self.objects.remove(removing)
            del removing

        # Collision algorithm
        for obj in self.objects:

            if hasattr(obj, "move_ability"):
                objects = copy(self.objects)  # gets all objects
                objects.remove(obj)  # remove the object that we are currently checking for collisions
                objects.append(self.player)  # add the player in the object list bc it's still a collider 
                for obj_ in copy(objects):
                    if hasattr(obj_, "IDENTITY"):
                        if obj_.IDENTITY == "PROP":
                            if not obj_.collidable or pg.Vector2(obj.rect.center).distance_to(obj_.rect.center) > \
                                    max(obj.rect.size) + max(obj_.rect.size):
                                objects.remove(obj_)
                self.collision_system(obj, objects)  # handle collisions

        # handle collisions for the player
        objects = copy(self.objects)
        for obj_ in copy(objects):
            if hasattr(obj_, "IDENTITY"):
                if obj_.IDENTITY == "PROP":
                    if not obj_.collidable or \
                            pg.Vector2(self.player.rect.topleft).distance_to(obj_.rect.center) > \
                            max(obj_.rect.size) + max(self.player.rect.size):
                        objects.remove(obj_)
        self.collision_system(self.player, objects)

        # Light system updating
        self.lights_manager.update(self)

        # MUST BE REWORKED -> supposed to track if the player is interacting with exit rects
        for exit_state, exit_rect in self.exit_rects.items():

            itr_box = p.Rect(
                *(self.player.rect.topleft - pg.Vector2(17, -45)),
                self.player.rect.w // 2, self.player.rect.h // 2
            )

            if exit_state[-1] == "useless":
                break

            if len(exit_rect) == 3 and exit_rect[-1] == "mandatory":
                if itr_box.colliderect(exit_rect[0]):
                    return exit_state

            exit_rect = pg.Rect(exit_rect[0].x, exit_rect[0].y, *exit_rect[0].size), exit_rect[1]

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

    """These are now generation methods, to generate procedurally roads, hills and every other type of object
    that is in open_world.json"""

    def build_road(self, start_pos: tuple[int, int], n_road: int, type_r: str = "",
                   start_type: str = "", end_type: str = "", types: list = []):
        """Function to procedurally generate roads
        Parameters
        ----------
        start_pos : tuple[int, int]
                    The position of the first road.
        n_road : int
                 The number of roads.
        type_r : str
                 The type of the roads generated (except end and start)
        start_type : str
                     *Optional* The type of the road first generated
        end_type : str
                   *Optional* The type of the last generated road
        types : list
                *Optional* The generation will follow the list of types
        """

        roads = []  # list to store all the generated roads
        current_pos = list(start_pos)  # first pos, will be incremented according to the added roads
        default = type_r if type_r != "" else "ver_road"
        if not types:  # if types is empty
            for i in range(n_road):
                if end_type != "" and i == n_road - 1:
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
        return roads

    def generate_chunk(self, type_: str, x: int, y: int, row: int, col: int, step_x: int, step_y: int,
                       randomize: int = 20) -> list:

        """Generates a grid of objects, and randomize the positions a little, in order it not to look too much
        grid-ish, and more realistic.
        Parameters
        ----------
        type_ : str
                The type of object that will be generated.
        x : int
            x position of the beginning of the grid.
        y : int
            y position of the beginning of the grid.
        row : int
              Number of rows.
        col : int
              Number of columns.
        step_x : int
                 Width separating each generated object.
        step_y : int
                 Height separating each generated object.
        randomize : int
                    *Optional* Using gaussian repartition, randomize is moving randomly each objects in the grid, in
                    order to make the generation more realistic and less strict.
        """

        return [
            self.prop_objects[type_](
                (x + c * step_x + int(gauss(0, randomize)), y + r * step_y + int(gauss(0, randomize))))
            for c in range(col) for r in range(row)
        ]

    def generate_hills(self, direction: str, dep_pos: tuple[int, int], n_hills: int, mid_type: str = "left",
                       end_type: str = "hill_side_inner", no_begin: bool = False, start_type: str = "none") -> list:
        """ Generate hills procedurally.
        Parameters
        ----------
        direction : str
                    Direction of the hill -> "down" to go down vertically, "right" to go right horizontally.
        dep_pos : tuple[int, int]
                  Basic position of the hill, the position of the first hill part.
        n_hills : int
                  The number of hills (counting the corners).
        mid_type : str
                   The type of the middle hills (the ones between the two ends).
        end_type : str
                   The type of the last hill.
        no_begin : bool
                   Begins directly the hill by a middle.
        start_type : str
                     Type of first hill
        """

        corner_left = "hill_side_outer"
        corner_right = "hill_side_outer_rev"
        hill_middle = "hill_mid"
        hill_middle_down = "hill_mid" if mid_type == "left" else mid_type
        # dictionary containing all the sizes
        sizes = {
            corner_left: self.prop_objects[corner_left]((0, 0)).current_frame.get_size(),
            corner_right: self.prop_objects[corner_right]((0, 0)).current_frame.get_size(),
            hill_middle: self.prop_objects[hill_middle]((0, 0)).current_frame.get_size(),
            hill_middle_down: self.prop_objects[hill_middle_down]((0, 0)).current_frame.get_size(),
        }

        # first pos of the first hill, will be incremented
        current_pos = list(dep_pos)
        hills = []  # list that contains all the generated hills

        if not no_begin and start_type == "none":
            if direction == "right" or direction == "up" or direction == "down":
                hills.append(self.prop_objects[corner_left](dep_pos))
            else:
                hills.append(self.prop_objects[corner_right](dep_pos))

            # according to the direction, increment the position for the next hill according to the size of the
            # hill currently being added
            match direction:
                case "right":
                    current_pos[0] += sizes[corner_left][0]
                case "down":
                    current_pos[1] += sizes[corner_left][1]
                    current_pos[1] -= 102
        elif not no_begin and start_type != "none":
            hills.append(self.prop_objects[start_type](dep_pos))
            match direction:
                case "right":
                    current_pos[0] += sizes[start_type][0]
                case "down":
                    current_pos[1] += sizes[start_type][1]
                    current_pos[1] -= 102

        # n_hills - 2 because the ending and starting hills are generated outside the loop
        for i in range(n_hills - 2):
            new_hill = None
            # according to the direction, increment the position for the next hill according to the size of the
            # hill currently being added
            match direction:
                case "right":
                    new_hill = self.prop_objects[hill_middle](current_pos)
                    current_pos[0] += sizes[hill_middle][0]
                case "down":
                    new_hill = self.prop_objects[hill_middle_down](current_pos)
                    current_pos[1] += sizes[hill_middle_down][1]

                    # "cancel" the gap that the sprites are applying (can't take the height of the sprite without
                    # generating a graphical gap
                    current_pos[1] -= 51
                case _:
                    pass
            if new_hill is not None:
                # appends the generated hill to the list
                hills.append(new_hill)

        # add the last hill
        if end_type != "none":
            hills.append(self.prop_objects[end_type](current_pos))

        return hills

    def get_new_road_object(self, name, pos):
        direction = "H" if "hori" in name else "V"  # get the direction
        flip = {"H": "H" in name, "V": "V" in name}  # determine the axis to flip
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