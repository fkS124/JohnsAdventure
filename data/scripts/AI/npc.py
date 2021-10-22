'''
Credits @Marios325346

This script contains our lovely npcs! 


'''
import pygame as p
from ..utils import load, get_sprite, flip_vertical, scale, resource_path
from ..backend import UI_Spritesheet

class NPCS:

    # Mau the big ears cat 
    class Mau:
        def __init__(self, x , y):  
            self.x, self.y = p.Vector2(x, y) # Position
            self.Right = True # If False he goes left        
            self.animation_counter = self.cooldown = 0
            self.speed = 1.25
            self.Idle = self.is_talking = False # Conditions
            # Animation & Rects (Check out pygame.transform.smoothscale @fks)
            self.sheet = load(resource_path('data/sprites/mau_sheet.png'))        
            self.image, self.interact_animation = [], []       
            self.reverse_image,self.flipped_interaction = [], []
        
            for i in range(6):
                sprite = scale(get_sprite(self.sheet, 43 * i, 0, 43, 33), 2)
                if i < 3:
                    self.image.append(sprite); self.reverse_image.append(flip_vertical(sprite))
                else:
                    self.interact_animation.append(sprite); self.flipped_interaction.append(flip_vertical(sprite))

            self.interact_rect = p.Rect(self.x, self.y, self.image[0].get_width()//2, self.image[0].get_height())       
            self.interact_text = 'mau'

        def update(self, screen, scroll, player):
            # Update rect
            self.Rect = self.image[0].get_rect(center=(self.x - scroll[0], self.y - scroll[1]))       
            if self.animation_counter >= 26: self.animation_counter = 0 # Reset Animation
            self.animation_counter += 1 # Run Animation
            self.speed = 0 if player.paused or player.Rect.colliderect(self.interact_rect) else 1.25 # Change his speed based on these conditions
            if player.Rect.colliderect(self.interact_rect): # Collision with the player       
                self.Idle = True # Turn Idle animation upon collision  /  vvv If Player presses Space vvv
                if player.Interactable: 
                    self.Idle, self.is_talking = False, True      
            else: self.Idle = self.is_talking = False # Stop animation
                
            # Movement mechanism
            if not(self.x < 450 and self.Right): self.Right = False
            if self.x < 150: self.Right = True

            # Animation Mechanism
            if self.Right:
                self.interact_rect.midleft = (self.x + 15 - scroll[0], self.y - scroll[1])       
                if self.Idle:
                    screen.blit(self.interact_animation[0], self.Rect)
                elif self.is_talking:
                    screen.blit(self.interact_animation[self.animation_counter // 9], self.Rect)
                else: # Walking
                    screen.blit(self.image[self.animation_counter // 9], self.Rect)              
                    self.x += self.speed
            else:
                self.interact_rect.midright = (self.x - 15 - scroll[0], self.y - scroll[1])
                if self.Idle: # Idle Animation
                    screen.blit(self.flipped_interaction[0], self.Rect)
                elif self.is_talking:
                    screen.blit(self.flipped_interaction[self.animation_counter // 9] , self.Rect)
                else: # Walking
                    screen.blit(self.reverse_image[self.animation_counter // 9], self.Rect)               
                    self.x -= self.speed
 
    # John's sister
    class Cynthia: 
        def __init__(self, x, y):
            self.x, self.y = x, y
            self.img = load(resource_path('data/sprites/npc_spritesheet.png'))
            self.image = [scale(get_sprite(self.img, 2 + 26 * i, 1, 24, 42), 3) for i in range(3)]
            self.Rect = self.image[0].get_rect() 
            self.animation_counter = 0
            self.interact_text = 'cynthia'
            self.interact_rect = p.Rect(0,0,0,0)

        def update(self, screen, scroll, player):  
            self.interact_rect = p.Rect(self.x - scroll[0] - 30, self.y - scroll[1] + 64, 64,64)
            self.Rect = self.image[self.animation_counter // 36].get_rect(center=(self.x - scroll[0], self.y - scroll[1]))
            if self.animation_counter >= 72: self.animation_counter = 0
            self.animation_counter += 1
            screen.blit(self.image[self.animation_counter // 36] , self.Rect)
    
    # MORE NPCS....