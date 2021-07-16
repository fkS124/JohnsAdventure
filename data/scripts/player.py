import pygame as p
import sys, math
from .utils import *
p.font.init()
font = p.font.Font("data/database/pixelfont.ttf", 16)
debug_font = p.font.Font("data/database/pixelfont.ttf", 12)

class Player(object):
    def __init__(self, x, y, screen, debug, interface):
        self.x, self.y = p.Vector2(x,y)
        self.screen, self.InteractPoint, self.Interface = screen, 0, interface
        self.Player = load('player_beta.png')
        self.Rect = self.Player.get_rect(center=(self.x, self.y))
        self.speedX = self.speedY = 6 # Player's speed       
        self.paused = self.click = self.Interactable = False #  Features       
        self.Right = self.Down = self.Left = self.Right = self.Up = False # Movement         
        self.debug = debug # Debugging
        self.interact_text = ''
        self.is_interacting = False
        self.position = p.Vector2(x,y)

    def update(self):
        self.controls()
        ''' Movement '''
        if self.Up:  self.y -= self.speedY                       
        elif self.Down: self.y += self.speedY                   
        if self.Left:  self.x -= self.speedX          
        elif self.Right: self.x += self.speedX      
        
        if self.Interactable and self.is_interacting:
            self.Interface.draw(self.interact_text)

        ''' Draw Player '''
        self.screen.blit(self.Player, self.Rect)
         
        ''' Debug Mode '''
        if self.debug:          
            i = 1
            for name, value in self.__dict__.items():
               self.position = p.Vector2(self.x,self.y) # update it
               text = debug_font.render(f"{name}={value}", True, (255,255,255))
               self.screen.blit(text, (20, 0 + 15 * i))
               i+=1


    def controls(self):  
        for event in p.event.get():
            keys = p.key.get_pressed() # Keys pressed
            if event.type == p.QUIT: p.quit(), sys.exit()
            self.Up, self.Down, self.Left, self.Right = bool(keys[p.K_w]), bool(keys[p.K_s]), bool(keys[p.K_a]), bool(keys[p.K_d])          
            self.speedX = self.speedY = 6 if not(self.paused) else 0 # If player pauses the game
                        
            # ----- Keybinds -----         
            if event.type == p.KEYDOWN:
                ''' Toggle Fullscreen '''
                if event.key == p.K_F12:  p.display.toggle_fullscreen()

                ''' Interaction '''
                if event.key == p.K_SPACE: 
                    self.Interactable = True 
                    self.InteractPoint += 1 

                # Reset Interaction
                if self.Up or self.Down or self.Right or self.Left or self.InteractPoint == 3: 
                    self.InteractPoint, self.Interactable = 0, False
                    self.is_interacting = False
                    self.Interface.reset();                 

                '''Pause the game'''
                if event.key == p.K_ESCAPE:
                      if self.paused: self.paused = False                
                      else: self.paused = True   
            # ----- Mouse -----                       
            if event.type == p.MOUSEBUTTONDOWN: 
                self.click = True             
            else: 
                self.click = False

class Mau(object):
    def __init__(self, x , y):  
        self.x, self.y = p.Vector2(x, y) # Position
        self.Right = True # If False he goes left        
        self.animation_counter = self.cooldown = 0
        self.speed = 1.25
        self.Idle = self.is_talking = False # Conditions
        # Animation & Rects (Check out pygame.transform.smoothscale @fks)
        self.image = [double_size(load(f'data/sprites/mau/mau{i}.png', alpha = True)) for i in range(1, 4)]
        self.reverse_image = [flip_vertical(self.image[i]) for i in range(3)]
        self.interact_rect = p.Rect(self.x, self.y, self.image[0].get_width()//2, self.image[0].get_height()) 
        self.interact_animation = [double_size(load(f'data/sprites/mau/mau_interact.png', alpha = True))  if i % 2 == 0 else double_size(load(f'data/sprites/mau/idle_mau.png', alpha = True)) for i in range(3)]             
        self.flipped_interaction = [flip_vertical(frame) for frame in self.interact_animation]  # Same list but flipped images

    def update(self, screen, scroll, player):
        # Update rect
        self.Rect = self.image[0].get_rect(center=(self.x - scroll[0], self.y - scroll[1]))       
        if self.animation_counter >= 36: self.animation_counter = 0 # Reset Animation
        self.animation_counter += 1 # Run Animation
        self.speed = 0 if player.paused or player.Rect.colliderect(self.interact_rect) else 1.25 # Change his speed based on these conditions
        if player.Rect.colliderect(self.interact_rect): # Collision with the player       
            self.Idle = True # Turn Idle animation upon collision  /  vvv If Player presses Space vvv
            if player.Interactable: 
                self.Idle, self.is_talking = False, True      
        else: self.Idle = self.is_talking = False # Stop animation
             
        # Movement mechanism
        if not(self.x < 768 and self.Right): self.Right = False
        if self.x < 150: self.Right = True

        # Text
        if self.interact_rect.colliderect(player.Rect):
            player.interact_text = 'mau'
            player.is_interacting = True

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
            if self.Idle: # Idle Animation
                screen.blit(self.flipped_interaction[1] , self.Rect)
            elif self.is_talking:
                screen.blit(self.flipped_interaction[self.animation_counter // 18] , self.Rect)
            else: # Walking
                screen.blit(self.reverse_image[self.animation_counter // 18], self.Rect)               
                self.x -= self.speed
            