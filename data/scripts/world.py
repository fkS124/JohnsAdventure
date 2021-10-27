'''
Credits @Marios325346, @ƒkS124

This script contains our lovely npcs!


'''

from .PLAYER.items import Chest
import sys, json
import pygame as pg
from .backend import UI_Spritesheet
from .PLAYER.player import *
from .PLAYER.inventory import *
from .AI.enemies import Dummy
from .sound_manager import SoundManager
from .AI import npc
from .UI.mainmenu import Menu
from .UI.interface import Interface
from .UI.loading_screen import LoadingScreen
from .utils import resource_path

from .levels import (
    PlayerRoom,
    Kitchen
)

'''

Anything related to pygame window below will move to main.py for organization

'''
pg.mixer.pre_init(44100, 32, 2, 4096) # Frequency, 32 Bit sound, channels, buffer
pg.init(), pg.display.set_caption("iBoxStudio Engine Pre Alpha 0.23")
DISPLAY = pg.display.set_mode((1280, 720), flags= p.SRCALPHA)

#  Uncomment the below when you stop debugging
#DISPLAY = pg.display.set_mode((1280, 720), flags=pg.RESIZABLE | pg.SCALED)  # pg.NOFRAME for linux :penguin:
#pg.display.toggle_fullscreen()

if '--debug' in sys.argv:
    print("Oh you sussy you're trying to debug me huh?")
    debug = True
else:
    debug = False

# INITIALIZE
framerate = pg.time.Clock()
get_screen_w, get_screen_h = DISPLAY.get_width(), DISPLAY.get_height()
scroll = [0, 0]  # player "camera"
dt = framerate.tick(35) / 1000 # Delta time :D

font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 24)
blacksword = pg.font.Font(resource_path("data/database/Blacksword.otf"), 113) # I use this only for the logo
pg.mouse.set_visible(True)


ui = UI_Spritesheet("data/ui/UI_spritesheet.png")


def main():
    GameManager().update()


class GameManager:

    """

    Game class -> handles everything of the game.

    """
    
    # CONSTS
    DISPLAY = DISPLAY
    W = get_screen_w
    H = get_screen_h
    FPS = 35

    # FONTS
    font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 24)
    blacksword = pg.font.Font(resource_path("data/database/Blacksword.otf"), 113)

    def __init__(self):

        # ------------- SPRITESHEET ---------------
        self.ui = UI_Spritesheet("data/ui/UI_spritesheet.png")

        # ------------ FRAMERATE ------------------
        self.framerate = pg.time.Clock()
        self.dt = self.framerate.tick(self.FPS) / 1000

        # ----------- GAME STATE VARIABLES --------
        self.scroll = [0, 0]
        self.menu = True
        self.loading = False

        # ---------- GAME MANAGERS ----------------
        self.sound_manager = SoundManager()
        self.loading_screen = LoadingScreen(self.DISPLAY)
        self.menu_manager = Menu(self.DISPLAY, self.blacksword, self.ui)
        self.interface = Interface(self.DISPLAY, self.ui, self.font, self.dt)


        # ------------- PLAYER ----------------
        self.player = Player(
        self.DISPLAY, # Screen surface
        font, # Font
        self.interface,
        self.ui, # Other UI like Inventory
        self.menu_manager.save, # controls
        )

        # ----------- GAME STATE ------------------
        self.state = "player_room"
        self.state_manager = {
            "player_room": PlayerRoom(self.DISPLAY, self.player),
            "kitchen": Kitchen(self.DISPLAY, self.player)
        }

    def pause(self):

        # REWORK NEEDED

        pass

    def routine(self):

        """Method called every frame of the game.
        (Created to simplify the game loop)"""

        self.dt = self.framerate.tick(self.FPS) / 1000

        if not self.menu and not self.loading:  # if the game is playing
            self.player.update(self.dt)
            self.pause()

        pg.display.update()

    def update(self):

        while True:

            if self.menu:  # menu playing

                self.menu_manager.update(pg.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = True
                    self.loading_screen.start("player_room", duration=2500, main_loading=True, cat=True, text=False, key_end=True)

            elif self.loading:  # update the loading screen

                update_return = self.loading_screen.update()
                if update_return is not None:
                    self.state = update_return["next_state"]
                    self.loading = False
                    if update_return["next_music"] is not None:
                        self.sound_manager.play_music(update_return["next_music"])

            else:
                self.DISPLAY.fill((0, 0, 0))
                update = self.state_manager[self.state].update(self.player.camera)
                if update is not None:  # if a change of state is detected
                    self.loading = True  # start a loading screen (update="next_state_name")
                    self.loading_screen.start(update, text=True, duration=750)
                    if self.state in self.state_manager[update].spawn:
                        self.player.rect.topleft = self.state_manager[update].spawn[self.state]

            self.routine()
