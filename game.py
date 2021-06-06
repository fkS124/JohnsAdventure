import sys, random
import pygame as pg
from pygame import mixer
from backend import *
from player import Player

# INITIALIZE
pg.init(), pg.display.set_caption("iBoxStudio Engine")
DISPLAY = pygame.display.set_mode((1280,720), flags = pg.RESIZABLE | pg.SCALED) # pg.NOFRAME for linux :penguin:
pygame.display.toggle_fullscreen() # Fullscreen's the game
framerate = pygame.time.Clock()
UIspriteSheet = UI_Spritesheet('data/ui/UI_spritesheet.png')
mouse_icon = UIspriteSheet.parse_sprite('mouse_cursor.png').convert() # Game's exclusive mouse icon!
get_screen_w, get_screen_h = DISPLAY.get_width(), DISPLAY.get_height()
scroll = [0, 0]  # player "camera"

class Interface(object): # Disabled for now
    def __init__(self):
        self.font = pygame.font.Font("data/database/pixelfont.ttf", 24)
        self.icon = UIspriteSheet.parse_sprite('interface_button.png').convert()
    def update(self, text):
        message = self.font.render(text, True, (0, 0, 0))
        DISPLAY.blit(self.icon, (get_screen_w // 2 - 460, get_screen_h // 2 + 80))
        DISPLAY.blit(message, (get_screen_w // 2 - 420, get_screen_h // 2 + 110))

# Objects
Objects = UI_Spritesheet('data/objects_spritesheet.png')

class stairs(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image = Objects.parse_sprite('stairs').convert()
        self.scaledImg = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.scaledImg.get_rect()
        self.interact_value = 0
        self.x, self.y = x, y
        self.rect.center = (x,y)
    def update(self, player_rect):
        global scroll
        self.rect.center = (self.x - scroll[0] + 78, self.y - scroll[1] + 72) # random numbers because it forced me to manually move the rect
        if self.rect.colliderect(player_rect):
            Player.isInteracting = True
        else:
            Player.isInteracting = False
        DISPLAY.blit(self.scaledImg,(self.x - scroll[0], self.y - scroll[1]))

# Classes
class MainMenu(object):
    def __init__(self):
        # ------------ Background and Animation  -------------
        self.background_l1 = [pygame.image.load('data/ui/mainmenubackground1.png').convert(),pygame.image.load('data/ui/mainmenubackground2.png').convert(), pygame.image.load('data/ui/mainmenubackground1.png').convert()]
        self.background_l2 = pygame.image.load('data/ui/mainmenutile.png')
        self.animationCounter = 0  # Important for background animation
        self.font = pygame.font.Font("data/database/pixelfont.ttf", 14)
        self.GameStart = False
        # ------------- Music Playlist -------------
        self.pb, self.qb, self.mm = 0, 0, 0  # 3 counters for each button for the music sounds
        self.music = [mixer.Sound("data/sound/forest_theme_part1.flac"), mixer.Sound("data/sound/Select_UI.wav")]
        for music in self.music:  music.set_volume(0.2)
        # ------------ Play Button UI  -------------
        self.playButton = [UIspriteSheet.parse_sprite('playbutton.png'), UIspriteSheet.parse_sprite('playbutton_hover.png')]
        self.playButtonRect = self.playButton[0].get_rect()
        self.playButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 107)
        # ------------ Quit Button UI  -------------
        self.quitButton = [UIspriteSheet.parse_sprite('quit_button.png'),UIspriteSheet.parse_sprite('quit_button_hover.png')]
        self.quitButtonRect = self.quitButton[0].get_rect()

    # ------------ UI Interface  -------------
    def PlayButton(self): 
        if self.playButtonRect.collidepoint(pg.mouse.get_pos()):
            while self.pb < 1:  # Plays sound once
                self.music[1].play()
                self.pb += 1
            DISPLAY.blit(self.playButton[1], (self.playButtonRect))
        else:
            self.pb = 0  # Reset sound counter
            DISPLAY.blit(self.playButton[0], (self.playButtonRect))

    def Buttons(self): # BLITING THE GUI, but in a more organized way
        self.buttonFunction(), self.PlayButton(), self.QuitButton()

    def QuitButton(self):  # Imagine closing the game of the year. smh 
        if self.quitButtonRect.collidepoint(pg.mouse.get_pos()):
            while self.qb < 1:
                self.music[1].play()
                self.qb += 1
            DISPLAY.blit(self.quitButton[1], (self.quitButtonRect))
        else:
            self.qb = 0
            DISPLAY.blit(self.quitButton[0], (self.quitButtonRect))
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
                if event.key == pg.K_F12:
                    pg.display.toggle_fullscreen()

    # ------------ Real time changing -------------
    def update(self):  # 26/3 == int(8.6)
        self.quitButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 174) # button position
        while self.mm < 1: 
            pygame.mouse.set_visible(False) # I dont want to set the mouse false over and over so I put it here to make sure it becomes false once
            self.music[0].play()
            self.mm += 1
        if self.animationCounter >= 104: self.animationCounter = 0
        self.animationCounter += 1
        DISPLAY.blit(self.background_l1[self.animationCounter // 36], (0, 0))
        DISPLAY.blit(self.background_l2, (0, 0))
        self.Buttons() # Display buttons (and function)
        DISPLAY.blit(mouse_icon, (pg.mouse.get_pos())) # Display our mouse!

class Game:
    def __init__(self):
        self.menu = MainMenu()
        self.world_value = 0
        self.black_screen = pygame.image.load('data/ui/black_overlay.png')
        # Objects
        self.stairs = stairs(get_screen_w // 2 + 350, 160) # X, Y
        # World images
        self.world = ''  # Current world
        self.worlds = [
            pygame.image.load('data/sprites/world/Johns_room.png').convert(),  # 0 John's Room
            pygame.image.load('data/sprites/world/kitchen.png').convert(),  # 1 Kitchen Room
        ]
        # Worlds
        self.Menu = True
        self.PlayerRoom, self.Kitchen, self.Route1 = False, False, False
        # Interface
        self.Interface = Interface() # not working yet
        # ---------- Menu Icon -------
        self.MenuIcon = [UIspriteSheet.parse_sprite('menu_button.png').convert(),UIspriteSheet.parse_sprite('menu_button_hover.png').convert()]
        self.MenuIconRect = self.MenuIcon[0].get_rect()
        self.MenuIconRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 174)
        self.menupl = 0

    def pause(self):
        if Player.paused:
            pygame.mouse.set_visible(False) # Hide actual cursor
            Player.speed = 0 # Aha now you can't move >:)))
            DISPLAY.blit(self.black_screen, (0, 0))
            self.menu.QuitButton()
            self.menu.quitButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 241) # Change its position
            isTouchingMenu = self.MenuIconRect.collidepoint(pygame.mouse.get_pos())
            if isTouchingMenu:
                while self.menupl < 1:
                    self.menu.music[1].play()
                    self.menupl += 1
                DISPLAY.blit(self.MenuIcon[1], self.MenuIconRect)
                if Player.click:
                    self.PlayerRoom, self.Menu, self.menu.GameStart = False, True, False
            else:
                self.menupl = 0
                DISPLAY.blit(self.MenuIcon[0], self.MenuIconRect)
            if Player.click and self.menu.quitButtonRect.collidepoint(pygame.mouse.get_pos()):
                pygame.quit(), sys.exit()
            DISPLAY.blit(mouse_icon, (pygame.mouse.get_pos())) # Display the mouse cursor

    def update(self):
        global scroll
        while True:
            DISPLAY.fill((0, 0, 0))
            if self.Menu:
                self.menu.update()
                if self.menu.GameStart:
                    self.Menu, self.PlayerRoom, self.world = False, True, self.worlds[0]
            else:
                pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(0, 0, get_screen_w * 4, get_screen_h * 4)) # Just a black background
                scroll[0] += (Player.x - scroll[0] - get_screen_w//2) # Player's X Camera
                scroll[1] += (Player.y - scroll[1] - get_screen_h//2) # Player's Y Camera
                # ANYTHING ELSE GOES BELOW            
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1])) # John's room layer 0
                #---LAYER 1---
                if self.PlayerRoom: self.stairs.update(Player.PlayerRect) # Draw the stairs
                #---LAYER 2---
                Player.update() # Draw player
                #---Collisions---
                if self.PlayerRoom:    
                    # ------ Collisions (shrinked) ------
                    if Player.x > get_screen_w - 40: Player.x = get_screen_w - 40  # Right walls
                    elif Player.x < (get_screen_w- get_screen_w) + 40: Player.x = get_screen_w - get_screen_w + 40 # Left walls
                    if Player.y > get_screen_h - 40:  Player.y = get_screen_h - 40 # Down walls
                    elif Player.y < (get_screen_h - get_screen_h) + 150: Player.y = (get_screen_h - get_screen_h) + 150 # Up walls
                    if Player.x <= 266:  Player.x = 266 # Bed
                    if Player.x < 626 and Player.y <= 290: Player.y = 290 # Desk bottom
                    if Player.x >= 626 and Player.x < 631 and Player.y < 290: Player.x = 631 # Desk right
                    if Player.x >= 1111 and Player.y > 310: Player.x = 1111   # Computer
                    if Player.x > 1111 and Player.y > 305 and Player.y < 310: Player.y = 305
                    #pygame.draw.rect(DISPLAY, (124,252,0), Player.PlayerRect, 1)
                    #pygame.draw.rect(DISPLAY, (124,252,0), self.stairs.rect, 1)
                    if self.stairs.rect.colliderect(Player.PlayerRect):
                        if Player.Interactable:
                            self.Interface.update('Go to kitchen?')
                            #if Player.InteractPoint == 2:
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
            framerate.tick(40)
            pygame.display.update()

Player = Player(get_screen_w // 2, get_screen_h // 2, DISPLAY)
def Engine(game=Game()):
    game.update()
if __name__ == '__main__':
    Engine()
