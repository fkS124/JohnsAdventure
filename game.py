import sys, random

import pygame as pg
from pygame import mixer
from backend import *
from player import Player

# INITIALIZE
pg.init(), pg.display.set_caption("iBoxStudio Engine")
DISPLAY = pygame.display.set_mode((1280,720), flags = pg.RESIZABLE | pg.SCALED | pg.NOFRAME)
pygame.display.toggle_fullscreen()

pygame.mouse.set_visible(False)
framerate = pygame.time.Clock()
UIspriteSheet = UI_Spritesheet('data/ui/UI_spritesheet.png')
mouse_icon = UIspriteSheet.parse_sprite('mouse_cursor.png').convert() # Game's exclusive mouse icon!
get_screen_w, get_screen_h = DISPLAY.get_width(), DISPLAY.get_height()

scroll = [0, 0]  # player "camera"
class cloud:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.cloudSpeed = 0.2
        self.image = pygame.image.load('data/ui/cloud.png').convert()
        self.image.set_colorkey((255, 255, 255))
    def update(self):
        if self.x <= -100:  # if the cloud is gone
            self.x = get_screen_w # teleport it to the right of the screen
        else:
            self.x -= self.cloudSpeed  # Move the cloud to the left
        return DISPLAY.blit(self.image, (self.x, self.y))

class Interface(object): # Disabled for now
    def __init__(self):
        self.font = pygame.font.Font("data/fonts/pixelfont.ttf", 24)
        self.icon = UIspriteSheet.parse_sprite('interface_button.png').convert()

    def update(self, text):
        message = self.font.render(text, True, (0, 0, 0))
        DISPLAY.blit(self.icon, (get_width / 4 - 460, get_height / 4 + 80))
        DISPLAY.blit(message, (get_width / 4 - 420, get_height / 4 + 110))


# Objects
Objects = UI_Spritesheet('data/objects_spritesheet.png')

