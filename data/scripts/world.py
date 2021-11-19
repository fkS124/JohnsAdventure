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

from .levels import (
    PlayerRoom,
    Kitchen,
    JohnsGarden
)

def main(debug=False):
    GameManager(debug=debug).update()


class GameManager:

    """

    Game class -> handles everything of the game.

    """
    pg.init()

    # FONTS

    pg.mixer.pre_init(44100, 32, 2, 4096) # Frequency, 32 Bit sound, channels, buffer
    pg.display.set_caption("iBoxStudio Engine Pre Alpha 0.23")
    pg.mouse.set_visible(False)
    # CONSTS
   
    DISPLAY = pg.display.set_mode((1280, 720), flags= pg.SRCALPHA) #| pg.SCALED | pg.DOUBLEBUF | pg.FULLSCREEN | pg.NOFRAME

    pg.display.set_icon(l_path("data/ui/logo.png", True))
    W, H = DISPLAY.get_size()
    
    FPS = 35


    def __init__(self, debug=False):

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
        self.interface = Interface(self.DISPLAY, self.ui, self.font, self.dt)
        self.pause_menu = PauseMenu(self.DISPLAY, self.ui)

        # ------------- PLAYER ----------------
        self.player = Player(
        self.DISPLAY, # Screen surface
        self.font, # Font
        self.interface,
        self.ui, # Other UI like Inventory
        self.menu_manager.save, # controls
        )

        # ----------- GAME STATE ------------------
        self.state = "player_room"
        self.state_manager = {
            "player_room": PlayerRoom(self.DISPLAY, self.player),
            "kitchen": Kitchen(self.DISPLAY, self.player),
            "johns_garden": JohnsGarden(self.DISPLAY, self.player)
        }

        # ------------ DEBUG ----------------------
        self.debug = debug
        self.debugger = Debugging(self.DISPLAY, self)

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
                    self.loading = True
                    self.loading_screen.start("menu", duration=1000, text=True, cat=True, key_end=False)
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
            self.player.update(self.dt)
            self.pause()

        if self.debug:
            self.debugger.update()

        pg.display.update()

    def pg_loading_screen(self):
        while pg.time.get_ticks()<3000:
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
            self.DISPLAY.blit(img, img.get_rect(center=(self.W//2, self.H//2)))  

            if pg.time.get_ticks() - self.start_logo_time > 700:
                self.DISPLAY.blit(self.font.render("@Copyright Logo by www.pygame.org", True, (0,0,0)), img.get_rect(topleft=(self.W//2 - 320, self.H//2 + 230)))

            self.framerate.tick(self.FPS)
            pg.display.update()

    def update(self):
        
        '''

            FOR DEBUGGING MEASURES, ELSE RUN THE GAME NORMAL
        
        '''
        if not self.debug:
            self.pg_loading_screen()
        else:
            self.menu = False
            self.loading = False 


        while True:

            if self.menu:  # menu playing

                self.menu_manager.update(pg.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = True
                    self.loading_screen.start(self.state, duration=2500, main_loading=True, cat=True, text=False, key_end=False)

            elif self.loading:  # update the loading screen

                update_return = self.loading_screen.update()
                if update_return is not None:
                    #print(update_return["next_state"])
                    if update_return["next_state"] != "menu":
                        self.state = update_return["next_state"]
                        self.loading = False
                        if update_return["next_music"] is not None:
                            self.sound_manager.play_music(update_return["next_music"])
                    else:
                        self.menu = True
                        self.loading = False

            else:
                self.DISPLAY.fill((0, 0, 0))
                update = self.state_manager[self.state].update(self.player.camera, self.dt)
                if update is not None:  # if a change of state is detected
                    self.loading = True  # start a loading screen (update="next_state_name")
                    self.loading_screen.start(update, text=True, duration=750, key_end=False)
                    if self.state in self.state_manager[update].spawn:
                        self.player.rect.topleft = self.state_manager[update].spawn[self.state]

                '''  RUN THE CAMERA ONLY WHEN ITS NOT IN DEBUGGING MODE  '''
                if not self.state_manager[self.state].ended_script and not self.debug:
                    self.camera_script_handler()
                else:
                    self.player.set_camera_to("follow")

            self.routine()

    def start_new_src_part(self):

        c_level = self.state_manager[self.state]
        cam_script = c_level.camera_script
        src_index = c_level.cam_index
        
        self.player.set_camera_to("auto")
        self.scripting = True
        self.ended = False

        cur_script = cam_script[src_index]
        self.player.camera.method.go_to(cur_script["pos"], duration=cur_script["duration"])
        self.s_next_cam = cur_script["next_cam_status"] if "next_cam_status" in cur_script else None
        self.player.camera.method.set_text(cur_script["text"] if "text" in cur_script else "")
        self.s_dt_to_wait_on_end = cur_script["waiting_end"] if "waiting_end" in cur_script else 0

        #print("Started:", src_index, "w:", self.s_dt_to_wait_on_end, "dt:", cur_script["duration"], cur_script["pos"])

    def camera_script_handler(self):
        c_level = self.state_manager[self.state]
        cam_script = c_level.camera_script
        src_index = c_level.cam_index
        camera = self.player.camera

        if not self.scripting:
            if src_index + 1 < len(cam_script):
                self.state_manager[self.state].cam_index += 1
                self.start_new_src_part()
            else:
                self.state_manager[self.state].ended_script = True
                return
            
        if not camera.method.moving_cam and not self.ended:
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

    def __init__(self, display, game_instance):

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
            rect.bottomleft=pos
        self.screen.blit(text, rect)

    def update(self):

        """Primitive debugging system showing rects.
        
        TODO: Improve it to show stats. And make it more readable."""
        
        if not self.game.menu and not self.game.loading:
            scroll = self.player.camera.offset.xy
            objects = copy(self.game.state_manager[self.game.state].objects)
            objects.append(self.player)

            for obj in objects:
                if type(obj) is pg.Rect:
                    pg.draw.rect(self.screen, self.colors["collision_rect"], pg.Rect(obj.topleft-self.player.camera.offset.xy, obj.size), 2)
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
                        pg.draw.rect(self.screen, self.colors["collision_rect"], col_rect, 2)

            
            exit_rects = self.game.state_manager[self.game.state].exit_rects
            for exit_rect in exit_rects:
                r = copy(exit_rects[exit_rect][0])
                r.topleft -= scroll
                pg.draw.rect(self.screen, self.colors["exit_rect"], r, 2)
                self.draw_text(str('To:'+exit_rect[0]), self.colors["exit_rect"], r.topleft, bottomleft=True)

            pl_col_rect = copy(self.player.rect)
            pl_col_rect.topleft -= scroll
            pl_col_rect.topleft -= pg.Vector2(15, -70)
            pl_col_rect.w -= 70
            pl_col_rect.h -= 115
            pg.draw.rect(self.screen,self.colors["collision_rect"], pl_col_rect, 1)
