import random

import pygame as pg
from pygame import Rect
from copy import copy
from operator import attrgetter
import json
from random import gauss

# from .PLAYER.items import Chest
from .PLAYER.player import *
from .PLAYER.inventory import *
from .AI.enemies import Dummy
from .AI import npc
from .utils import resource_path, load, l_path, flip_vertical, flip_horizontal
from .props import Chest
from .PLAYER.items import Training_Sword, Knight_Sword
from .AI.death_animator import DeathManager
from .POSTPROCESSING.lights_manager import LightManager
from .POSTPROCESSING.light_types import PolygonLight, LightSource


class GameState:
    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects, light_state="day"):

        # ------- SCREEN -----------------
        self.display, self.screen = DISPLAY, DISPLAY
        self.W, self.H = self.display.get_size()
        self.dt = 0  # wil be updated in update method

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj
        self._PLAYER_VEL = copy(self.player.base_vel)

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

        # Light system
        self.light_state = light_state
        self.lights_manager = LightManager(self.screen)
        self.additional_lights = []

    def load_objects(self, filename):
        # Open file
        file = open(resource_path(filename), 'r')
        temp_list = []

        # Sadly we have to manually define everything for eval, unless we find a way to one line it
        stuff = {
            'DISPLAY': self.display, 'Rect': Rect, 'npc': npc, 'Dummy': Dummy,
            'Chest': Chest, 'Training_Sword': Training_Sword

        }
        for line in file:
            obj = line.replace('\n', '')
            temp_list.append(eval(obj, stuff))
        # Close file for security
        file.close()
        return temp_list

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
                            obj_.centery = 0

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

        # Light system updating
        self.lights_manager.update(self)

        # MUST BE REWORKED -> supposed to track if the player is interacting with exit rects
        for exit_state, exit_rect in self.exit_rects.items():

            exit_rect = pg.Rect(exit_rect[0].x, exit_rect[0].y, *exit_rect[0].size), exit_rect[1]
            itr_box = p.Rect(
                *(self.player.rect.topleft - pg.Vector2(17, -45)),
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
        print("Successfully generated", len(roads))
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
                       end_type: str = "hill_side_inner", no_begin: bool = False) -> list:
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

        if not no_begin:
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


class PlayerRoom(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, light_state="inside_clear")
        self.objects = super().load_objects('data/database/levels/player_room.txt')
        self.world = pg.transform.scale(l_path('data/sprites/world/Johns_room.png'), (1280, 720))
        self.exit_rects = {
            "kitchen": (pg.Rect(1008, 148, 156, 132), "Go down?")
        }
        self.spawn = {
            "kitchen": (self.exit_rects["kitchen"][0].bottomleft + pg.Vector2(0, 50))
        }

        self.camera_script = [
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 0,
                "text": f"Hello Player. Welcome to John's Adventure.",
                "waiting_end": 4000,
                "zoom": 2
            },
            {
                "pos": (1100, 225),
                "duration": 1000,
                "waiting_end": 1000,
                "text": "Your quest is waiting for you downstairs."
            },
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 750,
                "waiting_end": 250,
            },
            {
                "next_cam_status": "follow",
                "zoom": 1,
                "zoom_duration": 1200
            }
        ]

        self.additional_lights = [
            PolygonLight(
                pg.Vector2(79*3, 9*3),
                68*3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175
            ),
            PolygonLight(
                pg.Vector2(347 * 3, 9 * 3),
                68 * 3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175
            ),
            PolygonLight(
                pg.Vector2(254*3+1, 26*3),
                49*3,
                150,
                25,
                125,
                (89, 144, 135),
                dep_alpha=255,
                horizontal=True
            )
        ]


class Kitchen(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, light_state="inside_clear")
        self.world = pg.transform.scale(load(resource_path('data/sprites/world/kitchen.png')), (1280, 720))
        self.objects = super().load_objects('data/database/levels/kitchen.txt')
        self.exit_rects = {
            "player_room": (pg.Rect(1054, 68, 138, 119), "Back to your room?"),
            "johns_garden": (pg.Rect(551, 620, 195, 99), "Go outside?")
        }
        self.spawn = {
            "player_room": (self.exit_rects["player_room"][0].bottomleft + pg.Vector2(75, 0)),
            "johns_garden": (self.exit_rects["johns_garden"][0].topleft + pg.Vector2(0, -200))
        }
        self.additional_lights = [
            PolygonLight(
                pg.Vector2(103 * 3, 9 * 3),
                68 * 3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=80,
                horizontal=True,
                additional_alpha=150
            ),
        ]


