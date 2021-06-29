
import sys, random
import pygame as pg
from pygame import mixer
import json

pg.init(), pg.display.set_caption("iBoxStudio Engine")
DISPLAY = pg.display.set_mode((1280, 720), flags=pg.RESIZABLE | pg.SCALED)  # pg.NOFRAME for linux :penguin:
#pygame.display.toggle_fullscreen()
# Data
from .backend import *
from .player import *


# INITIALIZE

framerate = pygame.time.Clock()
Objects = UI_Spritesheet('data/objects_spritesheet.png')
UIspriteSheet = UI_Spritesheet('data/ui/UI_spritesheet.png')
NPCS = UI_Spritesheet('data/npc_spritesheet.png')
get_screen_w, get_screen_h = DISPLAY.get_width(), DISPLAY.get_height()
mouse_icon = UIspriteSheet.parse_sprite('mouse_cursor.png').convert()  # Game's exclusive mouse icon!
scroll = [0, 0]  # player "camera"

'''
    Note: If I want to reset the text I do         
    if self.current_text_index >= len(text): If its reaches the end
        self.current_text_index = 0
'''
class Interface(object): 
    def __init__(self):
        self.font = pg.font.Font("data/database/pixelfont.ttf", 24)
        self.icon = UIspriteSheet.parse_sprite('interface_button.png').convert()
        self.current_text_index = self.timer = 0
        self.text_pos = (get_screen_w // 2 - 420, get_screen_h // 2 + 110) # Position of the first sentence
        with open('data/database/language.json') as f: self.data = json.load(f) # Read/Save Json Data
        f.close() # Close File  
        
        self.sound = pg.mixer.Sound('data/sound/letter_sound.wav')
        self.sound.set_volume(0.2)
        self.draw_ui = True
        self.text_display = ['' for i in range(4)] # Create 4 empty text renders
        self.text_surfaces = [self.font.render(self.text_display[i], True, (0,0,0)) for i in range(4)] # font render each of them

    def reset(self):
        self.current_text_index = -2
    
    def draw(self, path, dt, interact_point):    
        text = self.data[path]['text'] # Import from Json the AI/UI 's text
        self.timer += dt # Speed of text/delta_time

        if self.timer > 0.030:
                self.current_text_index += 1 # Next letter
                print(len(text))
                if self.current_text_index < len(text):
                    self.current_text_index += 1 
                    if not(text[self.current_text_index] == ' '):                  
                        self.sound.play()  # Play sound only if there isn't a space
                
                # --- UPDATE CONTENT --- (in one line yee B) )
                self.text_display = [text[44 * i : min(self.current_text_index, 44 * (i + 1))] for i in range(4)] # Update letters strings
                self.text_surfaces = [self.font.render(text, True, (0,0,0)) for text in self.text_display]  # Transform them into a surface
                        
                # --- End of if statement
                self.timer = 0 # Reset timer
                                                    
        # Blit the text
       
        for i, surface in enumerate(self.text_surfaces):
            DISPLAY.blit(surface, (self.text_pos[0], self.text_pos[1] + i * 30))          

    def update(self): # Draws the UI not the text
        return DISPLAY.blit(self.icon, (get_screen_w // 2 - 460, get_screen_h // 2 + 80))

      
class stairs(pg.sprite.Sprite):
    def __init__(self, x, y):
        self.image = Objects.parse_sprite('stairs').convert()
        self.scaledImg = pg.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.x, self.y, self.interact_value = x, y, 0

    def update(self, player_rect):
        self.rect = self.scaledImg.get_rect(topleft=(self.x - scroll[0], self.y - scroll[1]))
        if self.rect.colliderect(player_rect):
            Player.isInteracting = True
        else:
            Player.isInteracting = False
        DISPLAY.blit(self.scaledImg, self.rect)

# Classes
class MainMenu(object):
    def __init__(self):
        # ------------ Background and Animation  -------------
        self.background_l1 = [pg.image.load('data/ui/mainmenubackground1.png').convert(),
                              pg.image.load('data/ui/mainmenubackground2.png').convert(),
                              pg.image.load('data/ui/mainmenubackground1.png').convert()]
        self.background_l2 = pg.image.load('data/ui/mainmenutile.png')
        self.animationCounter = 0  # Important for background animation
        self.font = pygame.font.Font("data/database/pixelfont.ttf", 14)
        self.GameStart = False # The game loop
        # ------------- Music Playlist -------------
        self.pb, self.qb, self.mm = 0, 0, 0  # 3 counters for each button for the music sounds
        self.music = [mixer.Sound("data/sound/forest_theme_part1.flac"), mixer.Sound("data/sound/Select_UI.wav")]
        for music in self.music:  music.set_volume(0.2)
        # ------------ Play Button UI  -------------
        self.playButton = [UIspriteSheet.parse_sprite('playbutton.png'), UIspriteSheet.parse_sprite('playbutton_hover.png')]
        self.playButtonRect = self.playButton[0].get_rect(center=(get_screen_w // 2 - 7, get_screen_h // 2 + 107))
        # ------------ Quit Button UI  -------------
        self.quitButton = [UIspriteSheet.parse_sprite('quit_button.png'), UIspriteSheet.parse_sprite('quit_button_hover.png')]
        self.quitButtonRect = self.quitButton[0].get_rect()

    # ------------ UI Interface  -------------
    def PlayButton(self):
        if self.playButtonRect.collidepoint(pg.mouse.get_pos()):
            while self.pb < 1:  # Plays sound once
                self.music[1].play()
                self.pb += 1
            DISPLAY.blit(self.playButton[1], self.playButtonRect)
        else:
            self.pb = 0  # Reset sound counter
            DISPLAY.blit(self.playButton[0], self.playButtonRect)

    def Buttons(self):  # BLITING THE GUI, but in a more organized way
        self.buttonFunction(), self.PlayButton(), self.QuitButton()

    def QuitButton(self):  # Imagine closing the game of the year. smh 
        if self.quitButtonRect.collidepoint(pg.mouse.get_pos()):
            while self.qb < 1:
                self.music[1].play()
                self.qb += 1
            DISPLAY.blit(self.quitButton[1], self.quitButtonRect)
        else:
            self.qb = 0
            DISPLAY.blit(self.quitButton[0], self.quitButtonRect)

    # ------------  Mechanism  -------------
    def buttonFunction(self):  # The gears between the interface and user input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(), sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:  # Mouse
                if self.playButtonRect.collidepoint(pg.mouse.get_pos()):
                    self.music[0].stop()
                    self.GameStart = True
                elif self.quitButtonRect.collidepoint(pg.mouse.get_pos()):
                    pg.quit(), sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit(), sys.exit()
                if event.key == pg.K_F12:
                    pg.display.toggle_fullscreen()

    # ------------ Real time changing -------------
    def update(self):  # 26/3 == int(8.6)
        self.quitButtonRect.center = (get_screen_w // 2 - 7, get_screen_h // 2 + 174)  # button position
        while self.mm < 1:
            #pygame.mouse.set_visible(False)  # Turn off mouse's visibility
            self.music[0].play()
            self.mm += 1
        if self.animationCounter >= 104: self.animationCounter = 0
        self.animationCounter += 1
        DISPLAY.blit(self.background_l1[self.animationCounter // 36], (0, 0))
        DISPLAY.blit(self.background_l2, (0, 0))
        self.Buttons()  # Display buttons (and function)
        DISPLAY.blit(mouse_icon, (pg.mouse.get_pos()))  # Display our mouse!


class Game:
    def __init__(self):
        self.menu = MainMenu()
        self.world_value = 0
        self.black_screen = pygame.image.load('data/ui/black_overlay.png')
        # Objects
        self.stairs = stairs(get_screen_w // 2 + 350, 160)  # X, Y
        # World images
        self.world = ''  # Current world
        self.worlds = [
            pygame.image.load('data/sprites/world/Johns_room.png').convert(),  # 0 John's Room
            pygame.image.load('data/sprites/world/kitchen.png').convert(),  # 1 Kitchen Room
        ]

        self.Player = Player(get_screen_w // 2, get_screen_h // 2, DISPLAY) # The player

        self.Characters = [
            Mau(350,530) # 0 Mau
        ]
        # Worlds
        self.Menu = True
        self.PlayerRoom, self.Kitchen, self.Route1 = False, False, False
        # Interface
        self.Interface = Interface()  # not working yet
        # ---------- Menu Icon -------
        self.MenuIcon = [UIspriteSheet.parse_sprite('menu_button.png').convert(), UIspriteSheet.parse_sprite('menu_button_hover.png').convert()]
        self.MenuIconRect = self.MenuIcon[0].get_rect(center=(get_screen_w // 2 - 7, get_screen_h // 2 + 174))
        self.menupl = 0
        # ---------- Catalogs -------
        self.text_counter = 0

    def pause(self):
        if self.Player.paused:
            pygame.mouse.set_visible(False)  # Hide actual cursor
            DISPLAY.blit(self.black_screen, (0, 0))
            for character in self.Characters: character.speed = 0 # Stop characters from moving
            self.menu.QuitButton()
            self.menu.quitButtonRect.center = (get_screen_w // 2 - 7, get_screen_h // 2 + 241)  # Change its position

            if self.MenuIconRect.collidepoint(pygame.mouse.get_pos()):
                while self.menupl < 1:
                    self.menu.music[1].play()
                    self.menupl += 1
                DISPLAY.blit(self.MenuIcon[1], self.MenuIconRect)
                if self.Player.click:
                    self.PlayerRoom, self.Menu, self.menu.GameStart,self.Player.paused = False, True, False, False
            else:
                self.menupl = 0
                DISPLAY.blit(self.MenuIcon[0], self.MenuIconRect)

            if self.Player.click and self.menu.quitButtonRect.collidepoint(pygame.mouse.get_pos()):
                pygame.quit(), sys.exit()
            DISPLAY.blit(mouse_icon, (pygame.mouse.get_pos()))  # Display the mouse cursor
    
    def npc_collisions(self, collision_tolerance = 10):
         # Αλγόριθμος Παγκόσμιας Σύγκρουσης Οντοτήτων / Player Collision System with Entities (UNDER MANAGEMENT)

         for character in self.Characters:
             if self.Player.Rect.colliderect(character.Rect):
                 character.speed = 0

                 if self.Player.Down: # Clunky
                    if abs(character.Rect.top - self.Player.Rect.bottom) < collision_tolerance:
                        self.Player.y = self.Player.y - self.Player.speedY
  
                 if self.Player.Up: 
                    if abs(character.Rect.bottom - self.Player.Rect.top) < collision_tolerance:
                        self.Player.y = self.Player.y + self.Player.speedY

                 if self.Player.Right:  # Clunky
                    if abs(character.Rect.left - self.Player.Rect.right) < collision_tolerance:
                        self.Player.x = self.Player.x - self.Player.speedX
                        
                 if self.Player.Left: 
                    if abs(character.Rect.right - self.Player.Rect.left) < collision_tolerance:
                        self.Player.x = self.Player.x + self.Player.speedX

    def update(self):
        global scroll
        
        while True:
            dt = framerate.tick(35) / 1000 # DELTA TIME VERY IMPORTANT
            DISPLAY.fill((0, 0, 0))
            if self.Menu:
                self.menu.update()
                if self.menu.GameStart:
                    self.Menu, self.PlayerRoom, self.world = False, True, self.worlds[0]
            else:
                pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(0, 0, get_screen_w * 4, get_screen_h * 4))

                # Device the below with a number do add "smoothness"
                scroll[0] += (self.Player.x - scroll[0] - get_screen_w // 2)  # Player's X Camera
                scroll[1] += (self.Player.y - scroll[1] - get_screen_h // 2)  # Player's Y Camera
                # ANYTHING ELSE GOES BELOW            
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))  # John's room layer 0
                # ---LAYER 1---
                if self.PlayerRoom: 
                   self.stairs.update(self.Player.Rect) # Draw stairs
                   self.Characters[0].update(DISPLAY, scroll, self.Interface, self.Player, dt) # Mau
                # ---LAYER 2---
                self.Player.update()  # Draw player
                # ---Collisions---
                if self.PlayerRoom:
                         
                    
                        pygame.draw.rect(DISPLAY, (124,252,0), (300 - scroll[0], 450 - scroll[1],768,128), 1)
                        if self.Player.x > get_screen_w - 40:
                           self.Player.x = get_screen_w - 40  # Right walls
                        elif self.Player.x < (get_screen_w - get_screen_w) + 40:
                           self.Player.x = get_screen_w - get_screen_w + 40  # Left walls
                        if self.Player.y > get_screen_h - 40:
                            self.Player.y = get_screen_h - 40  # Down walls
                        elif self.Player.y < (get_screen_h - get_screen_h) + 150:
                            self.Player.y = (get_screen_h - get_screen_h) + 150  # Up walls
                        if self.Player.x <= 266:  self.Player.x = 266  # Bed
                        if self.Player.x < 626 and self.Player.y <= 290: self.Player.y = 290  # Desk bottom
                        if self.Player.x >= 626 and self.Player.x < 631 and self.Player.y < 290: self.Player.x = 631  # Desk right
                        if self.Player.x >= 1111 and self.Player.y > 310: self.Player.x = 1111  # Computer
                        if self.Player.x > 1111 and self.Player.y > 305 and self.Player.y < 310: self.Player.y = 305


                # Global stuff that all worlds share      
                self.npc_collisions()
                self.pause()  # Pause menu
            # General Function         
            pygame.display.update()



