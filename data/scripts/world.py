
import sys, random
import pygame as pg
from pygame import mixer
import json

pg.init(), pg.display.set_caption("iBoxStudio Engine")


DISPLAY = pg.display.set_mode((1280, 720))
#  Uncomment the below when you stop debugging
#DISPLAY = pg.display.set_mode((1280, 720), flags=pg.RESIZABLE | pg.SCALED)  # pg.NOFRAME for linux :penguin:
#pg.display.toggle_fullscreen()
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
dt = 0 # Delta time :D
paused_sound = False

# Fonts
blacksword = pg.font.Font("data/database/Blacksword.otf", 113) # I use this only for the logo

def play(sound): # Play's sound once
    global paused_sound
    if not paused_sound: 
        sound.play(); paused_sound = True


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
    
    def draw(self, path, interact_point):   
        global dt
        text = self.data[path]['text'] # Import from Json the AI/UI 's text
        self.timer += dt # Speed of text/delta_time

        if self.timer > 0.030:
                self.current_text_index += 1 # Next letter
 
                if self.current_text_index < len(text):
                    self.current_text_index += 1 
                    if not (text[self.current_text_index] == ' '):                  
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
        self.image = double_size(Objects.parse_sprite('stairs'))
        self.x, self.y, self.interact_value = x, y, 0


    def update(self, player, interface):
        self.rect = self.image.get_rect(topleft=(self.x - scroll[0], self.y - scroll[1]))
        if self.rect.colliderect(player.Rect):
            if player.Interactable:
                interface.update(), interface.draw('stairs', player.InteractPoint)
            else:
                interface.reset()

        DISPLAY.blit(self.image, self.rect)