class JohnsGarden(GameState):
    """Open world state of the game -> includes john's house, mano's hut, and more..."""

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, light_state="day")
        self._PLAYER_VEL = 10 * 3  # 3 freq

        # Get the positions and the sprites' informations from the json files
        with open(resource_path('data/database/open_world_pos.json')) as pos, \
                open(resource_path("data/database/open_world.json")) as infos:
            self.positions, self.sprite_info = json.load(pos), json.load(infos)
        self.get_scale = lambda name: self.sprite_info[name]["sc"]  # func to get the scale of a sprite

        # John's house position and size
        jh_pos = self.positions["john_house"][0] - pg.Vector2(1, 30)
        jh_siz = (self.sprite_info["john_house"]["w"] * self.get_scale("john_house"),
                  self.sprite_info["john_house"]["h"] * self.get_scale("john_house"))
        jh_sc = self.get_scale("john_house")

        # Mano's hut position and scale
        mano_pos = self.positions["manos_hut"][0]
        mano_sc = self.get_scale("manos_hut")

        # horizontal road width
        hr_r_width = self.sprite_info["hori_road"]["w"] * self.sprite_info["hori_road"]["sc"]
        hhr_r_width = self.sprite_info["hori_road_half"]["w"] * self.sprite_info["hori_road_half"]["sc"]
        hr_s_width = self.sprite_info["hori_sides"]["w"] * self.sprite_info["hori_sides"]["sc"]
        hr_s_height = self.sprite_info["hori_sides"]["h"] * self.sprite_info["hori_sides"]["sc"]
        vr_r_height = self.sprite_info["ver_road"]["h"] * self.sprite_info["ver_road"]["sc"]

        # Use super().load_objects() , when every model is ready
        self.objects = [
            # .prop_objects["box"]((200, 1200)),
            # Fences of john's house (values are calculated for scale = 3 considering this won't change)
            self.prop_objects["full_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 300)),
            self.prop_objects["side_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 300)),
            self.prop_objects["half_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 1611, jh_pos[1] * 3 + 1064)),
            self.prop_objects["half_fence_reversed"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 702, jh_pos[1] * 3 + 1064)),
            self.prop_objects["side_fence"]((jh_pos[0] * 3 + jh_siz[0] * 1.5 - 30, jh_pos[1] * 3 + 300)),
            # All the objects contained in open_world_pos.json
            *[self.prop_objects[object_](
                (pos[0] * self.get_scale(object_), pos[1] * self.get_scale(object_)))
                for object_, pos_ in self.positions.items()
                for pos in pos_
            ],
            self.prop_objects["street_lamp"]((323 * 3 + 900, 888 * 3 + 800)),
            self.prop_objects["street_lamp"]((323 * 3 - 300, 888 * 3 + 800)),
            # Mano's hut custom collisions
            pg.Rect(mano_pos[0] * mano_sc, (mano_pos[1] + 292) * mano_sc, 41 * mano_sc, 35 * mano_sc),
            pg.Rect((mano_pos[0] + 31) * mano_sc, (mano_pos[1] + 292) * mano_sc, 11 * mano_sc, 52 * mano_sc),
            pg.Rect((mano_pos[0] + 240) * mano_sc, (mano_pos[1] + 292) * mano_sc, 11 * mano_sc, 52 * mano_sc),
            pg.Rect((mano_pos[0] + 240) * mano_sc, (mano_pos[1] + 292) * mano_sc, 41 * mano_sc, 35 * mano_sc),
            pg.Rect((mano_pos[0] + 41) * mano_sc, (mano_pos[1] + 324) * mano_sc, 75 * mano_sc, 4 * mano_sc),
            pg.Rect((mano_pos[0] + 165) * mano_sc, (mano_pos[1] + 324) * mano_sc, 75 * mano_sc, 4 * mano_sc),
            pg.Rect((mano_pos[0] + 116) * mano_sc, (mano_pos[1] + 322) * mano_sc, 6 * mano_sc, 20 * mano_sc),
            pg.Rect((mano_pos[0] + 159) * mano_sc, (mano_pos[1] + 322) * mano_sc, 6 * mano_sc, 20 * mano_sc),

            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc, (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc),
                             n_road=4, type_r="hori_road", end_type="hori_road_half"),

            # john dirt road
            *self.build_road(start_pos=((jh_pos[0] + 846 - 727) * jh_sc, (jh_pos[1] + 361 - 82) * jh_sc),
                             n_road=2, start_type="ver_dirt", end_type="ver_sides"),

            # Manos dirt road
            *self.build_road(start_pos=((jh_pos[0] - 246) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width,
                                        (jh_pos[1] + 361 - 82) * jh_sc), start_type="ver_dirt", end_type="ver_sides",
                             n_road=2),

            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc), n_road=3, type_r="hori_road",
                             end_type="Vhori_sides"),

            # Route 4
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc + hr_s_height), n_road=3,
                             type_r="ver_road", end_type="Vhori_sides"),
            # Cave Road
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc + hr_s_height + 2 * vr_r_height),
                             n_road=2,
                             type_r="hori_road"),

            # Route 5 Bottom Right
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 498) * jh_sc + hr_s_height * 18), n_road=2,
                             type_r="ver_road", end_type="Vver_turn"),

            # Route 6 Bottom Right
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 3,
                                        (jh_pos[1] + 361 - 82 + 172 - 50) * jh_sc + 2 * hr_s_height + 3 * vr_r_height),
                             n_road=3, type_r="hori_road"),

            # Route 7 -> Top Right
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc - 3 * vr_r_height),
                             n_road=3, type_r="ver_road"),

            # Route 8 -> Top right of map
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49) * jh_sc - 3 * vr_r_height - 33 * 3),
                             n_road=4, type_r="hori_road", start_type="hori_turn"),

            # The game without the grass and trees take around 150mb of ram
            # Currently the trees take +100 mb of ram, so we need to be exact and precise with the numbers
            
            *self.generate_hills("right", (jh_pos[0]*jh_sc - 600, jh_pos[1]*jh_sc - 450), 8, mid_type="hill_mid", end_type="hill_side_inner_rev"),

            # Trees right from john's room
            *self.generate_chunk("tree", jh_pos[0] * jh_sc + 1250, jh_pos[1] * jh_sc, 3, 2, 100 * 4, 100 * 3,
                                 randomize=10),


            # Trees right from manos hut
            *self.generate_chunk("tree", mano_pos[0] * mano_sc + 950, jh_pos[1] * jh_sc, 3, 3, 100 * 4, 100 * 3,
                                 randomize=40),
            # Trees left from manos hut
            *self.generate_chunk("tree", mano_pos[0] * mano_sc - 750, jh_pos[1] * jh_sc, 3, 2, 100 * 4, 100 * 3,
                                 randomize=10),
            # Add grass details under those trees
            *self.generate_chunk("grass", jh_pos[0] * jh_sc + 1250, jh_pos[1] * jh_sc + 460, 4, 11, 100 * 2, 100 * 2,
                                 randomize=20),
            
            # Cave Borders
            *self.generate_hills("right", (jh_pos[0]*jh_sc - 2400, jh_pos[1]*jh_sc+1400), 10, mid_type="hill_mid", end_type="hill_side_outer_rev"),
            *self.generate_hills("down", (jh_pos[0]*jh_sc - 2400, jh_pos[1]*jh_sc+1400+160*3-102), 8, no_begin=True, mid_type="hill_side_mid", end_type="hill_side_outer"),

            *self.generate_hills("down", (jh_pos[0]*jh_sc + 2400 + 160 * 8 - 31, jh_pos[1]*jh_sc+1400+160*3-102), 3, no_begin=True, mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev"),


            *self.generate_hills("right", (jh_pos[0]*jh_sc - 2400 + 160 * 4 + 31, jh_pos[1]*jh_sc+1400 + 160 * 26 - 102 + 10), 10, no_begin=True, mid_type="hill_mid", end_type="hill_side_inner_rev")
        ]

        self.exit_rects = {
            "kitchen": (pg.Rect((jh_pos[0] + 846 - 728) * jh_sc + 3, (jh_pos[1] + 280) * jh_sc , 100, 60),
                        "Go back to your house?"),
            # pg.Rect(1829*3-200, 888*3+500, 100, 100) -> debug (spawn to manos hut roof) 
            "manos_hut": (pg.Rect((mano_pos[0] + 124) * mano_sc, (mano_pos[1] + 337 - 43) * mano_sc, 100, 50),
                          "Enter Mano's hut ?")
        }
        self.spawn = {
            "kitchen": self.exit_rects["kitchen"][0].bottomleft,
            "manos_hut": self.exit_rects["manos_hut"][0].midbottom
        }

    def update(self, camera, dt):
        pg.draw.rect(self.screen, [60, 128, 0], [0, 0, self.W, self.H])
        return super().update(camera, dt)


