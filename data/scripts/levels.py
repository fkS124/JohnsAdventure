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
from .AI.enemies import Dummy, ShadowDummy, Guardian, Goblin
from .AI import npc
from .utils import resource_path, load, l_path
from .props import Chest
from .PLAYER.items import Training_Sword, Knight_Sword
from .AI.death_animator import DeathManager
from .POSTPROCESSING.lights_manager import LightManager
from .POSTPROCESSING.light_types import PolygonLight, LightSource
from .POSTPROCESSING.gamestate import GameState
from .sound_manager import SoundManager


def get_cutscene_played(id_: str):
    with open(resource_path('data/database/cutscenes.json'), "r") as data:
        return json.load(data)[id_]


def play_cutscene(id_: str):
    with open(resource_path('data/database/cutscenes.json'), "r") as data:
        data = json.load(data)
    data[id_] = True
    with open(resource_path('data/database/cutscenes.json'), "w") as data2:
        json.dump(data, data2, indent=2)


class PlayerRoom(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, "player_room", light_state="inside_clear")
        self.objects = [  # super().load_objects('data/database/levels/player_room.txt')
            Rect(0, 0, 1280, 133),
            Rect(1270, 134, 10, 586),
            Rect(0, 0, 1280, 133),
            Rect(0, 711, 1280, 9),
            npc.Mau((150, 530), (300, 100)),
            Rect(10, 90, 430, 360),
            Rect(5, 500, 72, 214),
            Rect(450, 40, 410, 192),
            Rect(36, 400, 77, 94),
            ShadowDummy(self, self.screen, (600, 600), self.player)
        ]
        self.world = pg.transform.scale(l_path('data/sprites/world/Johns_room.png'), (1280, 720))
        self.exit_rects = {
            "kitchen": (pg.Rect(1008, 148, 156, 132), "Go down?")
        }
        self.spawn = {
            "kitchen": (self.exit_rects["kitchen"][0].bottomleft + pg.Vector2(0, 50))
        }

        """self.camera_script = [
        
            # EXAMPLE OF CAMERA SCRIPT THAT INCLUDES EVERY FUNCTIONALITY EXCEPT IMAGE AND CENTERED TEXT
        
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 0,
                "text": f"Hello Player. Welcome to John's Adventure.",
                "waiting_end": 2000,
                "zoom": 1.4,
                "text_dt": 1000
            },
            {
                "pos": (1100, 225),
                "duration": 1000,
                "waiting_end": 2000,
                "text": "Your quest is waiting for you downstairs.",
                "text_dt": 1000
            },
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 750,
                "waiting_end": 250,
            },
            {
                "duration": 1200,
                "next_cam_status": "follow",
                "zoom": 1,
                "zoom_duration": 1200
            }
        ]"""

        self.camera_script = [
            {
                "no_init": True,  # basically removes the cinema bar init that won't be seen because of black bg
                "duration": 4000,
                "centered_text": "PORTO RAFTH 202X ALTERNATIVE UNIVERSE",
                "centered_text_dt": 2000,
                "image": pg.Surface((1280, 720))
            },
            {
                "duration": 4000,
                "image": scale(l_path("data/sprites/cutscenes/cutscene1.png"), 3)
            },
            {
                "duration": 4000,
                "image": pg.Surface((1280, 720)),
                "centered_text": "THAT'S WHERE YOU PUT YOUR TEXT YOU SUSSIEST",
                "centered_text_dt": 2000,
                "waiting_end": 1000
            },
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 0,
                "text": f"Hello Player. Welcome to John's Adventure.",
                "waiting_end": 4000,
                "zoom": 1.4,
                "text_dt": 2000
            },
            {
                "pos": (1100, 225),
                "duration": 1000,
                "waiting_end": 2000,
                "text": "Your quest is waiting for you downstairs.",
                "text_dt": 1000
            },
            {
                "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
                "duration": 750,
                "waiting_end": 250,
            },
            {
                "duration": 1200,
                "next_cam_status": "follow",
                "zoom": 1,
                "zoom_duration": 1200
            }
        ]

        self.additional_lights = [
            # Windows 
            PolygonLight(pg.Vector2(79 * 3, 9 * 3), 68 * 3, 350, 50, 85, (255, 255, 255), dep_alpha=50, horizontal=True,
                         additional_alpha=175),

            PolygonLight(pg.Vector2(347 * 3, 9 * 3), 68 * 3, 350, 50, 85, (255, 255, 255), dep_alpha=50,
                         horizontal=True, additional_alpha=175),

            # John's Computer
            PolygonLight(pg.Vector2(254 * 3 + 1, 26 * 3), 49 * 3, 150, 25, 125, (89, 144, 135), dep_alpha=185,
                         horizontal=True)
        ]


