
import sys, random, json
import pygame as pg
from pygame import mixer

pg.init(), pg.display.set_caption("iBoxStudio Engine")
DISPLAY = pg.display.set_mode((1280, 720))
#  Uncomment the below when you stop debugging
#DISPLAY = pg.display.set_mode((1280, 720), flags=pg.RESIZABLE | pg.SCALED)  # pg.NOFRAME for linux :penguin:
#pg.display.toggle_fullscreen()
# Data
from .backend import *
from .player import *

if '--debug' in sys.argv:
    print("Oh you sussy you're trying to debug me huh?")
    debug = True
else:
    debug = False

# INITIALIZE
framerate = pygame.time.Clock()
UIspriteSheet = UI_Spritesheet('data/ui/UI_spritesheet.png')
get_screen_w, get_screen_h = DISPLAY.get_width(), DISPLAY.get_height()
mouse_icon = UIspriteSheet.parse_sprite('mouse_cursor.png').convert()  # Game's exclusive mouse icon!
scroll = [0, 0]  # player "camera"
dt = framerate.tick(35) / 1000 # Delta time :D
paused_sound = False
font = pg.font.Font("data/database/pixelfont.ttf", 24)

# Fonts
blacksword = pg.font.Font("data/database/Blacksword.otf", 113) # I use this only for the logo

