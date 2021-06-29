import pygame, sys, random, math
from .utils import *


pygame.font.init()
font = pygame.font.Font("data/database/pixelfont.ttf", 16)


class Player(object):
    def __init__(self, x, y, screen):
        self.x, self.y, self.screen, self.InteractPoint = x, y, screen, 0 # Init + interact_point
        self.Player = load('player_beta.png')
        self.Rect = self.Player.get_rect(center=(self.x, self.y))
        self.speedX = self.speedY = 6 # Player's speed       
        self.paused = self.click = self.Interactable = False #  Features       
        self.Right = self.Down = self.Left = self.Right = self.Up = False # Movement                  

    def update(self):
        self.controls()
        if self.Up:  self.y -= self.speedY                       
        elif self.Down: self.y += self.speedY
                       
        if self.Left:  self.x -= self.speedX          
        elif self.Right: self.x += self.speedX             
          
        # Debugging
        self.screen.blit(font.render(f'Position:{[self.x, self.y]}', True, (255, 255, 255)), (self.Rect[0] - 80, self.Rect[1] - 30))
        return self.screen.blit(self.Player, self.Rect)

    def controls(self):
        
        for event in pygame.event.get():
            keys = pygame.key.get_pressed() # Keys

            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()   
            
            # Movement 
            self.Up = bool(keys[pygame.K_w])
            self.Down = bool(keys[pygame.K_s])
            self.Left = bool(keys[pygame.K_a])
            self.Right = bool(keys[pygame.K_d])

            # Features
            self.speedX = self.speedY = 6 if not(self.paused) else 0
           
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: 
                self.Interactable = True
                if self.InteractPoint < 2:
                    self.InteractPoint += 1
                else:
                    self.InteractPoint = 0
                    self.Interactable = False

            if keys[pygame.K_F12]: pygame.display.toggle_fullscreen()
            if keys[pygame.K_ESCAPE]: self.paused = True            
            if event.type == pygame.MOUSEBUTTONDOWN: self.click = True             
            else: self.click = False

class Mau(object): # LOOK AT HIM GOOOOO
    def __init__(self, x , y):
        self.x, self.y = x, y
        self.image = [double_size(load(f'data/sprites/mau/mau{i}.png', alpha = True)) for i in range(1, 4)]
        self.reverse_image = [flip_vertical(self.image[i]) for i in range(3)]
        self.interact_animation = []
        self.flipped_interaction = []
        for i in range(3):
            if i % 2 == 0:
                self.interact_animation.append(double_size(load(f'data/sprites/mau/mau_interact.png', alpha = True)))
                self.flipped_interaction.append(flip_vertical(double_size(load(f'data/sprites/mau/mau_interact.png', alpha = True))))
            else:
                self.interact_animation.append(self.image[0])
                self.flipped_interaction.append(self.reverse_image[0])


        self.Right = True # If False he goes left
        self.interact_rect = pygame.Rect(self.x, self.y, self.image[0].get_width()//2, self.image[0].get_height())  
        self.animation_counter = self.cooldown = 0
        self.speed = 1.25
        self.Idle = False
        self.is_talking = False

    def update(self, screen, scroll, interface, player, dt):
        # Update rect
        self.Rect = self.image[0].get_rect(center=(self.x - scroll[0], self.y - scroll[1]))
        
        if self.animation_counter >= 36: self.animation_counter = 0 # Reset Animation
        self.animation_counter += 1 # Run animation       
        
        #pygame.draw.rect(screen, (124,252,0), self.Rect, 1)# Mau hitbox
        pygame.draw.rect(screen, (255,0,0), self.interact_rect, 1)

        if player.Rect.colliderect(self.interact_rect):
            self.speed = 0 
            self.Idle = True
            if player.Interactable:
                self.Idle = False
                interface.update()
                interface.draw('mau', dt, player.InteractPoint)
                self.is_talking = True
            else:       
                self.Idle = True
                interface.reset()
        else:
            self.is_talking = False
            self.Idle = False
            self.speed = 1.25

       
        # Movement mechanism
        if not(self.x < 1024 and self.Right):
            self.Right = False
        if self.x < 350:
            self.Right = True

        # Animation Mechanism
        if self.Right:
            self.interact_rect.midleft = (self.x + 15 - scroll[0], self.y - scroll[1])       
            if self.Idle:
                screen.blit(self.interact_animation[1], self.Rect)
            elif self.is_talking:
                screen.blit(self.interact_animation[self.animation_counter // 18], self.Rect)
            else: # Walking
                screen.blit(self.image[self.animation_counter // 18], self.Rect)              
                self.x += self.speed
        else:
            self.interact_rect.midright = (self.x - 15 - scroll[0], self.y - scroll[1])
            if self.Idle:
                screen.blit(self.flipped_interaction[1] , self.Rect)
            elif self.is_talking:
                screen.blit(self.flipped_interaction[self.animation_counter // 18] , self.Rect)
            else: # Walking
                screen.blit(self.reverse_image[self.animation_counter // 18], self.Rect)               
                self.x -= self.speed
            