class ManosHut(GameState):

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, light_state="inside_dark")

        # Mano's hut inside ground
        self.world = pg.transform.scale(l_path('data/sprites/world/manos_hut.png'), (1280, 720))
        sc_x = 1280 / 453
        sc_y = 720 / 271
        self.objects = [
            # Wall borders
            Rect(0, 0, 10, 720),  # Left
            Rect(1270, 134, 10, 586),  # Right
            Rect(0, 0, 1280, 133),  # Up
            Rect(0, 711, 1280, 9),  # Down

            # Όταν
            npc.Manos(pg.Vector2(235 * sc_x, 115 * sc_y), (300, 100)),
            npc.Candy(pg.Vector2(205, 395)),  # TODO : Put a real position

            Chest((422 * sc_x, 47 * 4 * sc_y - 45), {"items": Knight_Sword(), "coins": 30}),
            # Furnitures
            self.prop_objects["m_hut_bed"]((381 * sc_x, 47 * sc_y)),
            self.prop_objects["m_hut_sofa"]((97 * sc_x, 88 * sc_y)),
            self.prop_objects["m_hut_table"]((163 * sc_x, 37 * sc_y)),
            self.prop_objects["m_hut_fireplace"]((5 * sc_x, (193 - 236) * sc_y))
        ]

        #  Below are the hitboxes, the player spawns almost near them!

        self.spawn = {
            "johns_garden": (630, 490)
        }

        self.exit_rects = {
            "johns_garden": (pg.Rect(560, 635, 150, 75), "Go back to open world ?")
        }
