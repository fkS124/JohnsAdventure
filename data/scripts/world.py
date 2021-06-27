
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

        self.text_display = ['' for i in range(4)] # Create 4 empty text renders
        self.text_surfaces = [self.font.render(self.text_display[i], True, (0,0,0)) for i in range(4)] # font render each of them
    
    def draw(self, path, dt):    
        text = self.data[path]['text'] # Import from Json the AI/UI 's text
        self.timer += dt # Speed of text/delta_time
        if self.timer > 0.030:
                self.current_text_index += 1 # Next letter
                if self.current_text_index < len(text):
                    if text[self.current_text_index] == ' ': # If there is a space
                        self.current_text_index += 1 
                    else:
                        self.sound.play() # Play Sound
                
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

        self.Characters = [
            Player(get_screen_w // 2, get_screen_h // 2, DISPLAY), # 0 John
            Mau(350,350) # 1 Mau
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
        if self.Characters[0].paused:
            pygame.mouse.set_visible(False)  # Hide actual cursor
            self.Characters[0].speed = 0  # Aha now you can't move >:)))
            DISPLAY.blit(self.black_screen, (0, 0))
            self.menu.QuitButton()
            self.menu.quitButtonRect.center = (get_screen_w // 2 - 7, get_screen_h // 2 + 241)  # Change its position
            isTouchingMenu = self.MenuIconRect.collidepoint(pygame.mouse.get_pos())
            if isTouchingMenu:
                while self.menupl < 1:
                    self.menu.music[1].play()
                    self.menupl += 1
                DISPLAY.blit(self.MenuIcon[1], self.MenuIconRect)
                if self.Characters[0].click:
                    self.PlayerRoom, self.Menu, self.menu.GameStart,self.Characters[0].paused = False, True, False, False
            else:
                self.menupl = 0
                DISPLAY.blit(self.MenuIcon[0], self.MenuIconRect)
            if self.Characters[0].click and self.menu.quitButtonRect.collidepoint(pygame.mouse.get_pos()):
                pygame.quit(), sys.exit()
            DISPLAY.blit(mouse_icon, (pygame.mouse.get_pos()))  # Display the mouse cursor
        else:
            self.Characters[0].speed = 6 # Player can move again

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
                scroll[0] += (self.Characters[0].x - scroll[0] - get_screen_w // 2)  # Player's X Camera
                scroll[1] += (self.Characters[0].y - scroll[1] - get_screen_h // 2)  # Player's Y Camera
                # ANYTHING ELSE GOES BELOW            
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))  # John's room layer 0
                # ---LAYER 1---
                if self.PlayerRoom: self.stairs.update(self.Characters[0].Rect), self.Characters[1].update(DISPLAY, scroll)  # Draw the stairs
                # ---LAYER 2---
                self.Characters[0].update()  # Draw player
                # ---Collisions---
                if self.PlayerRoom:
                    
                    # Check for collision
                    #print(self.Characters[0].Rect)
                    #print(self.Characters[0].x, self.Characters[0].y
                    if self.Characters[0].Up or self.Characters[0].Down or self.Characters[0].Left or self.Characters[0].Right:
                        if self.Characters[0].Rect.colliderect(self.Characters[1].Rect):
                            # Top border
                            if abs(self.Characters[1].Rect.top - self.Characters[0].Rect.bottom) < 10:
                                    print('Top Collision')
                                    self.Characters[0].Rect.bottom = self.Characters[1].Rect.top
                            # Bottom Border
                            if abs(self.Characters[1].Rect.bottom - self.Characters[0].Rect.top) < 10:
                                    print('Bottom Collision')
                            
                            # Right Border
                            if abs(self.Characters[1].Rect.left - self.Characters[0].Rect.right) < 10:
                                    print('Left Collision')
                            # Left Border
                            if abs(self.Characters[1].Rect.right - self.Characters[0].Rect.left) < 10:
                                    print('Right Collision')
                   


                    #if self.Characters[0].Rect.top <= self.Characters[1].Rect.

                    # ------ Coordinate collisions (borders) ------
                    for character in self.Characters:
                        if character.x > get_screen_w - 40:
                            character.x = get_screen_w - 40  # Right walls
                        elif character.x < (get_screen_w - get_screen_w) + 40:
                            character.x = get_screen_w - get_screen_w + 40  # Left walls
                        if character.y > get_screen_h - 40:
                            character.y = get_screen_h - 40  # Down walls
                        elif character.y < (get_screen_h - get_screen_h) + 150:
                            character.y = (get_screen_h - get_screen_h) + 150  # Up walls
                        if character.x <= 266:  character.x = 266  # Bed
                        if character.x < 626 and character.y <= 290: character.y = 290  # Desk bottom
                        if character.x >= 626 and character.x < 631 and character.y < 290: character.x = 631  # Desk right
                        if character.x >= 1111 and character.y > 310: character.x = 1111  # Computer
                        if character.x > 1111 and character.y > 305 and character.y < 310: character.y = 305


                   
                    if self.stairs.rect.colliderect(self.Characters[0].Rect):
                        if self.Characters[0].Interactable:
                            self.Interface.update() # Draw catalog
                            self.Interface.draw('stairs', dt) # Draw text
                            # if Player.InteractPoint == 2:
                            #    self.PlayerRoom, self.Kitchen, self.world_value = False, True, 1
                            #    self.world = self.worlds[1]

                ''' THIS PART WORKS BUT I'LL DISABLED IT UNTIL JULY + I GOT FEATURES TO ADD FIRST 
                # Kitchen
                elif self.Kitchen:
                    # Kitchen collisions
                    if Player.y < 40:
                        if Player.x < 500:
                            Player.y = 40
                        elif Player.x >= 500 and Player.x < 505:
                            Player.x = 505
                    # Table collisions
                    if Player.y < 590:
                        if Player.y >= 585:
                            if Player.x < 280:  # Bottom
                                Player.y = 590
                        if Player.y > 205:
                            if Player.y < 210 and Player.x < 280:  # Top
                                Player.y = 205
                            elif Player.x > 280 and Player.x < 285:
                                Player.x = 285  # Right
                    # Interface 
                    if Player.x > 1160 and Player.y < 80:
                        if Player.interactable:  # John's Room
                            if Player.interact_value < 2:
                                self.Interface.update('Go to your room?')
                            else:
                                self.world, self.Kitchen, self.PlayerRoom = self.worlds[0], False, True
                    # Outdoors
                    if Player.x > 450 and Player.x < 700 and Player.y > 550:
                        if Player.interactable:  # Outside
                            if Player.interact_value < 2:
                                self.Interface.update('Go to outside?')
                            else:
                                self.world, self.Kitchen, self.Route1 = self.worlds[2], False, True
                elif self.Route1:
                    pass
                '''
                # Global stuff that all worlds share        
                self.pause()  # Pause menu
            # General Function         
            pygame.display.update()



