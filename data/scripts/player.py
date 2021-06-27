import pygame, sys, random, math
from .utils import *


pygame.font.init()
font = pygame.font.Font("data/database/pixelfont.ttf", 16)


class Player(object):
    def __init__(self, x, y, screen):
        self.x, self.y = x, y
        self.pos = [self.x, self.y]  # Player's position (debugging)
        self.screen = screen
        self.speed = 6  # Player's speed
        self.paused = False  # if player has paused the game
        self.click = False  # when Player clicks
        self.Interactable = False  # Player's interaction with the environment
        self.InteractPoint = 0
        # Movement
        self.Right = self.Down = self.Left = self.Right = self.Up = False
        self.Player = pygame.image.load('player_beta.png').convert()
        self.Rect = self.Player.get_rect(center=(self.x, self.y))

    def update(self):
        self.controls()
        self.InfoText = font.render(f'Position:{self.pos}', True, (255, 255, 255))
        # Movement
        if self.Up:
            self.y -= self.speed
        elif self.Down:
            self.y += self.speed
        if self.Left:
            self.x -= self.speed
        elif self.Right:
            self.x += self.speed
        self.pos = [self.x, self.y]  # DEBUGGING FOR WORLD POSITION
        self.screen.blit(self.InfoText, (self.Rect[0] - 80, self.Rect[1] - 30))
        return self.screen.blit(self.Player, self.Rect)

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            
            self.click = bool(event.type == pygame.MOUSEBUTTONDOWN) # Player left click

            if event.type == pygame.KEYDOWN:
                self.Interactable = False # If player clicks any button the interaction will stop
                if event.key == pygame.K_SPACE:
                    #print(self.InteractPoint)
                    self.Interactable = True
                    if self.InteractPoint != 2:
                        self.InteractPoint += 1
                    else:
                        self.InteractPoint = 0
                if event.key == pygame.K_ESCAPE: # Toggle Pause screen
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                if event.key == pygame.K_d:
                    self.Right = True
                if event.key == pygame.K_a:
                    self.Left = True
                if event.key == pygame.K_s:
                    self.Down = True
                if event.key == pygame.K_w:
                    self.Up = True
                if event.key == pygame.K_F12:
                    pygame.display.toggle_fullscreen() # Toggle fullscreen
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.Right = False
                if event.key == pygame.K_a:
                    self.Left = False
                if event.key == pygame.K_s:
                    self.Down = False
                if event.key == pygame.K_w:
                    self.Up = False


class Mau(object): # LOOK AT HIM GOOOOO
    def __init__(self, x , y):
        self.x, self.y = x, y
        self.image = [double_size(load(f'data/sprites/mau/mau{i}.png', alpha = True)) for i in range(1, 4)]
        self.Rect = self.image[0].get_rect()
        self.Left = self.Right = self.Up = self.down = False   
        self.animation_counter = 0
        # Τριγονομετρία :'(
        self.dx = self.dy = self.distance = 0
        # Other stuff
        self.mx = self.my = self.cooldown = self.switchConter = 0  

    ''' Reference
    cos = -1  Left (dx)
    sin = -1 (dy) Up
    syn = 1 (dy) down
    cos = 1 (dx) Right 
    _
    '''

    def move(self, scroll):
        # Update rect
        self.Rect = self.image[0].get_rect(topleft=(self.x - scroll[0], self.y - scroll[1]))

        '''
        # Calculations
            if self.cooldown > 100:
                self.mx, self.my = random.randint(300, 550), random.randint(-5, 5)
                radians = math.atan2(self.my - self.x, self.my - self.y)
                self.distance = int(math.hypot(self.mx - self.x, self.my - self.y))
                self.dx = math.cos(radians)
                self.dy = math.sin(radians)
                self.cooldown = 0
            else:
                self.switchConter = 0
                self.cooldown += 1
                self.mx = self.my = 0   
            # Moving Mau
            if self.distance:
                self.distance -= 1
                self.x += self.dx * 1.25
                self.y += self.dy * 1.25
        '''
        #self.active()

    def active(self):
        self.animation_counter += 1
        if self.mx != 0:
            if self.dx < 0:
                while self.switchConter < 1:
                    print('Mau is moving left')
                    self.ScaledImg = [pygame.transform.flip(image, True, False) for image in self.ScaledImg]
                    self.switchConter = 1
            if self.dx > 0:
                while self.switchConter < 1:
                    print('Mau is moving Right')  
                    self.ScaledImg = [pygame.transform.flip(image, False, False) for image in self.ScaledImg]
                    self.switchConter = 1  
    def update(self, screen, scroll):
        if self.animation_counter >= 52: self.animation_counter = 0 # Reset Animation
        self.animation_counter += 1 # Run animation
        
        self.move(scroll)
        pygame.draw.rect(screen, (124,252,0), self.Rect, 1)# Mau hitbox
        screen.blit(self.image[self.animation_counter // 18], self.Rect)