class stairs(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image = Objects.parse_sprite('stairs').convert()
        self.scaledImg = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.image.get_rect()
        self.interact_value = 0
        self.rect.center = (x, y)

    def update(self, player_rect):
        if self.rect.colliderect(player_rect):
            Player.isInteracting = True
        else:
            Player.isInteracting = False
        DISPLAY.blit(self.scaledImg, self.rect)


# Classes
class MainMenu(object):
    def __init__(self):
        # ------------ Background and Animation  -------------
        self.background_l1 = [pygame.image.load('data/ui/mainmenubackground1.png').convert(),
                              pygame.image.load('data/ui/mainmenubackground2.png').convert(),
                              pygame.image.load('data/ui/mainmenubackground1.png').convert()]
        self.background_l2 = pygame.image.load('data/ui/mainmenutile.png')
        self.animationCounter = 0  # Important for background animation
        self.font, self.font2 = pygame.font.Font("data/fonts/pixelfont.ttf", 18), pygame.font.Font(
            "data/fonts/pixelfont.ttf", 14)
        self.GameStart = False
        # ------------- Music Playlist -------------
        self.pb, self.ab, self.qb, self.mm = 0, 0, 0, 0  # 4 counters because I can't work with only one  
        self.music = [mixer.Sound("data/sound/forest_theme_part1.flac"), mixer.Sound("data/sound/Select_UI.wav")]
        for music in self.music:  music.set_volume(0.2)
        # ------------ Play Button UI  -------------
        self.playButton = [UIspriteSheet.parse_sprite('playbutton.png'),
                           UIspriteSheet.parse_sprite('playbutton_hover.png')]
        self.playButtonRect = self.playButton[0].get_rect()
        self.playButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 107)
        # ------------ About Button UI  -------------
        self.aboutButton = [UIspriteSheet.parse_sprite('about_button.png'),
                            UIspriteSheet.parse_sprite('about_button_hover.png')]
        self.aboutButtonRect = self.aboutButton[0].get_rect()
        self.aboutButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 174)
        # ------------ Quit Button UI  -------------
        self.quitButton = [UIspriteSheet.parse_sprite('quit_button.png'),
                           UIspriteSheet.parse_sprite('quit_button_hover.png')]
        self.quitButtonRect = self.quitButton[0].get_rect()
        self.quitButtonRect.center = (get_screen_w//2 - 7, get_screen_h//2 + 241)
        # ------------ About Button UI  -------------
        self.Catalog = pygame.transform.scale(UIspriteSheet.parse_sprite('catalog_button.png'),(450 * 2, int(228 + 228 * 1.5)))
        self.CatalogRect = self.Catalog.get_rect()
        self.CatalogRect.center = (get_screen_w//2, get_screen_h//2)
        # ------------ Clouds  -------------
        self.gap, self.y_gap = 0, 0
        self.Clouds = []
        self.Cloud_X_end, self.Cloud_Y_end = get_screen_w * 2, get_screen_h * 2  # End of Player's DISPLAY

        for i in range(5):  # Generate some clouds
            self.gap += 120  # The gap between each cloud
            self.y_gap += 20
            self.Clouds.append(
                cloud(random.randint(self.Cloud_X_end - 250, self.Cloud_X_end) - self.gap, 0 + self.y_gap))

    # ------------ UI Interface  -------------
    def PlayButton(self):
        isTouchingPlay = self.playButtonRect.collidepoint(pg.mouse.get_pos())
        if isTouchingPlay:
            while self.pb < 1:  # Plays sound once
                self.music[1].play()
                self.pb += 1
            DISPLAY.blit(self.playButton[1], (self.playButtonRect))
        else:
            self.pb = 0  # Reset sound counter
            DISPLAY.blit(self.playButton[0], (self.playButtonRect))

    def AboutButton(self):
        isTouchingAbout = self.aboutButtonRect.collidepoint(pg.mouse.get_pos())
        if isTouchingAbout:
            while self.ab < 1:
                self.music[1].play()
                self.ab += 1
            DISPLAY.blit(self.aboutButton[1], (self.aboutButtonRect))
            DISPLAY.blit(self.Catalog, self.CatalogRect)
            #vvvv The part below is going to be optimized vvvv
            DISPLAY.blit(self.font.render("Thank you for downloading Johns's Adventure!", True, (0, 0, 0)),(get_screen_w//4, get_screen_h//2 - 200))
            DISPLAY.blit(self.font.render('Project made by:', True, (0, 0, 0)),(get_screen_w//3 + 100, get_screen_h//2 - 100))
            DISPLAY.blit(self.font2.render('@MariosPapaz  Programming/Design', True, (0, 0, 0)),(get_screen_w//4 + 100, get_screen_h//2 - 70))
            DISPLAY.blit(self.font2.render('@TohaU  Music Design', True, (0, 0, 0)),(get_screen_w//4 + 100, get_screen_h//2 - 45))
            DISPLAY.blit(self.font2.render('@ImPoPzz Story Writing', True, (0, 0, 0)),(get_screen_w//4 + 100, get_screen_h//2 - 20))
            DISPLAY.blit(self.font.render('Support our game by sharing it to your friends!', True, (0, 0, 0)), (get_screen_w//4, get_screen_h//2 + 70))
        else:
            self.ab = 0
            DISPLAY.blit(self.aboutButton[0], (self.aboutButtonRect))

    def Buttons(self):
        self.buttonFunction(), self.PlayButton(), self.QuitButton(), self.AboutButton()

    def CloudsGoBrr(self):
        for cloud in self.Clouds:
            cloud.update()  # Updates each cloud (wish I could do this in one line)

    def QuitButton(self):  # Imagine closing the game of the year.
        isTouchingQuit = self.quitButtonRect.collidepoint(pg.mouse.get_pos())
        if isTouchingQuit:
            while self.qb < 1:
                self.music[1].play()
                self.qb += 1
            DISPLAY.blit(self.quitButton[1], (self.quitButtonRect))
        else:
            self.qb = 0
            DISPLAY.blit(self.quitButton[0], (self.quitButtonRect))

    # ------------  Mechanism  -------------
    def buttonFunction(self):  # The gears between the interface and user input
        isTouchingPlay, isTouchingAbout, isTouchingQuit = self.playButtonRect.collidepoint(
            pg.mouse.get_pos()), self.aboutButtonRect.collidepoint(
            pg.mouse.get_pos()), self.quitButtonRect.collidepoint(pg.mouse.get_pos())
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:  # Mouse
                if isTouchingPlay:
                    self.music[0].stop()
                    self.GameStart = True
                elif isTouchingQuit:
                    pg.quit(), sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == pg.K_ESCAPE:  # Keyboard
                    pg.quit(), sys.exit()

    # ------------ Real time changing -------------
    def update(self):  # 26/3 == int(8.6)
        while self.mm < 1: 
            self.music[0].play()
            self.mm += 1
        if self.animationCounter >= 104: self.animationCounter = 0
        self.animationCounter += 1
        DISPLAY.blit(self.background_l1[self.animationCounter // 36], (0, 0))
        DISPLAY.blit(self.background_l2, (0, 0)), self.CloudsGoBrr() 
        self.Buttons() # Display buttons (and function)
        DISPLAY.blit(mouse_icon, (pg.mouse.get_pos())) # Display our mouse!

class Game:
    def __init__(self):
        self.menu = MainMenu()
        self.SpawnCounter = 0
        self.world_value = 0
        self.black_DISPLAY = pygame.image.load('data/ui/black_overlay.png')
        # Objects
        #self.stairs = stairs(int(get_width // 2) - 250, 160)
        # World images
        self.world = ''  # Current world
        self.worlds = [
            pygame.image.load('data/sprites/world/Johns_room.png').convert(),  # 0 John's Room
            pygame.image.load('data/sprites/world/kitchen.png').convert(),  # 1 Kitchen Room
            pygame.image.load('data/sprites/world/route1.png').convert()  # 2 Route 1
        ]
        self.world_rect = ''  # Gets current world's rect
        # Worlds
        self.Menu = True
        self.PlayerRoom, self.Kitchen, self.Route1 = False, False, False

        # Interface
        self.Interface = Interface()
        # Interface text
        # ---------- Menu Icon -------
        self.MenuIcon = [UIspriteSheet.parse_sprite('menu_button.png').convert(),
                         UIspriteSheet.parse_sprite('menu_button_hover.png').convert()]
        self.MenuIconRect = self.MenuIcon[0].get_rect()
        self.MenuIconRect.center = (get_screen_w - 7, get_screen_h + 174)
        self.menupl = 0

    def pause(self):
        if Player.paused:
            Player.velX, Player.velY = 0, 0
            DISPLAY.blit(self.black_screen, (0, 0))
            self.menu.QuitButton()
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
                pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(0, 0, get_width * 4, get_height * 4))
                DISPLAY.blit(self.world, (0 - scroll[0], 0 - scroll[1]))
                #Scroll (Player's camera)
                scroll[0] += (Player.x - scroll[0] - get_screen_w//2 + 50)
                scroll[1] += (Player.y - scroll[1] - get_screen_h//2)
                # if self.PlayerRoom:
                #    self.stairs.update(Player.player_rect)
                Player.update(scroll)
                # John's Room
                if self.PlayerRoom:
                    pass
                    # ------ Collisions ------
                    #if Player.x > get_width // 2:  # Right walls
                        #Player.x = get_width // 2
                    #elif Player.x < (get_width // 2 - get_width // 2) + 40:  # Left walls
                        #Player.x = get_width // 2 - get_width // 2 + 40

                    #if Player.y > get_height // 2 - 40:  # Down walls
                        #Player.y = get_height // 2 - 40
                    #elif Player.y < (get_height // 2 - get_height // 2) + 150:  # Up walls
                        #Player.y = (get_height // 2 - get_height // 2) + 150

                    #if Player.x <= 266:  # Bed
                        #Player.x = 266

                    #if Player.x < 626 and Player.y <= 290:  # Desk bottom
                        #Player.y = 290
                    #if Player.x >= 626 and Player.x < 631 and Player.y < 290:  # Desk Right
                        #Player.x = 631

                    # Computer
                    #if Player.x >= 1111 and Player.y > 310:
                        #Player.x = 1111
                    #if Player.x > 1111 and Player.y > 305 and Player.y < 310:
                        #Player.y = 305

                    # Player.x = self.world_rect.left + 5
                    # Stairs check
                    #if Player.x >= 900 and Player.x <= 1080 and Player.y >= 80 and Player.y <= 190:
                    #    if Player.interactable:
                    #        self.Interface.update('Go to kitchen?')
                    #        if Player.interact_value == 2:
                    #            self.PlayerRoom, self.Kitchen, self.world_value = False, True, 1
                    #            self.world = self.worlds[1]
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

                # Global stuff that all worlds share        
                self.pause()  # Pause menu
            # General Function         
            framerate.tick(40)
            pygame.display.update()


Player = Player(get_screen_w // 2 - 50, get_screen_h // 2, DISPLAY)



def Engine(game=Game()):
    game.update()


if __name__ == '__main__':
    Engine()
