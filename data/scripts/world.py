from copy import copy
import pygame as pg
from .backend import UI_Spritesheet
from .PLAYER.player import Player
from .PLAYER.inventory import *
from .AI.enemies import Dummy
from .sound_manager import SoundManager
from .AI import npc
from .UI.mainmenu import Menu
from .UI.interface import Interface
from .UI.loading_screen import LoadingScreen
from .UI.pause_menu import PauseMenu
from .utils import resource_path, l_path
from .props import PropGetter, init_sheets, del_sheets
from threading import Thread
from pympler import asizeof, summary
import gc

from .levels import (
    GameState,
    PlayerRoom,
    Kitchen,
    JohnsGarden,
    ManosHut
)


def main(debug=False, first_state="player_room", no_rect=False):
    return GameManager(debug=debug, first_state=first_state, no_rect=no_rect)


class GameManager:
    """

    Game class -> handles everything of the game.

    """
    pg.init()

    # FONTS

    pg.mixer.pre_init(44100, 32, 2, 4096)  # Frequency, 32 Bit sound, channels, buffer
    pg.display.set_caption("iBoxStudio Engine Pre Alpha 0.23")
    pg.mouse.set_visible(False)
    # CONSTS

    DISPLAY = pg.display.set_mode((1280, 720),
                                  flags=pg.SCALED)  # | pg.SCALED | pg.DOUBLEBUF | pg.FULLSCREEN | pg.NOFRAME

    pg.display.set_icon(l_path("data/ui/logo.png", True))
    W, H = DISPLAY.get_size()

    FPS = 35

    def __init__(self, debug=False, first_state="player_room", no_rect=False):

        # ------------- SPRITESHEET ---------------
        self.ui = UI_Spritesheet("data/ui/UI_spritesheet.png")

        # ------------ FRAMERATE ------------------
        self.framerate = pg.time.Clock()
        self.dt = self.framerate.tick(self.FPS) / 1000

        # ----------- GAME STATE VARIABLES --------
        self.menu = True
        self.loading = False

        # 
        self.font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 24)
        self.blacksword = pg.font.Font(resource_path("data/database/Blacksword.otf"), 113)

        # pygame powered
        self.pygame_logo = l_path("data/sprites/pygame_powered.png", alpha=True)
        self.start_logo_time = pg.time.get_ticks()
        self.pg_logo = False
        self.start_scale = 1
        self.current_scale = 0
        self.delay_scaling = 0

        # ---------- GAME MANAGERS ----------------
        self.sound_manager = SoundManager()
        self.loading_screen = LoadingScreen(self.DISPLAY)
        self.menu_manager = Menu(self.DISPLAY, self.blacksword, self.ui)
        self.interface = Interface(self.DISPLAY, scale(self.ui.parse_sprite('interface_button.png'), 8))
        self.pause_menu = PauseMenu(self.DISPLAY, self.ui)

        # ------------- PLAYER ----------------
        self.player = Player(
            self.DISPLAY,  # Screen surface
            self.font,  # Font
            self.interface,
            self.ui,  # Other UI like Inventory
            self.menu_manager.save,  # controls
        )

        # ----------- GAME STATE ------------------
        self.state = first_state
        self.first_state = False
        self.prop_objects = PropGetter(self.player).PROP_OBJECTS
        self.state_manager = {
            "player_room": PlayerRoom,
            "kitchen": Kitchen,
            "johns_garden": JohnsGarden,
            "manos_hut": ManosHut,
        }
        self.game_state: GameState = None

        # ------------ DEBUG ----------------------
        self.debug = debug
        self.debugger = Debugging(self.DISPLAY, self, no_rect)

        # -------- CAMERA SRC HANDLER -------------
        self.s_duration = 0
        self.s_next_cam = None
        self.scripting = False
        self.s_dt_to_wait_on_end = 0
        self.end = 0
        self.ended = False

    def pause(self):
        if self.player.paused:
            self.pause_menu.init_pause()
            while True:
                upd = self.pause_menu.update()

                if upd == "quit":
                    self.pause_menu.quit_pause()
                    self.menu = True
                    del self.game_state
                    self.player.paused = False
                    self.menu_manager.start_game = False
                    break
                elif upd == "resume":
                    self.pause_menu.quit_pause()
                    self.player.paused = False
                    break

                pg.display.update()

    def routine(self):

        """Method called every frame of the game.
        (Created to simplify the game loop)"""

        self.dt = self.framerate.tick(self.FPS) / 1000

        if not self.menu and not self.loading:  # if the game is playing
            self.player.user_interface(pg.mouse.get_pos(), (
                # 52 48 are players height and width
                self.player.rect.x - 52 - self.player.camera.offset.x,
                self.player.rect.y - self.player.camera.offset.y - 48
                ), 
                self.dt # <- is needed for the NPC interaction
            ) 
            self.pause()
            self.player.camera.method.draw()

        if self.debug:
            self.debugger.update()

        pg.display.update()

    def pg_loading_screen(self):
        while pg.time.get_ticks() < 3000:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    raise SystemExit

            self.DISPLAY.fill((255, 255, 255))

            if pg.time.get_ticks() - self.delay_scaling > 25 and self.start_scale - self.current_scale > 0.75:
                self.delay_scaling = pg.time.get_ticks()
                self.current_scale += 0.1

            scale_ = self.start_scale - self.current_scale
            img = scale(self.pygame_logo, scale_)
            self.DISPLAY.blit(img, img.get_rect(center=(self.W // 2, self.H // 2)))

            if pg.time.get_ticks() - self.start_logo_time > 700:
                self.DISPLAY.blit(self.font.render("@Copyright Logo by www.pygame.org", True, (0, 0, 0)),
                                  img.get_rect(topleft=(self.W // 2 - 320, self.H // 2 + 230)))

            self.framerate.tick(self.FPS)
            pg.display.update()

    def start_new_level(self, level_id, last_state="none", first_state=False):

        if hasattr(self, "game_state"):
            if self.game_state is not None:
                self.game_state.objects.clear()
            del self.game_state
            gc.collect()
        self.state = level_id

        init_sheets()

        def load_new_level(parent, level_):
            print("Started loading thread :", level_)
            print(parent.state_manager[level_])
            parent.game_state = parent.state_manager[level_](parent.DISPLAY, parent.player, parent.prop_objects)
            print("Loading thread terminated.")

        loading_thread = Thread(target=load_new_level, args=(self, level_id))
        loading_thread.start()

        while loading_thread.is_alive():

            for event in pg.event.get():

                if event.type == pg.QUIT:
                    del loading_thread
                    pg.quit()
                    raise SystemExit

            self.DISPLAY.fill((255, 0, 0))

            pg.display.update()

        if last_state == "none":
            keys = [key for key in self.game_state.spawn]
            self.player.rect.topleft = self.game_state.spawn[keys[0]]
        else:
            self.player.rect.topleft = self.game_state.spawn[last_state]

        if first_state and not self.debug:
            self.player.rect.topleft = (self.DISPLAY.get_width() // 2 - 120, self.DISPLAY.get_height() // 2 - 20)
            self.first_state = True

        self.game_state.lights_manager.init_level(self.game_state)
        del_sheets()

    def update(self):

        """

            FOR DEBUGGING MEASURES, ELSE RUN THE GAME NORMAL

        """
        if not self.debug:
            self.pg_loading_screen()
        else:
            self.start_new_level(self.state, first_state=True)
            self.menu = False
            self.loading = False

        while True:

            if self.menu:  # menu playing

                self.menu_manager.update(pg.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = False

                    self.start_new_level(self.state, first_state=not self.first_state)

            else:
                self.DISPLAY.fill((0, 0, 0))
                update = self.game_state.update(self.player.camera, self.dt)
                if update is not None:  # if a change of state is detected
                    self.start_new_level(update, last_state=self.state)

                '''  RUN THE CAMERA ONLY WHEN ITS NOT IN DEBUGGING MODE  '''
                if not self.game_state.ended_script and not self.debug:
                    self.camera_script_handler()
                else:
                    self.player.set_camera_to("follow")

            self.routine()

    def start_new_src_part(self):

        c_level = self.game_state
        cam_script = c_level.camera_script
        src_index = c_level.cam_index

        self.player.set_camera_to("auto")
        self.scripting = True
        self.ended = False

        cur_script = cam_script[src_index]
        if "pos" in cur_script and "duration" in cur_script:
            self.player.camera.method.go_to(cur_script["pos"], duration=cur_script["duration"])
        self.s_next_cam = cur_script["next_cam_status"] if "next_cam_status" in cur_script else None
        self.player.camera.method.set_text(cur_script["text"] if "text" in cur_script else "")
        self.s_dt_to_wait_on_end = cur_script["waiting_end"] if "waiting_end" in cur_script else 0
        if "zoom" in cur_script:
            if "zoom_duration" not in cur_script:
                self.player.camera.method.fov = cur_script["zoom"]
            else:
                self.player.camera.method.start_zoom_out(cur_script["zoom"], cur_script["zoom_duration"])

        # print("Started:", src_index, "w:", self.s_dt_to_wait_on_end, "dt:", cur_script["duration"], cur_script["pos"])

    def camera_script_handler(self):
        c_level = self.game_state
        cam_script = c_level.camera_script
        src_index = c_level.cam_index
        camera = self.player.camera

        if not self.scripting:
            if src_index + 1 < len(cam_script):
                self.game_state.cam_index += 1
                self.start_new_src_part()
            else:
                self.game_state.ended_script = True
                return

        if not camera.method.moving_cam and not camera.method.zooming_out and not self.ended:
            self.end = pg.time.get_ticks()
            self.ended = True

        if self.ended:
            if self.s_dt_to_wait_on_end != 0:
                if pg.time.get_ticks() - self.end > self.s_dt_to_wait_on_end:
                    self.scripting = False
                    if self.s_next_cam is not None:
                        self.player.set_camera_to(self.s_next_cam)
            else:
                self.scripting = False
                if self.s_next_cam is not None:
                    self.player.set_camera_to(self.s_next_cam)


class Debugging:

    def __init__(self, display, game_instance, no_rect):

        self.no_rect = no_rect
        self.screen = display
        self.game = game_instance
        self.player = self.game.player

        self.colors = {
            "interaction_rect": (255, 255, 0),
            "collision_rect": (0, 255, 0),
            "attacking_rect": (255, 0, 0),
            "exit_rect": (255, 255, 0)
        }

        self.font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 15)

    def draw_text(self, txt, color, pos, bottomleft=False):
        text = self.font.render(txt, True, color)
        rect = text.get_rect(topleft=pos)
        if bottomleft:
            rect.bottomleft = pos
        self.screen.blit(text, rect)

    def update(self):

        """Primitive debugging system showing rects.
        
        TODO: Improve it to show stats. And make it more readable."""

        if not self.no_rect:
            if not self.game.menu and not self.game.loading:
                scroll = self.player.camera.offset.xy
                objects = copy(self.game.game_state.objects)
                objects.append(self.player)

                for obj in objects:
                    if type(obj) is pg.Rect:
                        pg.draw.rect(self.screen, self.colors["collision_rect"],
                                     pg.Rect(obj.topleft - self.player.camera.offset.xy, obj.size), 2)
                    else:
                        for key, color in self.colors.items():
                            if hasattr(obj, key):
                                attr = (getattr(obj, key))
                                if type(attr) is pg.Rect:
                                    pg.draw.rect(self.screen, color, attr, 1)

                        col_rect = copy(obj.rect)
                        if hasattr(obj, "IDENTITY"):
                            if obj.IDENTITY in ["NPC", "PROP"]:
                                col_rect.topleft -= scroll
                            if hasattr(obj, "d_collision"):
                                col_rect.topleft += pg.Vector2(*obj.d_collision[:2])
                                col_rect.size = obj.d_collision[2:]
                            pg.draw.rect(self.screen, self.colors["collision_rect"], col_rect, 2)

                exit_rects = self.game.game_state.exit_rects
                for exit_rect in exit_rects:
                    r = copy(exit_rects[exit_rect][0])
                    r.topleft -= scroll
                    pg.draw.rect(self.screen, self.colors["exit_rect"], r, 2)
                    self.draw_text(str('To:' + exit_rect[0]), self.colors["exit_rect"], r.topleft, bottomleft=True)

                pl_col_rect = copy(self.player.rect)
                pl_col_rect.topleft -= scroll
                pl_col_rect.topleft -= pg.Vector2(15, -70)
                pl_col_rect.w -= 70
                pl_col_rect.h -= 115
                pg.draw.rect(self.screen, self.colors["collision_rect"], pl_col_rect, 1)

                position = (self.player.rect.topleft - self.player.camera.offset.xy)
                itr_box = pg.Rect(*position, self.player.rect.w // 2, self.player.rect.h // 2)
                # Manual Position tweaks
                itr_box.x -= 17
                itr_box.y += 45
                pg.draw.rect(self.screen, (0, 0, 0), itr_box, 2)