class Interface(object): 
    def __init__(self):
        self.icon = scale(UIspriteSheet.parse_sprite('interface_button.png').convert(), 8)
        self.current_text_index = self.timer = 0
        self.text_pos = (get_screen_w // 2 - 420, get_screen_h // 2 + 110) # Position of the first sentence
        with open('data/database/language.json') as f: self.data = json.load(f); f.close() # Read Json and close it     
        self.sound = pg.mixer.Sound('data/sound/letter_sound.wav'); self.sound.set_volume(0.2) # Insert music and change sound     
        self.text_display = ['' for i in range(4)] # Create 4 empty text renders
        self.text_surfaces = [font.render(self.text_display[i], True, (0,0,0)) for i in range(4)] # font render each of them

     # Resets text
    def reset(self): self.current_text_index  =  0
    
    def draw(self, path):
        if path: # If string is not empty
            DISPLAY.blit(self.icon, (155 , get_screen_h // 2 + 80)) # UI
            text = self.data[path]['text'] # Import from Json the AI/UI 's text
            self.timer += dt # Speed of text/delta_time
            if self.timer > 0.030:
                    self.current_text_index += 1 # Next letter
                    if self.current_text_index < len(text):
                        self.current_text_index += 1 
                        if not (text[self.current_text_index] == ' '):  self.sound.play()  # if there isn't space            
                    # --- UPDATE CONTENT ---
                    self.text_display = [text[44 * i : min(self.current_text_index, 44 * (i + 1))] for i in range(4)] # Update letters strings
                    self.text_surfaces = [font.render(text, True, (0,0,0)) for text in self.text_display]  # Transform them into a surface                        
                    self.timer = 0 # Reset timer /  End of if statement                 
            for i, surface in enumerate(self.text_surfaces): # Blits the text 
                DISPLAY.blit(surface, (self.text_pos[0], self.text_pos[1] + i * 30))          

# Classes
class MainMenu(object):
    def __init__(self):
        # ------------ Background and Animation  -------------
        self.background = pg.transform.scale(load('data/ui/background.png'), (1280,720))
        self.event = None # event for keys
        self.logo = [blacksword.render("John's Adventure", True, (255 * i, 255 * i,255 * i)) for i in range(2)]

        # ------------- Music Playlist -------------
        self.button_font = pg.font.Font("data/database/pixelfont.ttf", 34)
        self.music = [mixer.Sound("data/sound/forest_theme_part1.flac"), mixer.Sound("data/sound/Select_UI.wav")]
        for music in self.music:  music.set_volume(0.2)
        # --------- GUI ----------
        self.buttons = [[scale(UIspriteSheet.parse_sprite('button.png'), 4),scale(UIspriteSheet.parse_sprite('button_hover.png'), 4)] for i in range(2)]
        self.gui_text = [self.button_font.render("Play", True, (255,255,255)), self.button_font.render("Quit", True, (255,255,255))]

    def update(self, mouse_p):  
        DISPLAY.blit(self.background,(0,0)) # Background
        for i, button in enumerate(self.buttons): # Buttons     
            button_rect = button[0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 75 * (i + 1)))) # Rect of image in sublist
            if button_rect.collidepoint(mouse_p):
                DISPLAY.blit(button[1], button_rect) # Show hovered image
            else:    
                DISPLAY.blit(button[0], button_rect) # Show normal image       
            DISPLAY.blit(self.gui_text[i], (button_rect[0] + button[0].get_width()//4, button_rect[1])) # Centered text    
         
        # Logo
        for i, text in enumerate(self.logo): 
            DISPLAY.blit(text, (get_screen_w//6+20, get_screen_h//2 - 190 - (2 * i)))

        for event in pg.event.get():
            self.event = event
            if event.type == pg.QUIT: pg.quit(), sys.exit()                       
            if event.type == pygame.KEYDOWN and event.key == pg.K_F12: pg.display.toggle_fullscreen()
                               
class Game:
    def __init__(self):
        self.menu = MainMenu()
        self.Menu = True # If False , the adventure starts
        #------- World -----
        self.worlds = [
            pg.transform.scale(load('data/sprites/world/Johns_room.png'), (1280,720)), # 0 John's Room
            pg.transform.scale(load('data/sprites/world/kitchen.png'), (1280,720))  # 1 Kitchen Room
        ]
        self.world = self.worlds[0]  # Current world      
        self.PlayerRoom = self.Kitchen = self.Forest = False  # Worlds   
        self.Player = Player(get_screen_w // 2, get_screen_h // 2, DISPLAY, debug, Interface()) # The player
        self.Characters = [Mau(150,530)]    

        #------- Objects -----
        ''' Lists of non OOP objects '''
        self.objects_p = [
            [pg.Vector2(10,90), pg.Vector2(5,500), pg.Vector2(450, 40)], # John's Room
            [pg.Vector2(20, 250), pg.Vector2(280,300), pg.Vector2(10,0), pg.Vector2(1020, 440)] # Kitchen Room
        ]
        self.objects = [
            [pg.Rect(0,0, 430,360), pg.Rect(0,0, 72, 214), pg.Rect(0,0, 410, 192)], # John's Room     
            [pg.Rect(0,0, 250,350), pg.Rect(0,0, 64, 256), pg.Rect(0,0, 860, 230), pg.Rect(0,0, 256, 200)]
        ] 

    def pause(self, mouse):
        if self.Player.paused:
            surface = pygame.Surface((get_screen_w,get_screen_h), pygame.SRCALPHA)
            surface.fill((0,0,0)); surface.set_alpha(235); DISPLAY.blit(surface, (0,0)) # Draws black screen with opacity
            for character in self.Characters: character.speed = 0 # Stop characters frog
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

    # Αλγόριθμοι Παγκόσμιας Σύγκρουσης Οντοτήτων / Player Collision System with Entities (UNDER MANAGEMENT)
    '''object collision and npc will be seperate until I find a way to merge them'''
    def object_collisions(self, index: int):
        for i,object in enumerate(self.objects[index]): # where index is a sublist
            object.topleft = (self.objects_p[index][i].x - scroll[0], self.objects_p[index][i].y - scroll[1]) # 0 is its static position when the world moves
            if self.Player.Rect.colliderect(object):            
                 if self.Player.Up or self.Player.Down:  # Up / Down borders
                    if abs(object.bottom - self.Player.Rect.top) < 10:
                        self.Player.y = self.Player.y + self.Player.speedY
                    elif abs(object.top - self.Player.Rect.bottom) < 10:
                        self.Player.y = self.Player.y - self.Player.speedY # Clunky             
                 if self.Player.Left or self.Player.Right:  # Left / Right borders
                    if abs(object.right - self.Player.Rect.left) < 10:
                        self.Player.x = self.Player.x + self.Player.speedX
                    elif abs(object.left - self.Player.Rect.right) < 10:
                        self.Player.x = self.Player.x - self.Player.speedX # Clunky
            if debug: pg.draw.rect(DISPLAY, (255,255,255), object, width = 1)      
    
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
        while True:
            dt, mouse_p = framerate.tick(35) / 1000, pg.mouse.get_pos() # Framerate Indepence and Mouse position
            DISPLAY.fill((0, 0, 0))
            if self.Menu:
                self.menu.update(mouse_p) # Show Menu Screen  
                # Position of the buttons
                menu_rect , quit_rect = self.menu.buttons[0][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 75))), self.menu.buttons[1][0].get_rect(center=((get_screen_w//2, get_screen_h//2 + 150)))
                if self.menu.event.type == pg.MOUSEBUTTONDOWN:
                     if menu_rect.collidepoint(mouse_p):  self.Menu = False; self.PlayerRoom = True
                     elif quit_rect.collidepoint(mouse_p): pg.quit(), sys.exit()
            else: # The game
                scroll[0] += (self.Player.x - scroll[0] - get_screen_w // 2)
                scroll[1] += (self.Player.y - scroll[1] - get_screen_h // 2)                
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))  # World Background Image
                ''' John's Room '''
                if self.PlayerRoom:                  
                   self.Characters[0].update(DISPLAY, scroll, self.Player) # Mau      
                   self.room_borders(), self.object_collisions(0) # Collisions   
                   if self.Player.y < 270:
                       self.Player.is_interacting = True
                       if self.Player.x >= 680 and self.Player.x <= 870:
                            self.Player.interact_text = 'computer'
                       elif self.Player.x >= 490 and self.Player.x < 650:
                            self.Player.interact_text = 'desk'
                   # Stairs
                   if self.Player.Rect.colliderect(pygame.Rect(get_screen_w // 2 + 334 - scroll[0], 150 - scroll[1], 195, 130)):
                        self.Player.interact_text = 'stairs'
                        self.Player.is_interacting = True
                        if self.Player.InteractPoint == 2:
                            self.PlayerRoom, self.world, self.Kitchen = False, self.worlds[1], True
                            self.Player.x , self.Player.y = 1080, 250
                            self.Player.is_interacting = False
                    # End of John's Room         
                elif self.Kitchen:
                    self.room_borders(), self.object_collisions(1) # Collisions

                    ''' Kitchen '''
                    if self.Player.y < 270 and self.Player.x >= 420 and self.Player.x <= 810:
                       self.Player.is_interacting = True
                       if self.Player.x < 570:
                           self.Player.interact_text = 'kitchen'
                       else:
                           self.Player.interact_text = 'sink'

                    ''' Stairs '''
                    if self.Player.x >= 1005 and self.Player.y < 240 and self.Player.Interactable:
                        self.Player.interact_text = 'stairs_up'
                        self.Player.is_interacting = True
                        if self.Player.InteractPoint == 2:
                            self.PlayerRoom, self.world, self.Kitchen = True, self.worlds[0], False
                            self.Player.x, self.Player.y = 1080, 320
                            self.Player.is_interacting = False

                # Global stuff that all worlds share
                self.Player.update()  # Draw player
                self.npc_collisions()
                self.pause(mouse_p)  # Pause menu
            # General Function         
            pg.display.update()



