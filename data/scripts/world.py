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
from .AI.enemies import Enemy
from .sound_manager import SoundManager
from .AI import npc
from .UI.mainmenu import Menu
from .UI.interface import Interface
from .UI.loading_screen import LoadingScreen


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
font = pg.font.Font("data/database/pixelfont.ttf", 24)
blacksword = pg.font.Font("data/database/Blacksword.otf", 113) # I use this only for the logo
pg.mouse.set_visible(True)


ui = UI_Spritesheet("data/ui/UI_spritesheet.png")


class Game:
    def __init__(self):
        self.sound_manager = SoundManager()
        
        self.menu = Menu(DISPLAY, blacksword, ui)
        self.Menu = True # If False , the adventure starts
        self.loading = False
        self.loading_screen = LoadingScreen(DISPLAY)
        #------- World -----
        self.worlds = [
            pg.transform.scale(load('data/sprites/world/Johns_room.png'), (1280,720)), # 0 John's Room
            pg.transform.scale(load('data/sprites/world/kitchen.png'), (1280,720))  # 1 Kitchen Room
        ]
        self.world = self.worlds[0]  # Current world      
        self.PlayerRoom = self.Kitchen = self.Forest = False  # Worlds

        self.interface = Interface(DISPLAY, ui, font, dt)

        self.Player = Player(get_screen_w // 2, get_screen_h // 2, DISPLAY, self.interface, self.menu.save, ui) # The player
        #------- Objects -----
        self.o_index = 0 # Index for the sublists below
        self.objects = [
            [npc.NPCS.Mau(150,530), pg.Rect(10,90, 430,360), pg.Rect(5,500, 72, 214), pg.Rect(450, 40, 410, 192), Enemy.Dummy(DISPLAY, (1050, 300)), Enemy.Dummy(DISPLAY, (1050, 600))], # John's Room
            [npc.NPCS.Cynthia(570, 220), Chest(960,175, 0),pg.Rect(20, 250, 250,350), pg.Rect(280,300, 64, 256), pg.Rect(10,0, 990, 230), pg.Rect(1020, 440, 256, 200)] # Kitchen Room
        ]

        # We need to refactor this so we dont have to put seperate pointers on every single object ( I got a idea ngl)
        self.object_p = [
            [None, pg.Vector2(10,90), pg.Vector2(5,500), pg.Vector2(450, 40)], # John's Room     
            [None, None,pg.Vector2(20, 250), pg.Vector2(280,300), pg.Vector2(10,0), pg.Vector2(1020, 440)]    
        ]

    # Αλγόριθμος Παγκόσμιας Σύγκρουσης Οντοτήτων / Player Collision System with Object&Entities
    def collision_system(self, index):
        for i, object in enumerate(self.objects[index]):
            collision = False # No collision      
            object.topleft = (
                self.object_p[index][i].x - scroll[0], self.object_p[index][i].y - scroll[1]) if type(object) == pg.Rect \
                else (object.x - scroll[0], object.y - scroll[1]
            )  

            t, b, l, r, is_rect = self.Player.Rect.top,  self.Player.Rect.bottom, self.Player.Rect.left, self.Player.Rect.right, bool(type(object) is pg.Rect)
            collision =  self.Player.Rect.colliderect(object) if is_rect else self.Player.Rect.colliderect(object.Rect)
            try:
                if self.Player.Rect.colliderect(object.interact_rect): self.Player.is_interacting, self.Player.interact_text = True, object.interact_text
                draw = pg.draw.rect(DISPLAY, (255,255,255), object.Rect) if is_rect else  pg.draw.rect(DISPLAY, (255,255,255), object)
            except: pass
            top = abs(object.bottom - t) if is_rect else abs(object.Rect.bottom - t)
            bottom = abs(object.top - b) if is_rect else abs(object.Rect.top - b)
            left = abs(object.right - l) if is_rect else abs(object.Rect.right - l)
            right = abs(object.left - r) if is_rect else abs(object.Rect.left - r)
            # Collision happens
            if collision:                       
                if self.Player.Up or self.Player.Down:  # Up / Down borders
                    if top < 10:
                        self.Player.y += self.Player.speedY
                    elif bottom < 10:
                        self.Player.y -= self.Player.speedY # Clunky             
                if self.Player.Left or self.Player.Right:  # Left / Right borders
                    if left < 10:
                        self.Player.x += self.Player.speedX
                    elif right < 10:
                        self.Player.x -= self.Player.speedX # Clunky

    # We will rework the pause menu class
    def pause(self, mouse):
        if self.Player.paused:
            surface = pg.Surface((get_screen_w,get_screen_h), pg.SRCALPHA)
            surface.fill((0,0,0)); surface.set_alpha(235); DISPLAY.blit(surface, (0,0)) # Draws black screen with opacity
            # -----v TEMPORARY v-----
            DISPLAY.blit(font.render("(GAME UNDER CONSTRUCTION)", True, (255,255,255)), (get_screen_w//2 - 220, get_screen_h//2 - 140))
            DISPLAY.blit(blacksword.render("Paused", True, (255,255,255)), (get_screen_w//2 - 190, get_screen_h//2 - 120))
            DISPLAY.blit(font.render("PRESS ESQ TO UNPAUSE", True, (255,255,255)), (get_screen_w//2 - 190, get_screen_h//2 + 100))
            DISPLAY.blit(font.render("THINGS ARE GOING TO BE CHANGED IN THE FUTURE", True, (255,255,255)), (256, get_screen_h//2 + 140))

    # When in a room
    def room_borders(self, up = get_screen_h - get_screen_h, down = get_screen_h, left = get_screen_w - get_screen_w, right = get_screen_w):
        if self.Player.y < up + 150: self.Player.y = up + 150
        elif self.Player.y > down - 40: self.Player.y = down - 40
        if self.Player.x < left + 40: self.Player.x = left + 40
        elif self.Player.x > right - 40: self.Player.x = right - 40

    def update(self):
        global scroll
        while 1:
            dt, mouse_p = framerate.tick(35) / 1000, pg.mouse.get_pos() # Framerate Indepence and Mouse position
            DISPLAY.fill((0, 0, 0))
            if self.Menu:
                self.menu.update(mouse_p) # Show Menu Screen
                # Position of the buttons
                if self.menu.event.type == pg.MOUSEBUTTONDOWN and not self.menu.show_settings:
                    if self.menu.btns_rects[0].collidepoint(mouse_p):  
                        self.Menu = False
                        self.loading = True
                        self.loading_screen.start("PlayerRoom")
                    if self.menu.btns_rects[2].collidepoint(mouse_p): 
                        raise SystemExit

            elif self.loading:
                update_return = self.loading_screen.update()
                if update_return is not None:
                    setattr(self, update_return["next_state"], True)
                    self.loading = False
                    if update_return["next_music"] is not None:
                        self.sound_manager.play_music(update_return["next_music"])

            else: # The game           
                scroll += pg.Vector2(self.Player.x - scroll[0] - get_screen_w // 2, self.Player.y - scroll[1] - get_screen_h // 2)
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))  # World Background Image
                ''' John's Room '''
                if self.PlayerRoom:    
                    self.Player.rooms_objects = self.objects[0]
                    self.objects[0][0].update(DISPLAY, scroll, self.Player), self.room_borders() # Mau
                    self.objects[0][4].update(scroll)
                    self.objects[0][5].update(scroll)
                    if self.Player.y < 270 and self.Player.x < 870:
                       self.Player.interact_text, self.Player.is_interacting = 'computer' if 680 <= self.Player.x <= 870 else 'desk', True                  
                    # Stairs
                    if self.Player.Rect.colliderect(pg.Rect(get_screen_w // 2 + 353 - scroll[0], 150 - scroll[1], 155, 130)):
                        self.Player.interact_text, self.Player.is_interacting  = 'stairs', True
                        if self.Player.InteractPoint == 2:
                            self.PlayerRoom, self.world, self.Player.x , self.Player.y, self.Player.is_interacting, self.o_index = False, self.worlds[1], 1120, 250, False, 1
                            self.loading = True
                            self.loading_screen.start("Kitchen", text=False, cat=False, duration=1250)
                     # End of John's Room
                elif self.Kitchen:
                    self.Player.rooms_objects = self.objects[1]
                    self.room_borders()
                    self.objects[1][0].update(DISPLAY, scroll, self.Player)
                    self.objects[1][1].update(DISPLAY, scroll, self.Player)
                    if self.Player.y < 270 and self.Player.x <= 810:
                        self.Player.interact_text, self.Player.is_interacting = 'kitchen' if self.Player.x < 570 else 'sink', True
                    ''' Stairs '''
                    if self.Player.x >= 1005 and self.Player.y < 240 and self.Player.Interactable:
                        self.Player.is_interacting , self.Player.interact_text = True, 'stairs_up'
                        if self.Player.InteractPoint == 2:
                            self.PlayerRoom, self.world, self.Kitchen, self.Player.x, self.Player.y, self.Player.is_interacting, self.o_index = True, self.worlds[0], False, 1080, 320, False, 0
                # Global stuff that all worlds share
                self.Player.update(dt)  # Draw player
                self.collision_system(self.o_index)
                self.pause(mouse_p)  # Pause menu
            # General Function         
            pg.display.update()