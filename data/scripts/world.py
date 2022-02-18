from .PLAYER.player import Player
from .PLAYER.inventory import *
from .sound_manager import SoundManager
from .UI.mainmenu import Menu
from .UI.interface import Interface
from .UI.loading_screen import LoadingScreen
from .UI.pause_menu import PauseMenu, quit_pause
from .utils import resource_path, l_path, UI_Spritesheet, smooth_scale
from .QUESTS.quest_manager import QuestManager
from .QUESTS.quest_ui import QuestUI
from .props import PropGetter, init_sheets, del_sheets
from threading import Thread
from .POSTPROCESSING.cutscene_engine import CutsceneManager

from .PLAYER.player_sub.tools import set_camera_to

from .PLAYER.player_sub.animation_handler import user_interface


from .levels import (
    Gymnasium,
    get_cutscene_played,
    play_cutscene,
    GameState,
    PlayerRoom,
    Kitchen,
    JohnsGarden,
    ManosHut,
    Cave,
    Training_Field
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
    pg.display.set_caption("iBoxStudio Engine Demo")
    pg.mouse.set_visible(False)
    # CONSTS

    DISPLAY = pg.display.set_mode((1280, 720),
                                )  # | pg.SCALED | pg.DOUBLEBUF | pg.FULLSCREEN | pg.NOFRAME

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
        self.font = pg.font.Font(resource_path("data/database/menu-font.ttf"), 24)
        
        # (main menu title)
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
        self.menu_manager = Menu(self, self.DISPLAY, self.blacksword, self.ui)
        self.interface = Interface(self.DISPLAY, scale(self.ui.parse_sprite('interface_button.png'), 8))
        self.pause_menu = PauseMenu(self.DISPLAY, self.ui)

        # ------------- PLAYER ----------------
        self.player = Player(
            self,
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
        
        # THIS IS WHERE YOU LOAD THE WORLDS
        self.state_manager = {
            "player_room": PlayerRoom,
            "kitchen": Kitchen,
            "johns_garden": JohnsGarden,
            "manos_hut": ManosHut,
            "cave": Cave,
            "training_field": Training_Field,
            "gymnasium": Gymnasium
        }
        self.loaded_states: dict[str: GameState] = {}
        self.game_state: GameState = None

        # ------------ DEBUG ----------------------
        self.debug = debug
        self.debugger = Debugging(self.DISPLAY, self, no_rect)

        # -------- CAMERA SRC HANDLER -------------
        self.cutscene_engine = CutsceneManager(self, self.DISPLAY)

        # ------------- QUESTS -------------------
        self.quest_manager = QuestManager(self, self.player)
        self.quest_UI = QuestUI(self.DISPLAY, self.quest_manager)
        self.player.quest_UI = self.quest_UI

    def pause(self):
        if self.player.paused:
            self.pause_menu.init_pause()
            while True:
                upd = self.pause_menu.update()

                if upd == "quit":
                    quit_pause()
                    self.menu = True
                    self.player.paused = False
                    self.menu_manager.start_game = False
                    break
                elif upd == "resume":
                    quit_pause()
                    self.player.paused = False
                    break

                pg.display.update()

    def routine(self):

        """Method called every frame of the game.
        (Created to simplify the game loop)"""

        self.dt = self.framerate.tick(self.FPS) / 1000

        if not self.menu and not self.loading:  # if the game is playing
            user_interface(self.player, pg.mouse.get_pos(), (
                # 52 48 are players height and width
                self.player.rect.x - 52 - self.player.camera.offset.x,
                self.player.rect.y - self.player.camera.offset.y - 48
                ), 
                self.dt  # <- is needed for the NPC interaction
            ) 
            self.pause()
            if hasattr(self.player.camera.method, "fov"):
                if self.player.camera.method.fov != 1:
                    surface = self.DISPLAY.subsurface(self.player.camera.method.capture_rect)
                    surface = smooth_scale(surface, self.player.camera.method.fov)
                    self.DISPLAY.blit(surface, surface.get_rect(center=(self.DISPLAY.get_width()//2,
                                                                        self.DISPLAY.get_height()//2)))
            self.cutscene_engine.render()
            if self.player.inventory.show_menu or self.player.upgrade_station.show_menu:
                self.DISPLAY.blit(self.player.mouse_icon, pg.mouse.get_pos())
            self.quest_manager.update_quests()

        if self.debug:
            self.debugger.update()


        pg.display.update()

    def pg_loading_screen(self):
        while pg.time.get_ticks() < 3000:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_()

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

    def quit_(self):
        for key, level in self.loaded_states.items():
            for obj in level.objects:
                if hasattr(obj, "end_instance"):
                    obj.end_instance()
        for obj in self.game_state.objects:
            if hasattr(obj, "end_instance"):
                obj.end_instance()
        pg.quit()
        raise SystemExit

    def start_new_level(self, level_id, last_state="none", first_pos=None):

        if self.game_state is not None:
            self.loaded_states[self.game_state.id] = self.game_state

        # load all the sheets (to delete them afterwards)
        init_sheets()

        def load_new_level(parent, level_):
            parent.game_state = parent.state_manager[level_](parent.DISPLAY, parent.player, parent.prop_objects) \
                if level_ not in parent.loaded_states else parent.loaded_states[level_]

        loading_thread = Thread(target=load_new_level, args=(self, level_id))
        loading_thread.start()

        start = pg.time.get_ticks()  # time to start (track the loading screen duration)
        self.state = level_id  # update the current state to the next one
        self.player.UI_interaction_anim.clear()  # empty the UI animations
        load_type = ["loading..." if first_pos is None else "main_loading", 750]  # [load_type, duration]
        self.loading_screen.init(load_type[0], duration=load_type[1])  # initialize the loading screen
        run_loading = True
        while run_loading:
            # check if loading screen has to be ended
            is_load_alive = loading_thread.is_alive() or pg.time.get_ticks() - start < load_type[1]

            # don't ask for a key if it's just an in-between level loading. (just exit the loading)
            if not is_load_alive and load_type[0] == "loading...":
                run_loading = False

            # ask for a key to end the loading screen
            load_type[0] = "ended" if not is_load_alive else load_type[0]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    del loading_thread  # quit the thread
                    self.quit_()
                elif event.type == pg.KEYDOWN:  # ask for a key to leave the loading
                    if event.key == self.loading_screen.get_key() and not is_load_alive:
                        run_loading = False
            self.DISPLAY.fill((0, 0, 0))  # draw background
            self.loading_screen.draw(self.DISPLAY, load_type[0])  # draw loading screen (according to load_type)
            pg.display.update()

        if last_state == "none":  # update pos according to spawn points
            keys = [key for key in self.game_state.spawn]
            self.player.rect.topleft = self.game_state.spawn[keys[0]]
        else:
            self.player.rect.topleft = self.game_state.spawn[last_state]

        # replace the player for the cutscene (if needed)
        if first_pos is not None and not self.debug:
            self.player.rect.topleft = first_pos
            self.first_state = True

        # load all the lights in the game
        self.game_state.lights_manager.init_level(self.game_state)
        # unload the sheets (theoretically supposed to save RAM)
        del_sheets()
        # stop the player from moving
        self.player.Left = self.player.Right = self.player.Up = self.player.Down = False

    def update(self):

        """

            FOR DEBUGGING MEASURES, ELSE RUN THE GAME NORMAL

        """
        if not self.debug:
            self.pg_loading_screen()
        else:
            self.start_new_level(self.state,
                                 first_pos=(self.DISPLAY.get_width() // 2 - 120, self.DISPLAY.get_height() // 2 - 20))
            self.menu = False
            self.loading = False

        while True:

            if self.menu:  # menu playing

                self.menu_manager.update(pg.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = False

                    self.start_new_level(self.state,
                                         first_pos=((self.DISPLAY.get_width() // 2 - 120,
                                                     self.DISPLAY.get_height() // 2 - 20) if not self.first_state
                                                    else None))

            else:
                self.DISPLAY.fill((0, 0, 0))
                update = self.game_state.update(self.player.camera, self.dt)
                if update is not None:  # if a change of state is detected
                    self.start_new_level(update, last_state=self.state)

                '''  RUN THE CAMERA ONLY WHEN ITS NOT IN DEBUGGING MODE  '''
                if not self.debug and self.cutscene_engine.state != "inactive":
                    self.cutscene_engine.update()
                    self.FPS = 360  # if it works
                elif not self.debug:
                    set_camera_to(self.player.camera, self.player.camera_mode, "follow")

                    if not self.game_state.ended_script and len(self.game_state.camera_script) > 0:
                        self.cutscene_engine.init_script(self.game_state.camera_script)

                    self.FPS = 35
                else:
                    set_camera_to(self.player.camera, self.player.camera_mode, "follow")

            self.routine()


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

        self.font = pg.font.Font(resource_path("data/database/menu-font.ttf"), 15)

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

                            if obj.IDENTITY == "ENEMY":
                                self.draw_text(f"STATUS: {obj.status}", (255, 255, 255), obj.rect.topleft)

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

                try:
                    pg.draw.rect(self.screen, (255, 0, 0), self.player.attacking_hitbox, 2)
                except TypeError:
                    pass

                position = (self.player.rect.topleft - self.player.camera.offset.xy)
                itr_box = pg.Rect(*position, self.player.rect.w // 2, self.player.rect.h // 2)
                # Manual Position tweaks
                itr_box.x -= 17
                itr_box.y += 45
                pg.draw.rect(self.screen, (0, 0, 0), itr_box, 2)