class Kitchen(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, "kitchen", light_state="inside_clear")
        self.world = pg.transform.scale(load(resource_path('data/sprites/world/kitchen.png')), (1280, 720))
        self.objects = [  # super().load_objects('data/database/levels/kitchen.txt')
            Rect(0, 0, 1280, 133),
            Rect(1270, 134, 10, 586),
            Rect(0, 0, 1280, 133),
            Rect(0, 711, 1280, 9),
            npc.Cynthia((570, 220)),
            Rect(20, 250, 250, 350),
            Rect(280, 300, 64, 256),
            Rect(10, 0, 990, 230),
            Rect(1020, 440, 256, 200)
        ]
        self.exit_rects = {
            "player_room": (pg.Rect(1054, 68, 138, 119), "Back to your room?"),
            "johns_garden": (pg.Rect(551, 620, 195, 99), "Go outside?")
        }
        self.spawn = {
            "player_room": (self.exit_rects["player_room"][0].bottomleft + pg.Vector2(75, 0)),
            "johns_garden": (self.exit_rects["johns_garden"][0].topleft + pg.Vector2(0, -200))
        }
        self.additional_lights = [
            PolygonLight(pg.Vector2(103 * 3, 9 * 3), 68 * 3, 350, 50, 85, (255, 255, 255), dep_alpha=80,
                         horizontal=True, additional_alpha=150),
        ]