# Classes
class MainMenu(object):
    def __init__(self):
        # ------------ Background and Animation  -------------
        self.background = pg.transform.scale(load('data/ui/background.png'), (1280,720))
        self.mouse, self.event = 0, None # Mouse Coordinates and event for keys
        self.logo_text_outline = blacksword.render("John's Adventure", True, (0,0,0))
        self.logo_text = blacksword.render("John's Adventure", True, (255,255,255))

        # ------------- Music Playlist -------------
        self.button_font = pg.font.Font("data/database/pixelfont.ttf", 34)
        self.music = [mixer.Sound("data/sound/forest_theme_part1.flac"), mixer.Sound("data/sound/Select_UI.wav")]
        for music in self.music:  music.set_volume(0.2)

        # --------- GUI ----------
        self.buttons = [ 
            [
               scale(UIspriteSheet.parse_sprite('button.png'), 4),
               scale(UIspriteSheet.parse_sprite('button_hover.png'), 4)
            ]
            for i in range(2) # Create two buttons (make it 3 if im going to add settings)
        ]

        # Gui Text
        self.gui_text = [self.button_font.render("Play", True, (255,255,255)), self.button_font.render("Quit", True, (255,255,255))]

    def gui(self): # BLOATWARE!!!!111
        global paused_sound
        for i, button in enumerate(self.buttons):
            # Take the rect of the first image of the sublist
            button_rect = button[0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 75 * (i + 1) )  ))
            if button_rect.collidepoint(self.mouse):
                DISPLAY.blit(button[1], button_rect) # Show hovered image
                play(self.music[1]) # Plays sound once
            else:    
                DISPLAY.blit(button[0], button_rect) # Show normal image
            # The below results in a centered text
            DISPLAY.blit(self.gui_text[i], (button_rect[0] + button[0].get_width()//4, button_rect[1]))

    # ------------ Real time changing -------------
    def update(self):  
        global paused_sound
        self.mouse = pg.mouse.get_pos()           
        # ------------ BLITS ------------- 
        DISPLAY.blit(mouse_icon, (self.mouse)), DISPLAY.blit(self.background,(0,0)), self.gui()
        DISPLAY.blit(self.logo_text_outline, (get_screen_w//6+20, get_screen_h//2 - 190))
        DISPLAY.blit(self.logo_text, (get_screen_w//6+20, get_screen_h//2 - 188))
        
        menu_rect = self.buttons[0][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 75)))
        quit_rect = self.buttons[1][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 150)))  

        if not(menu_rect.collidepoint(pg.mouse.get_pos()) or quit_rect.collidepoint(pg.mouse.get_pos())):
            paused_sound = False

        for event in pg.event.get():
            self.event = event
            if event.type == pg.QUIT: pg.quit(), sys.exit()                       
            if event.type == pygame.KEYDOWN and event.key == pg.K_F12: pg.display.toggle_fullscreen()
                               
class Game:
    def __init__(self):
        self.menu = MainMenu()       
        self.black_screen = load('data/ui/black_overlay.png', True)
        # Objects
        self.stairs = stairs(get_screen_w // 2 + 350, 160)  # X, Y
        # World images            
        self.worlds = [
            load('data/sprites/world/Johns_room.png'),  # 0 John's Room
            load('data/sprites/world/kitchen.png'),  # 1 Kitchen Room
        ]
        self.world = self.worlds[0]  # Current world

        self.Player = Player(get_screen_w // 2, get_screen_h // 2, DISPLAY) # The player
        self.Characters = [
            Mau(350,530) # 0 Mau
        ]
        # Worlds
        self.Menu = True # If False , the game starts
        self.PlayerRoom = True  # First world
        self.Kitchen = self.Forest = False
        # Interface
        self.Interface = Interface()


    def pause(self, mouse):
        if self.Player.paused:
            pygame.mouse.set_visible(False)  # Hide actual cursor
            DISPLAY.blit(self.black_screen, (0, 0))
            for character in self.Characters: character.speed = 0 # Stop characters from moving
            DISPLAY.blit(mouse_icon, mouse)  # Display the mouse cursor
            # -----v TEMPORARY v-----
            DISPLAY.blit(self.Interface.font.render("(GAME UNDER CONSTRUCTION)", True, (255,255,255)), (get_screen_w//2 - 220, get_screen_h//2 - 140))
            DISPLAY.blit(blacksword.render("Paused", True, (255,255,255)), (get_screen_w//2 - 190, get_screen_h//2 - 120))
            DISPLAY.blit(self.Interface.font.render("PRESS ESQ TO UNPAUSE", True, (255,255,255)), (get_screen_w//2 - 190, get_screen_h//2 + 100))
            DISPLAY.blit(self.Interface.font.render("THINGS ARE GOING TO BE CHANGED IN THE FUTURE", True, (255,255,255)), (256, get_screen_h//2 + 140))
    
    # Wall collisions when player enters a room
    def room_borders(self): 
        # Up
        if self.Player.y < (get_screen_h - get_screen_h) + 150: self.Player.y = (get_screen_h - get_screen_h) + 150
        # Down
        elif self.Player.y > get_screen_h - 40: self.Player.y = get_screen_h - 40 
        # Left
        if self.Player.x < (get_screen_w - get_screen_w) + 40: self.Player.x = get_screen_w - get_screen_w + 40 
        # Right
        elif self.Player.x > get_screen_w - 40: self.Player.x = get_screen_w - 40  
       

    # Αλγόριθμος Παγκόσμιας Σύγκρουσης Οντοτήτων / Player Collision System with Entities (UNDER MANAGEMENT)
    def npc_collisions(self, collision_tolerance = 10):   
         for character in self.Characters:
             if self.Player.Rect.colliderect(character.Rect):
                 # Up / Down borders
                 if self.Player.Up or self.Player.Down: 
                    if abs(character.Rect.bottom - self.Player.Rect.top) < collision_tolerance:
                        self.Player.y = self.Player.y + self.Player.speedY
                    elif abs(character.Rect.top - self.Player.Rect.bottom) < collision_tolerance:
                        self.Player.y = self.Player.y - self.Player.speedY # Clunky
                 # Left / Right borders
                 if self.Player.Left or self.Player.Right: 
                    if abs(character.Rect.right - self.Player.Rect.left) < collision_tolerance:
                        self.Player.x = self.Player.x + self.Player.speedX
                    elif abs(character.Rect.left - self.Player.Rect.right) < collision_tolerance:
                        self.Player.x = self.Player.x - self.Player.speedX # Clunky


    def update(self):
        global scroll, dt
        
        while True:
            dt = framerate.tick(35) / 1000 # DELTA TIME VERY IMPORTANT
            DISPLAY.fill((0, 0, 0))
            if self.Menu:
                self.menu.update() # Show Menu Screen  

                # Position of the buttons
                menu_rect = self.menu.buttons[0][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 75)))
                quit_rect = self.menu.buttons[1][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 150)))

                if self.menu.event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_rect.collidepoint(pg.mouse.get_pos()):
                        self.Menu = False
                    elif quit_rect.collidepoint(pg.mouse.get_pos()):
                        pg.quit(), sys.exit()

            else: # The game
               
                #pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(0, 0, get_screen_w * 4, get_screen_h * 4))
                scroll[0] += (self.Player.x - scroll[0] - get_screen_w // 2)  # Player's X Camera  (divide scroll to gain smoothness)
                scroll[1] += (self.Player.y - scroll[1] - get_screen_h // 2)  # Player's Y Camera
                # ANYTHING ELSE GOES BELOW            
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))  # John's room layer 0
                # ---LAYER 1---
                if self.PlayerRoom:                  
                   self.Characters[0].update(DISPLAY, scroll, self.Interface, self.Player) # Mau
                   self.stairs.update(self.Player, self.Interface) # Draw stairs
                   
                # ---LAYER 2---
                self.Player.update()  # Draw player

                # --- WORLD ---
                if self.PlayerRoom:                       
                    self.room_borders()

                    if self.Player.x <= 266:  self.Player.x = 266  # Bed
                    if self.Player.x < 626 and self.Player.y <= 290: self.Player.y = 290  # Desk bottom
                    if self.Player.x >= 626 and self.Player.x < 631 and self.Player.y < 290: self.Player.x = 631  # Desk right
                    if self.Player.x >= 1111 and self.Player.y > 310: self.Player.x = 1111  # Computer
                    if self.Player.x > 1111 and self.Player.y > 305 and self.Player.y < 310: self.Player.y = 305

                    # End of John's Room
                    if self.Player.Rect.colliderect(self.stairs.rect) and self.Player.InteractPoint == 2:
                        self.PlayerRoom, self.world, self.Kitchen = False, self.worlds[1], True
                elif self.Kitchen:
                    self.room_borders()

                # Global stuff that all worlds share
                self.npc_collisions()
                self.pause(pg.mouse.get_pos())  # Pause menu
            # General Function         
            pg.display.update()



