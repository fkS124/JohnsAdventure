import pygame as pg
from pygame import Rect

from .PLAYER.items import Chest
from .PLAYER.player import *
from .PLAYER.inventory import *
from .AI.enemies import Dummy
from .AI import npc
from .utils import resource_path, load


class GameState:

    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        # ------- SCREEN -----------------
        self.display, self.screen = DISPLAY, DISPLAY
        self.W, self.H = self.display.get_size()

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj

        self.objects = []
        self.world = pg.Surface((1, 1))  # set default values for world -> supposed to be replaced

        # eg. -> "next_state_name" : pg.Rect(0, 0, 100, 100)
        self.exit_rects = {}  # the rects that lead to exit the current room

    def collision_system(self, obj):
        """
        Top,
        Bottom,
        Left,
        Right

        Checks for collision before input,
        else it will go throught the object and then do the calc
        """
        t = abs(obj.bottom - self.player.rect.top)
        b = abs(obj.top - self.player.rect.bottom)
        l = abs(obj.right - self.player.rect.left)
        r = abs(obj.left - self.player.rect.right)
        if self.player.rect.colliderect(obj):
            if self.player.Up or self.player.Down:  # Up / Down borders
                if t < 10:
                    self.player.y += self.player.speedY
                elif b < 10:
                    self.player.y -= self.player.speedY # Clunky
            if self.player.Left or self.player.Right:  # Left / Right borders
                if l < 10:
                    self.player.x += self.player.speedX
                elif r < 10:
                    self.player.x -= self.player.speedX # Clunky


    def update(self, camera):

        # update the game values
        self.player.rooms_objects = self.objects

        # display background
        self.display.blit(self.world, -camera.offset.xy)

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
            pass
            # Find the NPC
            #if type(obj) is not pg.Rect:
                #obj.update(*[getattr(self, arg) for arg in obj.update.__code__.co_varnames[1:obj.update.__code__.co_argcount]])
                #self.collision_system(obj.Rect)
            # Its Furtniture or Borders
            #else:
                #self.collision_system(obj)


        # MUST BE REWORKED -> supposed to track if the player is interacting with exit rects
        for exit_state, exit_rect in self.exit_rects.items():
            exit_rect = pg.Rect(exit_rect.x, exit_rect.y, *exit_rect.size)
            if self.player.rect.colliderect(exit_rect):
                if self.player.InteractPoint == 2:
                    return exit_state


class PlayerRoom(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        super().__init__(DISPLAY, player_instance)

        self.objects = [
            #npc.NPCS.Mau(150,530),
            #Rect(10,90, 430,360),
            #Rect(5,500, 72, 214),
            #Rect(450, 40, 410, 192),
            #Dummy(DISPLAY, (1050, 300))
        ]
        self.world = pg.transform.scale(load(resource_path('data/sprites/world/Johns_room.png')), (1280, 720))

        self.exit_rects = {
            "kitchen": pg.Rect(self.W // 2 + 353, 150, 155, 130)
        }


class Kitchen(GameState):

    def __init__(self, DISPLAY:pg.Surface, player_instance):

        super().__init__(DISPLAY, player_instance)

        self.world = pg.transform.scale(load(resource_path('data/sprites/world/kitchen.png')), (1280,720))  # 1 Kitchen Room
        self.objects = [
            npc.NPCS.Cynthia(570, 220),
            Chest(960,175, 0),
            Rect(20, 250, 250,350),
            Rect(280,300, 64, 256),
            Rect(10,0, 990, 230),
            Rect(1020, 440, 256, 200)
        ]

        self.exit_rects = {
            "player_room": pg.Rect(1005, 0, 1280-1005, 240)
        }