class JohnsGarden(GameState):
    """Open world state of the game -> includes john's house, mano's hut, and more..."""

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, "johns_garden", light_state="day")

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
        hills_height = self.sprite_info["hill_mid"]["h"] * self.sprite_info["hill_mid"]["sc"]

        # Use super().load_objects() , when every model is ready
        self.objects = [
            # .prop_objects["box"]((200, 1200)),
            # Fences of john's house (values are calculated for scale = 3 considering this won't change)

            self.prop_objects["hori_fence_rev"](((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100) * jh_sc)),
            self.prop_objects["hori_fence"](((jh_pos[0] - 83) * jh_sc + jh_siz[0], (jh_pos[1] + 100) * jh_sc)),
            self.prop_objects["side_fence"](((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100) * jh_sc)),
            self.prop_objects["side_fence"](
                ((jh_pos[0] - 83 + 233 - 9) * jh_sc + jh_siz[0], (jh_pos[1] + 100) * jh_sc)),
            self.prop_objects["hori_fence_rev"](((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100 + 254) * jh_sc)),
            self.prop_objects["hori_fence"](((jh_pos[0] - 83) * jh_sc + jh_siz[0], (jh_pos[1] + 100 + 254) * jh_sc)),

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
            # cave barrier
            pg.Rect((4826, 6054, 130, 500)),

            # Bottom Cave route
            *self.build_road(start_pos=((jh_pos[0] + 152) * jh_sc, (jh_pos[1] + 2196) * jh_sc),
                             n_road=6, type_r="hori_road", end_type="hori_road_half"),

            *self.build_road(start_pos=((jh_pos[0] + 152) * jh_sc, (jh_pos[1] + 399) * jh_sc),
                             n_road=4, type_r="hori_road", end_type="hori_road_half"),

            # john dirt road
            *self.build_road(start_pos=((jh_pos[0] + 119) * jh_sc, (jh_pos[1] + 279) * jh_sc),
                             n_road=2, start_type="ver_dirt", end_type="ver_sides"),

            *self.build_road(start_pos=((jh_pos[0] + 119) * jh_sc, (jh_pos[1] + 432) * jh_sc),
                             n_road=6, start_type="ver_road", end_type="Vhori_turn"),

            *self.build_road(start_pos=((jh_pos[0] - 702) * jh_sc, (jh_pos[1] + 399) * jh_sc),
                             n_road=4, type_r="hori_road", end_type="hori_road_half"),

            # Out of bounds before Chapter 2 map
            Rect(500, 3600, 100, 10000),
            *self.generate_chunk("tree", 300, 3900, 15, 3, 100 * 3, 100 * 4, randomize=25),
            *self.generate_chunk("grass", 780, 4000, 45, 3, 180, 150, randomize=125),
            # Out of bounds bottom of the map
            Rect(500, 9700, 9500, 100),
            Rect(7600, 7400, 100, 2250),
            Rect(7600, 7400, 1100, 100),

            *self.generate_chunk("grass", 1600, 8900, 2, 23, 210, 120, randomize=75),
            *self.generate_chunk("tree", 1650, 8750, 1, 8, 100 * 6, 0, randomize=5),
            *self.generate_chunk("grass", 300, 9500, 5, 32, 210, 120, randomize=75),
            *self.generate_chunk("tree", 1650, 9150, 2, 8, 100 * 6, 75, randomize=45),

            # Manos dirt road
            *self.build_road(start_pos=((jh_pos[0] - 246) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width,
                                        (jh_pos[1] + 361 - 82) * jh_sc), start_type="ver_dirt", end_type="ver_sides",
                             n_road=2),

            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc), n_road=3, type_r="hori_road",
                             end_type="Vhori_sides"),

            # Route 4
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc + hr_s_height), n_road=3,
                             type_r="ver_road", end_type="Vhori_sides"),
            # Cave Road
            *self.build_road(start_pos=((jh_pos[0] - 247) * jh_sc + 4 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 240 - 49 - 3) * jh_sc + hr_s_height + 2 * vr_r_height),
                             n_road=2,
                             type_r="hori_road"),

            # Hills above the john's and mano's hut
            *self.generate_hills("right", (jh_pos[0] * jh_sc - 600, jh_pos[1] * jh_sc - 250), 8, mid_type="hill_mid",
                                 end_type="none"),
            *self.generate_hills("down",
                                 (jh_pos[0] * jh_sc - 600 + 3 * 224 * 7, jh_pos[1] * jh_sc - hills_height * 7 + 77), 7,
                                 no_begin=True, mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev"),

            # _____TOP_RIGHT_MAP_______
            # Out of bounds 
            Rect(5700, 140 - 150, 5500, 300),

            *self.generate_chunk("tree", 5800, -140, 3, 13, 100 * 4, 140, randomize=25),
            *self.generate_chunk("tree", 5800, 600, 5, 3, 100 * 3, 100 * 4, randomize=25),

            # Collision at the top right of the john's home fenches
            Rect(jh_pos[0] * jh_sc + 224 * 5 + 75, jh_pos[1] * jh_sc + 200, 64, 128),

            # Trees right from john's room
            *self.generate_chunk("tree", jh_pos[0] * jh_sc + 1250, jh_pos[1] * jh_sc, 3, 2, 100 * 4, 100 * 3,
                                 randomize=10),

            # Trees right from manos hut
            *self.generate_chunk("tree", mano_pos[0] * mano_sc + 950, jh_pos[1] * jh_sc, 3, 3, 100 * 4, 100 * 3,
                                 randomize=40),
            # Trees left from manos hut
            *self.generate_chunk("tree", mano_pos[0] * mano_sc - 730, jh_pos[1] * jh_sc, 3, 2, 100 * 4, 100 * 3,
                                 randomize=10),
            # grass details under those trees
            *self.generate_chunk("grass", jh_pos[0] * jh_sc + 1340, jh_pos[1] * jh_sc + 460, 4, 11, 100 * 2, 100 * 2,
                                 randomize=20),

            # Under manos hut     
            *self.generate_chunk("tree", 5700, 6500, 9, 3, 350, 250, randomize=10),
            *self.generate_chunk("tree", 5700, 3800, 9, 3, 350, 250, randomize=10),
            *self.generate_chunk("grass", 5700, 4000, 8, 6, 180, 250, randomize=35),
            *self.generate_chunk("grass", 5700, 6450, 8, 6, 180, 250, randomize=35),

            *self.generate_chunk("grass", 5700, 400, 16, 6, 180, 250, randomize=35),
            *self.generate_chunk("grass", 7000, 350, 2, 26, 180, 120, randomize=35),
            *self.generate_chunk("grass", 7000, 700, 64, 6, 90, 140, randomize=35),

            # "_________________ Right place of the map_________________"
            # Big Hill B
            *self.generate_hills("right", (7200, 720), 6, mid_type="hill_mid", end_type="hill_side_outer_rev"),
            *self.generate_hills("down", (7200, 720), 10, start_type="hill_side_outer", mid_type="hill_side_mid",
                                 end_type="hill_side_outer"),
            *self.generate_hills("right", (7200, 720 + 140 * 3 * 13 + 102), 5, mid_type="hill_mid",
                                 end_type="hill_side_inner_rev"),

            # Route 7 -> Top Right
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc - 3 * vr_r_height),
                             n_road=3, type_r="ver_road"),

            # Route 8 -> Top right of map
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc - 3 * vr_r_height - 33 * 3),
                             n_road=8, type_r="hori_road", start_type="VHhori_turn"),

            # Route 5 Bottom Right
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        (jh_pos[1] + 498 - 3) * jh_sc + hr_s_height * 18), n_road=2,
                             type_r="ver_road", end_type="Hver_turn"),

            # Road that connect bottom cave route with 
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 2,
                                        4994), n_road=5,
                             type_r="ver_road", end_type="VHver_turn"),

            # Route 6 Bottom Right
            *self.build_road(start_pos=((jh_pos[0] - 247 - 1) * jh_sc + 6 * hr_r_width + hhr_r_width + hr_s_width * 3,
                                        (jh_pos[
                                             1] + 361 - 82 + 172 - 50 - 3 - 65) * jh_sc + 2 * hr_s_height + 3 * vr_r_height),
                             n_road=6, type_r="hori_road_half", end_type="Vver_end"),

            # """_________________Cave Borders_________________"""   
            # Top
            *self.generate_hills("right", (jh_pos[0] * jh_sc + 600, jh_pos[1] * jh_sc + 1400), 6, mid_type="hill_mid",
                                 end_type="hill_side_outer_rev"),
            # Bottom   
            *self.generate_hills("right", (jh_pos[0] * jh_sc + 600, jh_pos[1] * jh_sc + 1400 + 160 * 3 * 9 + 102), 6,
                                 mid_type="hill_mid",
                                 end_type="hill_side_outer_rev"),

            # Left Border
            *self.generate_hills("down", (jh_pos[0] * jh_sc + 600, jh_pos[1] * jh_sc + 1400 + 160 * 3 - 102), 8,
                                 no_begin=True,
                                 mid_type="hill_side_mid", end_type="hill_side_outer"),

            # Right up border
            *self.generate_hills("down",
                                 (jh_pos[0] * jh_sc + 600 + 3 * 224 * 5, jh_pos[1] * jh_sc + 1400 + 160 * 3 - 102), 4,
                                 no_begin=True, mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev"),

            # Right down border
            *self.generate_hills("down", (jh_pos[0] * jh_sc + 600 + 3 * 224 * 5,
                                          jh_pos[1] * jh_sc + 1500 + 160 * 3 - 102 + 4 * hills_height),
                                 mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev", n_hills=4,
                                 start_type="hill_side_outer_rev"),
        ]

        # print(F"HOLY F* {len(self.objects)} SURFACES!11")

        self.exit_rects = {
            "kitchen": (pg.Rect((jh_pos[0] + 846 - 728) * jh_sc + 3, (jh_pos[1] + 268) * jh_sc, 100, 60),
                        "Go back to your house?"),
            # pg.Rect(1829*3-200, 888*3+500, 100, 100) -> debug (spawn to manos hut roof) 
            "manos_hut": (pg.Rect((mano_pos[0] + 124) * mano_sc, (mano_pos[1] + 337 - 43 + 12) * mano_sc, 100, 50),
                          "Enter Mano's hut ?"),

            # mandatory forced level switch, useless requires input
            # exit_rects and spawn must have the same keys else the entire level will crash because it wont be found
            "cave_garden": (pg.Rect(5350, 6130, 200, 380), "", "mandatory"),
            "training_field": (pg.Rect(8700, 6680, 600, 800), "", "mandatory"),
            "gymnasium": (pg.Rect(10500, 200, 300, 600), "", "mandatory")
        }
        self.spawn = {
            "kitchen": self.exit_rects["kitchen"][0].bottomleft,
            "manos_hut": self.exit_rects["manos_hut"][0].midbottom,
            "cave_garden": self.exit_rects["cave_garden"][0].midright + pg.Vector2(120, -140),
            "training_field": self.exit_rects["training_field"][0].midleft - pg.Vector2(100, 100),
            "gymnasium": pg.Vector2(10300, 500)
        }

    def update(self, camera, dt):
        pg.draw.rect(self.screen, [60, 128, 0], [0, 0, self.W, self.H])
        update = super().update(camera, dt)
        return update


class Training_Field(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(Training_Field, self).__init__(DISPLAY, player_instance, prop_objects, "training_field",
                                             light_state="day")

        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()
        self.objects = [

            *self.generate_chunk("grass", -600, 600, 20, 25, 120, 150, randomize=45),
            # OUT OF BOUNDS
            Rect(-400, 200, 300, 2600),  # Left
            Rect(2800, 200, 300, 2600),  # Right
            # No need Top, we have the hills
            Rect(-400, 2800, 2600, 300),

            *self.generate_hills("right", (-700, 0), 10, mid_type="hill_mid", end_type="hill_side_outer_rev"),
            *self.build_road((-700, hills_height + 50), n_road=2, start_type="hori_road", end_type="Vver_end"),

            self.prop_objects["feevos_shop"]((1100, 800)),

            # ____ TREES ____
            # Up
            *self.generate_chunk("tree", 300, 200, 2, 10, 250, 180, randomize=30),

            # Right
            *self.generate_chunk("tree", 2200, 722, 4, 3, 250, 400, randomize=30),

            # Down
            *self.generate_chunk("tree", 0, 2200, 2, 8, 400, 250, randomize=50),

            # Left
            *self.generate_chunk("tree", -200, 1000, 4, 2, 150, 400, randomize=50),
            npc.Candy(pg.Vector2(1250, 1470), awake=True),  # Όταν
            npc.Manos(pg.Vector2(1150, 1480)),
            Chest((1630, 1410), {"items": Training_Sword(), "coins": 50}),
            Dummy(self, self.screen, (1850, 1534), self.player),
            Dummy(self, self.screen, (1850, 1734), self.player)
        ]

        self.exit_rects = {
            "johns_garden": (pg.Rect(-100, hills_height - 200, 100, 900), "Go back to open world ?", "mandatory")
        }

        self.spawn = {
            "johns_garden": self.exit_rects["johns_garden"][0].topright + pg.Vector2(100, 280)
        }

        self.sound_manager = SoundManager(True, False, volume=1)
        self.ended_script = True
        self.spawned = False
        self.started_script = False
        self.radius_circles = 0
        self.delay_radius = 0
        self.max_radius = 250
        self.shockwave_radius = 100
        self.exploded = False
        self.centers = [(0, 0), (0, 0)]
        self.dummies = []
        self.camera_script = [
            {
                "duration": 0,
                "pos": (1138, 1526),
                "zoom": 1.2
            },
            {
                "duration": 3000,
                "text": "Manos - Congratulations ! These dummies are dead as fuck !",
                "text_dt": 1500
            },
            {
                "duration": 1500,
                "pos": (1660, 1682)
            },
            {
                "duration": 2500  # at this point, the dummies appear
            },
            {
                "duration": 2000,
                "pos": (1138, 1526),
                "text": "Manos - Oh shit what the hell is that !",
                "text_dt": 1500,
                "zoom": 1,
                "zoom_duration": 1800
            }

        ]

    def update(self, camera, dt):
        pg.draw.rect(self.screen, [60, 128, 0], [0, 0, *self.screen.get_size()])

        if not get_cutscene_played(self.id) and not self.started_script:
            if self.player.game_instance.quest_manager.quests["A new beginning"].quest_state["Talk back to manos"]:
                self.started_script = True
                self.ended_script = False
                self.player.is_interacting = False
                self.player.InteractPoint = 0

        if self.started_script and not self.spawned:
            if self.player.game_instance.cutscene_engine.index_script == 3:
                self.spawned = True
                self.dummies = [ShadowDummy(self, self.screen, (1700, 1540), self.player, hp=150, xp_drop=125),
                                ShadowDummy(self, self.screen, (1700, 1720), self.player, hp=150, xp_drop=125)]
                self.centers = [dummy.rect.center for dummy in self.dummies]
                self.radius_circles += 2
                self.sound_manager.play_sound("magic_shooting")
                self.exploded = True

        update = super(Training_Field, self).update(camera, dt)

        if self.exploded:
            self.shockwave_radius += 100  # vel of shockwave

            # (1000, 1000) = explosion start
            pg.draw.circle(self.screen, (255, 255, 255), pg.Vector2((1000, 1000)) - self.scroll, self.shockwave_radius,
                           width=10)

        if self.spawned and self.radius_circles < self.max_radius and self.dummies == []:
            if pg.time.get_ticks() - self.delay_radius > 40:
                self.radius_circles += 15
                self.delay_radius = pg.time.get_ticks()
            for pos in self.centers:
                pg.draw.circle(self.screen, (128, 0, 128), pg.Vector2(pos) - self.scroll, self.radius_circles, 4)
                pg.draw.circle(self.screen, (255, 255, 255), pg.Vector2(pos) - self.scroll, self.radius_circles + 4, 2)

        # 884 = the distance between explosion start and first dummy
        if self.shockwave_radius > 884 and self.dummies != []:
            self.objects.extend(self.dummies)
            self.dummies = []

        return update


class Gymnasium(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(Gymnasium, self).__init__(DISPLAY, player_instance, prop_objects, "gymnasium", light_state="day")

        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()

        center_spawn = 200

        self.objects = [
            *self.generate_chunk("tree", hills_width // 2 + 20, -hills_height * 3 + 270, 5, 2, 400, 320, randomize=45),

            # Right side trees
            *self.generate_chunk("tree", hills_width * 6, -hills_height * 3 + 270, 5, 3, 450, 320, randomize=45),
            *self.generate_chunk("grass", -100, -1000, 13, 8, 150, 60, randomize=125),
            *self.generate_chunk("grass", 4200, -860, 10, 10, 80, 80, randomize=125),
            *self.generate_hills("right", (-400, center_spawn), 10, mid_type="hill_mid",
                                 end_type="hill_side_outer_rev"),

            # Weird bug, temp patch
            # The road turns 90 degrees on the end if I add more than 2 roads that use Vver_end,
            # so I made 2 on top of each othet
            *self.build_road(
                start_pos=(-600, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end"
            ),

            *self.build_road(
                start_pos=(350, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end"
            ),

            *self.build_road(
                start_pos=(1320, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end"
            ),

            # ___OUT_OF_BOUNDS
            Rect(5160, -900, 50, 2100),  # Right
            Rect(40, -900, 50, 2100),  # Left
            Rect(40, -900, hills_width * 8, 50),  # Up

            self.prop_objects["school_entrance"]((hills_width * 2 - 150, -hills_height * 2 + 30)),
            *self.generate_chunk('h_ladder', x=4970, y=-200, row=1, col=1, step_x=0, step_y=0, randomize=0),
            npc.Bababooye(pg.Vector2(2702, -75))
        ]

        self.exit_rects = {
            "johns_garden": (pg.Rect(-100, -center_spawn - 121, 300, 600), "Go back to open world ?", "mandatory"),
            "cave_passage": (pg.Rect(4970, -200, 64, 64), "Are you sure you want to get in ?")
        }

        self.spawn = {
            "johns_garden": (300, 0),
            "cave_passage": (4750, -150)
        }

    def update(self, camera, dt):
        pg.draw.rect(self.screen, [60, 128, 0], [0, 0, *self.screen.get_size()])
        print(self.player.rect.topleft)
        return super(Gymnasium, self).update(camera, dt)


class ManosHut(GameState):

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(DISPLAY, player_instance, prop_objects, "manos_hut", light_state="inside_dark")
        self.world = pg.transform.scale(l_path('data/sprites/world/manos_hut.png'), (1280, 720))
        sc_x = 1280 / 453
        sc_y = 720 / 271
        self.objects = [
            Rect(-40, 0, 40, 720),  # Left borders
            Rect(1270, 134, 40, 586),  # Right borders
            Rect(0, 4 - 0, 1280, 133 + 40),  # Up borders
            Rect(0, 711, 1280, 40),  # Down borders
            npc.Manos(pg.Vector2(235 * sc_x, 115 * sc_y), (300, 100)),
            npc.Candy(pg.Vector2(205, 395)),
            Chest((422 * sc_x, 47 * 4 * sc_y - 45), {"items": Knight_Sword(), "coins": 30}),
            self.prop_objects["m_hut_bed"]((381 * sc_x, 47 * sc_y)),
            self.prop_objects["m_hut_sofa"]((97 * sc_x, 88 * sc_y)),
            self.prop_objects["m_hut_table"]((163 * sc_x, 37 * sc_y)),
            self.prop_objects["m_hut_fireplace"]((5 * sc_x, (193 - 236) * sc_y)),
            # ShadowDummy(self, self.screen, (600, 600), self.player)
        ]

        self.spawn = {
            "johns_garden": (630, 490)
        }

        self.exit_rects = {
            "johns_garden": (pg.Rect(560, 635, 150, 75), "Go back to open world ?")
        }


class CaveGarden(GameState):

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveGarden, self).__init__(DISPLAY, player_instance, prop_objects, "cave_garden", light_state="day")
        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()

        self.objects = [
            # The chunk cut in 4 pieces for easyness 
            *self.generate_chunk("grass", 240 * 3, 160 * 9, 14, 11, 120, 100, randomize=30),
            *self.generate_chunk("grass", 240 * 3, 160 * 19, 14, 11, 120, 100, randomize=30),
            *self.generate_chunk("grass", 2060, 160 * 9, 14, 11, 120, 100, randomize=30),
            *self.generate_chunk("grass", 2060, 160 * 19, 14, 11, 120, 100, randomize=30),

            *self.generate_chunk("cave_spike", 2060, 160 * 17 + 30, 1, 3, 150, 0, randomize=10),
            *self.generate_chunk("cave_spike_small", 2150, 160 * 17 + 80, 1, 3, 150, 0, randomize=10),

            *self.generate_chunk("cave_spike", 2080, 160 * 17 + 220, 1, 3, 150, 0, randomize=10),
            *self.generate_chunk("cave_spike_small", 2150, 160 * 17 + 220 + 30, 1, 3, 150, 0, randomize=10),

            *self.build_road(start_pos=(2040, 2865),
                             n_road=2, type_r="hori_road", end_type="hori_road"),
            # """_________________Cave Borders_________________"""   
            # Top
            *self.generate_hills("right", (0, 160 * 3 * 2), 6, mid_type="hill_mid",
                                 end_type="hill_side_outer_rev"),
            # Bottom   
            *self.generate_hills("right", (0, 160 * 3 * 9 + 102), 6, mid_type="hill_mid",
                                 end_type="hill_side_outer_rev"),

            # Left Border
            *self.generate_hills("down", (0, 160 * 3 - 102), 8, no_begin=True,
                                 mid_type="hill_side_mid", end_type="hill_side_outer"),

            # Right up border
            *self.generate_hills("down", (0 + 3 * 224 * 5, 160 * 3 - 102), 5,
                                 no_begin=True, mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev"),

            # Right down border
            *self.generate_hills("down", (0 + 3 * 224 * 5, 160 * 3 - 102 + 4 * hills_height),
                                 mid_type="hill_side_mid_rev", end_type="hill_side_inner_rev", n_hills=5,
                                 start_type="hill_side_outer_rev"),

            self.prop_objects["cave_entrance"]((hills_width + 100, hills_height * 4 - 255)),

            *self.generate_chunk("tree", hills_width * 3 - 50, hills_height * 2 - 50, 4, 3, 100 * 5, 100 * 3),
            *self.generate_chunk("tree", hills_width, hills_height * 2 - 50, 3, 3, 100 * 4, 100 * 3),
            *self.generate_chunk("tree", hills_width + 10, 3350, 3, 3, 100 * 4, 100 * 3),
            *self.generate_chunk("tree", 2100, 2970, 4, 3, 100 * 4, 100 * 3)
        ]

        self.spawn = {
            "johns_garden": (hills_width * 5 - 100, hills_height * 4 + 100),
            "cave_entrance": (2150, 2830)
        }

        self.exit_rects = {
            "johns_garden": (
                pg.Rect(hills_width * 5 + 50, hills_height * 4, 200, 400),
                "", "mandatory"
            ),
            "cave_entrance": (
                pg.Rect(hills_width * 3, hills_height * 4 + 177, 100, 100),
                "Get inside the cave ?"
            )
        }

    def update(self, camera, dt):
        pg.draw.rect(self.screen, (60, 128, 0), [0, 0, *self.screen.get_size()])
        return super(CaveGarden, self).update(camera, dt)


class CaveEntrance(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveEntrance, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_entrance",
            light_state="inside_dark"
        )

        self.spawn = {
            "cave_entrance": (
                self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width() * 3 + 50,
                self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width() * 4 + 100
            ),

            "cave_garden": (1300, 100),

            "cave_room_1": (-2400, 120)
        }

        self.objects = \
            [
                *self.generate_cave_walls(
                    direction="right",
                    dep_pos=self.spawn['cave_garden'] - vec(1350 * 4, self.spawn['cave_garden'][1] * 2),
                    n_walls=14,
                    start_type="c_wall_corner",
                    end_type="c_flipped_corner",
                ),

                *self.generate_cave_walls(
                    direction="right",
                    dep_pos=self.spawn['cave_garden'] - vec(1350 * 4, -self.spawn['cave_garden'][1] * 2),
                    n_walls=14,
                    start_type="c_wall_corner_turn",
                    end_type="c_flipped_corner"
                ),
                # Since cave exit is optional, I need to add a bound
                Rect(1400 + 140, self.spawn['cave_garden'][1], 150, 300),
                Rect(-(2700 + 140), self.spawn['cave_garden'][1], 150, 300)
            ]

        self.exit_rects = {

            "cave_garden": (
                pg.Rect(
                    1400,
                    self.spawn['cave_garden'][1],
                    150, 300
                ),
                "Go back to open world ?"
            ),

            "cave_room_1": (
                pg.Rect(
                    -2700, self.spawn['cave_garden'][1],
                    150, 300
                ),
                "", "mandatory"
            )
        }

        self.additional_lights = [

            PolygonLight(
                vec(1400, self.spawn['cave_garden'][1] + 40),
                68 * 3,  # height
                350,  # radius
                50,  # dep_angle
                85,  # end_angle
                (255, 255, 255),  # color
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175
            )
        ]

    def update(self, camera, dt):
        # Background
        pg.draw.rect(self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()])

        # Top void
        pg.draw.rect(self.screen, (0, 0, 0),
                     [
                         *(vec(-3200, -335) - vec(self.scroll))
                         , 5350, 400
                     ]
                     )

        # Flashlight
        pg.draw.circle(
            self.screen,
            (240, 240, 240, 30),
            (self.screen.get_width() // 2 + 20, self.screen.get_height() // 2 + 92),
            70
        )

        # Bottom and left void (it would be best if we could blit it after the cave objects)
        pg.draw.rect(self.screen, (0, 0, 0),
                     [
                         *(vec(-3200, 335) - vec(self.scroll))
                         , 5350, 400
                     ]
                     )

        return super(CaveEntrance, self).update(camera, dt)


class CaveRoomOne(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveRoomOne, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_room_1",
            light_state="inside_dark"
        )

        self.player.DEFAULT_VEL = 30

        w = self.prop_objects['c_wall_mid']((0, 0)).idle[0].get_width()
        h = (self.prop_objects['c_wall_side']((0, 0)).idle[0].get_width() * 3 * 2) + 23

        self.objects = \
            [
                # Borders
                *self.generate_wall_chunk(n=12, pos=(-300, -300), x_side=6),

                # Right side of the map
                *self.generate_wall_chunk(n=5, pos=(-300 + (18-5) * w, -300), up_side=False, right_side=False, d_n=1, l_n=1),
                *self.generate_wall_chunk(n=5, pos=(-300 + (18-5) * w, 1300), down_side=False, right_side=False, u_n=1),

                # Right-bottom left room
                *self.generate_cave_walls(
                    direction="down", n_walls=5, door_n=1, dep_pos=((18 - 3) * w - w // 2 - 160, 1300),
                    start_type="none", end_type="none", no_begin=True
                ),

                *self.generate_cave_walls(
                    direction="down", n_walls=5, door_n=1, dep_pos=((18 - 2) * w - w//2, 1300),
                    start_type="none", end_type="none", no_begin=True
                ),

                *self.generate_cave_walls(
                    direction="down", n_walls=5, door_n=1, dep_pos=((18 - 2) * w - w // 2, -384),
                    start_type="none", end_type="none", no_begin=True
                ),

                # Left side

                *self.generate_cave_walls(
                    direction="right", n_walls=13, door_n=[2, 9], dep_pos=(-270, 900),
                    start_type="none", end_type="c_flipped_corner", no_begin=True
                ),

                # This one has a 'layering' issue
                *self.generate_cave_walls(
                    direction="down", n_walls=5, door_n=1, dep_pos=((18 - 6) * w + 174, 1000),
                    start_type="none", end_type="none", no_begin=True
                ),  # draw over the above broken block


                *self.generate_cave_walls(
                    direction="down", n_walls=4, dep_pos=(6 * w, -200),
                    start_type="none", end_type="none", no_begin=True
                ),

                *self.generate_cave_walls(
                    direction="down", n_walls=5, dep_pos=(6 * w, -320),
                    start_type="none", end_type="none", no_begin=True
                ),

                *self.generate_cave_walls(
                    direction="down", n_walls=4, dep_pos=(1000,  900),
                    start_type="none", end_type="none", no_begin=True
                ),

                *self.generate_cave_walls(
                    direction="down", n_walls=4, dep_pos=(1750, 900),
                    start_type="none", end_type="none", no_begin=True
                ),
            ]

        self.spawn = {
            "cave_entrance": (8000, 1160),
        }
        self.exit_rects = {
            "cave_room_2": (pg.Rect(800, 100, 150, 200), "", "mandatory"),
            "cave_entrance": (pg.Rect(8100, 1112, 150, 280), "", "mandatory")
        }

    def update(self, camera, dt):
        print("floor 1")
        # Background
        pg.draw.rect(self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()])

        print(self.player.rect.center)

        pg.draw.circle(  # Flashlight
            self.screen,
            (240, 240, 240, 30),
            (self.screen.get_width() // 2 + 20, self.screen.get_height() // 2 + 92),
            70
        )

        return super(CaveRoomOne, self).update(camera, dt)


class CaveRoomTwo(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveRoomTwo, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_room_2",
            light_state="inside_dark"
        )

        self.objects = \
            [
                *self.generate_wall_chunk(n=12, pos=(-300, -300), x_side=6),
            ]

        self.spawn = {
            "cave_room_1": (0, 0),
            "cave_passage": (860, 200)
        }

        self.exit_rects = {
            "cave_passage": (pg.Rect(800, 100, 150, 140), "", "mandatory")
        }

    def update(self, camera, dt):
        # Background
        pg.draw.rect(self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()])

        # Flashlight
        pg.draw.circle(
            self.screen,
            (240, 240, 240, 30),
            (self.screen.get_width() // 2 + 20, self.screen.get_height() // 2 + 92),
            70
        )

        return super(CaveRoomTwo, self).update(camera, dt)


class CaveRoomPassage(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveRoomPassage, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_passage",
            light_state="inside_dark"
        )

        self.spawn = {
            "cave_room_2": (880, 2100),
            "gymnasium": (783, 730)
        }

        w = self.prop_objects['c_wall_mid']((0, 0)).idle[0].get_width()

        self.objects = \
            [

                *self.generate_cave_walls(
                    direction="right",
                    dep_pos=(300, 300),
                    n_walls=2,
                    start_type="c_wall_corner_turn",
                    end_type="c_flipped_corner_turn",
                ),

                *self.generate_cave_walls(
                    direction="down",
                    dep_pos=(300, 300),
                    n_walls=8,
                    no_begin=True,
                    start_type="none",
                    end_type="none",
                ),

                *self.generate_cave_walls(
                    direction="down",
                    dep_pos=(800 + 150 + 300 - 32, 300),
                    n_walls=8,
                    no_begin=True,
                    start_type="none",
                    end_type="none",
                ),

                *self.generate_cave_walls(
                    direction="right",
                    dep_pos=(300, (w * 6) + 1),
                    n_walls=2,
                    start_type="c_wall_corner",
                    end_type="c_flipped_corner",
                ),


                *self.generate_chunk('ladder', x=770, y=300, row=1, col=1, step_x=0, step_y=0, randomize=0)

            ]

        self.exit_rects = {
            "gymnasium": (pg.Rect(732, 530, 150, 140), "Are you sure you want to exit the cave ?"),
            "cave_room_2": (
                pg.Rect(
                    726,
                    self.spawn['cave_room_2'][1] + 620,
                    150,
                    140),
                "", "mandatory"
            ),
        }

        self.additional_lights = [

            PolygonLight(
                vec(800, 300),
                68 * 3,  # height
                350,  # radius
                50,  # dep_angle
                85,  # end_angle
                (255, 255, 255),  # color
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175
            )
        ]

    def update(self, camera, dt):
        # Background
        pg.draw.rect(self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()])

        print(self.player.rect.topleft)

        # Flashlight
        pg.draw.circle(
            self.screen,
            (240, 240, 240, 30),
            (self.screen.get_width() // 2 + 20, self.screen.get_height() // 2 + 92),
            70
        )

        pg.draw.rect(self.screen, (0, 0, 0),
                     [
                         *(vec(-294, -335) - vec(self.scroll))
                         , 600, 4000
                     ]
                     )

        pg.draw.rect(self.screen, (0, 0, 0),
                     [
                         *(vec(1244, -335) - vec(self.scroll))
                         , 600, 4000
                     ]
                     )

        return super(CaveRoomPassage, self).update(camera, dt)
