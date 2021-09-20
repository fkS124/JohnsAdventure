from threading import setprofile
from data.scripts.backend import UI_Spritesheet
from types import prepare_class
from typing import Tuple
import pygame as p
import math

from pygame import mouse
from pygame.time import get_ticks
from .utils import load, get_sprite, scale, flip_vertical
from .inventory import Inventory

p.font.init()
font = p.font.Font("data/database/pixelfont.ttf", 16)
debug_font = p.font.Font("data/database/pixelfont.ttf", 12)

class Player(object):
    def __init__(self, x, y, screen, debug, interface, data, ui_sprite_sheet):
        self.x, self.y = self.position = p.Vector2(x,y)
        self.screen, self.InteractPoint, self.Interface = screen, 0, interface
       
        self.Rect = p.Rect(self.x - 46, self.y, 64, 64)
        self.speedX = self.speedY = 6 # Player's speed       
        self.paused = self.click = self.Interactable = self.is_interacting = False #  Features       
        self.Right = self.Down = self.Left = self.Right = self.Up = False # Movement         
        self.debug, self.interact_text = debug, '' # Debugging and Interaction
        self.data = data
        self.inventory = Inventory(self.screen, ui_sprite_sheet, font)

        # States
        self.walking = False

        # Animation
        self.sheet = load('data/sprites/john.png')
        
        
        
        self.a_index = 0
        
        #scale(get_sprite(self.sheet, 52, 46 * row, 46,52), 3) for i in range(10)
        
        
        # Frame Width: 46
        # Frame Height: 52
        
        self.walk_right = [scale(get_sprite(self.sheet, 46 * i, 0, 46, 52),3) for i in range(5)]
        self.walk_left = [flip_vertical(image) for image in self.walk_right]
        
        self.walk_up = [scale(get_sprite(self.sheet, 46 * i, 52, 46, 52),3) for i in range(5)]
        self.walk_down = [scale(get_sprite(self.sheet, 46 * i, 104, 46, 52),3) for i in range(5)]
        

        self.combo_1_3_right = [scale(get_sprite(self.sheet, 46 * 5 + 46 * i, 0, 46,52), 3) for i in range(5)]
        self.combo_1_3_left = [flip_vertical(image) for image in self.combo_1_3_right]
        
        
        self.combo_2_right = [scale(get_sprite(self.sheet, 46 * 10 + 46 * i, 0, 46,52), 3) for i in range(5)]
        self.combo_2_left = [flip_vertical(image) for image in self.combo_2_right]
        
        
        self.looking_down = False
        self.looking_up = False
        self.looking_right = False
        self.looking_left = False

        

        self.index_attack_animation = 0
        self.delay_attack_animation = 0
        self.restart_animation = True
        self.attacking_frame = self.combo_1_3_left[self.index_attack_animation]
        
        ''' Stats'''
        self.health = 110
        self.damage = 10
        # recalculate the damages, considering the equiped weapon
        self.modified_damages = self.damage + (self.inventory.get_equiped("Weapon").damage if self.inventory.get_equiped("Weapon") is not None else 0)
        
        ''' UI '''
        self.health_box = scale(ui_sprite_sheet.parse_sprite('health'),5)
        self.heart = scale(ui_sprite_sheet.parse_sprite('heart'), 4)
        self.hp_box_rect = self.health_box.get_rect(topleft = (self.screen.get_width() - self.health_box.get_width() - 10, 20))
        
        '''  Combat System '''
        self.crosshair,  self.attack_pointer = load('data/ui/crosshair.png', True), load('data/ui/attack_pointer.png', True)
        self.dash = False
        self.dash_t = p.time.get_ticks()

        self.attacking = False
        self.current_combo = 0
        self.last_attack = 3 # The number of attacks the player deals to the enemy, last is rewarding extra damage
        self.last_attacking_click = 0  # ticks value in the future
        self.attack_speed = 1750 # still to be determined
        self.attack_cooldown = 500  # still to be determined
        self.max_combo_multiplier = 1.025
        self.last_combo_hit_time = 0
        self.next_combo_available = True

        self.attacking_hitbox = None
        self.attacking_hitbox_size = (self.Rect.height*2, self.Rect.width)  # reversed when up or down -> (100, 250)
        self.rooms_objects = []

    def check_for_hitting(self):

        for obj in self.rooms_objects:
            if hasattr(obj, "attackable"):
                if obj.attackable:  
                    if self.attacking_hitbox.colliderect(obj.Rect):
                        obj.deal_damage(self.modified_damages) if self.current_combo != self.last_attack else obj.deal_damage(self.modified_damages*self.max_combo_multiplier)

    def attack(self):

        click_time = p.time.get_ticks()
        if not self.attacking and self.inventory.get_equiped("Weapon") is not None:
            self.attacking = True
            self.last_attacking_click = click_time

            self.current_combo += 1
            self.next_combo_available = False

            self.update_attack()
            self.check_for_hitting()

        else:
            if not self.next_combo_available:
                pass
            else:
                if click_time - self.last_attacking_click > self.attack_speed:
                    self.attacking = False
                    self.current_combo = 0
                else:
                    
                    self.restart_animation = True
                    self.current_combo += 1
                    self.last_attacking_click = click_time
                    self.update_attack()
                    self.check_for_hitting()
                    self.next_combo_available = False

                    if self.current_combo < self.last_attack:
                        pass
                    else:
                        self.last_combo_hit_time = p.time.get_ticks()

    def update_attack(self):
        # print("Up:", self.looking_up, "Down:", self.looking_down, "Left:", self.looking_left, "Right:", self.looking_right)
        
        # print("Current combo :", self.current_combo, "Time elapsed :", p.time.get_ticks()-self.last_attacking_click, "Cooldown :", p.time.get_ticks()-self.last_attacking_click>self.attack_cooldown, "Index :", self.index_attack_animation)

        if self.attacking:

            # sets the attacking hitbox according to the direction 
            if self.looking_up:
                self.attacking_hitbox = p.Rect(self.Rect.x, self.Rect.y-2*self.attacking_hitbox_size[1], self.attacking_hitbox_size[1], self.attacking_hitbox_size[0])
            elif self.looking_down:
                self.attacking_hitbox = p.Rect(self.Rect.x, self.Rect.y+self.attacking_hitbox_size[1], self.attacking_hitbox_size[1], self.attacking_hitbox_size[0])
            elif self.looking_left:
                self.attacking_hitbox = p.Rect(self.Rect.x-self.attacking_hitbox_size[0], self.Rect.y, self.attacking_hitbox_size[0], self.attacking_hitbox_size[1])
            elif self.looking_right:
                self.attacking_hitbox = p.Rect(self.Rect.x+self.attacking_hitbox_size[1], self.Rect.y, self.attacking_hitbox_size[0], self.attacking_hitbox_size[1])

            # animation delay of 100 ms
            if p.time.get_ticks() - self.delay_attack_animation > 100 and self.restart_animation:
                
                # select the animation list according to where the player's looking at
                if self.looking_right:
                    curr_anim = self.combo_1_3_right if self.current_combo == 1 or self.current_combo == 3 else self.combo_2_right
                elif self.looking_left:
                    curr_anim = self.combo_1_3_left if self.current_combo == 1 or self.current_combo == 3 else self.combo_2_left
                elif self.looking_down:
                    curr_anim = []  # -> add here down anim
                elif self.looking_up:
                    curr_anim = []  # -> add here up anim

                if self.index_attack_animation + 1 < len(curr_anim):  # check if the animation didn't reach its end
                        self.delay_attack_animation = p.time.get_ticks()  # reset the delay
                        self.attacking_frame = curr_anim[self.index_attack_animation+1]  # change the current animation frame
                        self.index_attack_animation+=1  # increment the animation index
                else:
                    print("ended animation")
                    self.restart_animation = False  # don't allow the restart of the animation until a next combo is reached
                    self.index_attack_animation = 0  # reset the animation index, without changing the frame in order to stay in "pause"
                    self.next_combo_available = True  # allow to attack again


            p.draw.rect(self.screen, (255,255,255), self.Rect)
            if self.looking_right:  # blitting the frame, with the right coordinates according to the side of the attack
                self.screen.blit(self.attacking_frame, self.attacking_frame.get_rect(left=self.Rect.right, y=self.Rect.y))
            elif self.looking_left:
                self.screen.blit(self.attacking_frame, self.attacking_frame.get_rect(right=self.Rect.right, y=self.Rect.y))
            elif self.looking_down:
                pass  # -> add here down anim
            elif self.looking_up:
                pass  # -> add here up anim

            # reset the whole thing if the combo reach his end and the animation of the last hit ended too
            if self.current_combo == self.last_attack and not self.restart_animation and not self.index_attack_animation:
                self.attacking = False  # stop attack
                self.current_combo = 0  # reset combo number
                self.next_combo_available = True  # allow to attack again
                self.restart_animation = True  # allow to restart an animation

            # show hitbox
            # p.draw.rect(self.screen, (255, 0, 0), self.attacking_hitbox)

            if p.time.get_ticks() - self.last_attacking_click > self.attack_speed:
                self.attacking = False
                self.current_combo = 0
                self.next_combo_available = True
                self.restart_animation = True

                # RESET ANIMATION HERE
        
    def health_bar(self):
        p.draw.rect(self.screen, (255,0,0), p.Rect(self.hp_box_rect.x + 25,self.hp_box_rect.y  + 20, self.health, 25)) # Health bar
        self.screen.blit(self.health_box, self.hp_box_rect)
        self.screen.blit(self.heart, (self.hp_box_rect.x + 10 , self.hp_box_rect.y + 15))
    
    def set_looking(self, dir_:str):
        if dir_ == "up":
            self.looking_up, self.looking_down, self.looking_right, self.looking_left = True, False, False, False
        elif dir_ == "down":
            self.looking_up, self.looking_down, self.looking_right, self.looking_left = False, True, False, False
        elif dir_ == "left":
            self.looking_up, self.looking_down, self.looking_right, self.looking_left = False, False, False, True
        elif dir_ == "right":
            self.looking_up, self.looking_down, self.looking_right, self.looking_left = False, False, True, False

    def update(self):

        # recalculate the damages, considering the equiped weapon
        self.modified_damages = self.damage + (self.inventory.get_equiped("Weapon").damage if self.inventory.get_equiped("Weapon") is not None else 0)

        self.controls()
        self.health_bar()    
        if not self.inventory.show_menu:
            
            if not self.attacking: # if he is not attacking, allow him to move
                ''' Movement '''
                if self.Up: 
                    self.y -= self.speedY 
                    dash_vel = -25 
                elif self.Down: 
                    self.y += self.speedY   
                    dash_vel = 25
                
                if self.Left: 
                    self.x -= self.speedX   
                    dash_vel = -25 if not self.Down else 25 # Diagonal
                # Note: Add here a smoother diagonal dash if combat system demands it
                elif self.Right: 
                    self.x += self.speedX 
                    dash_vel = 25 if not self.Up else -25 # Diagonal
            
            else: # He is attacking
                dash_vel = 0
                    
            ''' Animation '''
            if self.a_index >= 27: self.a_index = 0
            self.a_index += 1
        else: # Player is looking at the inventory,therefore dont allow him to animate walking
            self.a_index = 0 # Play only first frame

        if self.dash:
            if p.time.get_ticks() - self.dash_t > 30:
                self.dash = False          
            if self.Up or self.Down:
                self.y += dash_vel
            elif self.Left or self.Right:
                self.x += dash_vel

        ''' Animation '''
        player_pos = self.Rect[0], self.Rect[1] - 80
        # ? Mouse position
        mouse_p = p.mouse.get_pos()
        
        # ! Noooo you can't make calculations for silly stuff , haha  trig go brrrrrrr
        angle = math.atan2(mouse_p[0] - self.Rect.midbottom[0], mouse_p[1] - self.Rect.midbottom[1]) 
        x, y = player_pos[0] - math.cos(angle), player_pos[1] - math.sin(angle) 
        image = p.transform.rotate(self.attack_pointer, math.degrees(angle))
        ring_pos = (x - image.get_width()//2 + 50, y - image.get_height()//2  + 120)
        self.screen.blit(image, ring_pos)
        self.update_attack()

        # Player animation
        if not self.attacking:
            if mouse_p[0] > 550 and mouse_p[0] < 750:
                if mouse_p[1] < self.Rect.y: # ? Up
                    self.set_looking("up")
                    if self.walking:
                            self.screen.blit(self.walk_up[self.a_index // 7], player_pos) 
                    else:
                        self.screen.blit(self.walk_up[0], player_pos)
                else: # ? Down
                    self.set_looking("down")
                    if self.walking:
                            self.screen.blit(self.walk_down[self.a_index // 7], player_pos) 
                    else:
                        self.screen.blit(self.walk_down[0], player_pos)
            else: # Left/Right
                if mouse_p[0] <= self.Rect.x: # ? Left
                    self.set_looking("left")
                    if self.walking:
                            self.screen.blit(self.walk_left[self.a_index // 7], player_pos) 
                    else:
                        self.screen.blit(self.walk_left[0], player_pos)
                else: # ? Right
                    self.set_looking("right")
                    if self.walking:
                            self.screen.blit(self.walk_right[self.a_index // 7], player_pos) 
                    else:
                        self.screen.blit(self.walk_right[0], player_pos)
                       
            
        if not self.Up and not self.Down and not self.Right and not self.Left:
            self.walking = False
      
        # if player presses interaction key and is in a interaction zone
        if self.Interactable and self.is_interacting:
            self.Interface.draw(self.interact_text)
     
        if self.debug:          
            i = 1
            for name, value in self.__dict__.items():
               self.position = p.Vector2(self.x,self.y) # update it
               text = debug_font.render(f"{name}={value}", True, (255,255,255))
               self.screen.blit(text, (20, 0 + 15 * i))
               i+=1

        self.screen.blit(self.crosshair, self.crosshair.get_rect(center=mouse_p)) # Mouse Cursor
        self.inventory.update(self)  # sending its own object in order that the inventory can access to the player's damages


    def controls(self):       
        for event in p.event.get():   
            keys = p.key.get_pressed()
            if event.type == p.QUIT: p.quit(); raise SystemExit

            if not self.inventory.show_menu: # if player is looking at the inventory dont allow him to press keys besides Inventory
                self.Up, self.Down, self.Left, self.Right = keys[self.data["controls"][0]], keys[self.data["controls"][1]], keys[self.data["controls"][2]], keys[self.data["controls"][3]]      
            self.speedX = self.speedY = 6 if not(self.paused) else 0 # If player pauses the game
            
                        
            # ----- Keybinds -----         
            if event.type == p.KEYDOWN:
                ''' Toggle Fullscreen '''
                if event.key == p.K_F12:  p.display.toggle_fullscreen()
                
                ''' Dash Ability'''
                if event.key == p.K_LSHIFT:             
                    if p.time.get_ticks() - self.dash_t > 1500: # 1.5 Second (not yet balanced)
                        self.dash, self.dash_t = True, p.time.get_ticks()
                        
                ''' Inventory '''
                if event.key == p.K_e:
                    self.inventory.set_active()

                if self.inventory.show_menu:
                    if event.key == p.K_UP: # scroll up
                        self.inventory.scroll_up()
                    
                    if event.key == p.K_DOWN: # scroll down
                        self.inventory.scroll_down()
                        self.srl_gap += 1

                ''' Interaction '''
                if event.key == self.data["controls"][4]: 
                    self.Interactable = True 
                    self.InteractPoint += 1 

                # Reset Interaction
                if self.Up or self.Down or self.Right or self.Left or self.InteractPoint == 3:
                    self.walking = True                                
                    self.InteractPoint, self.Interactable = 0, False
                    self.is_interacting = False
                    self.Interface.reset()

                '''Pause the game'''
                if event.key == p.K_ESCAPE:
                      if self.paused: self.paused = False                
                      else: self.paused = True   
            # ----- Mouse -----                       
            if event.type == p.MOUSEBUTTONDOWN: 
                if event.button == 1:
                    self.inventory.handle_clicks(event.pos)

                if self.inventory.show_menu:
                    if event.button == 4:  # scroll up
                        if self.inventory.im_rect.collidepoint(event.pos):  # check if the mouse is colliding with the rect
                            self.inventory.scroll_up()
                    if event.button == 5:  # scroll down
                        if self.inventory.im_rect.collidepoint(event.pos):
                            self.inventory.scroll_down()  
                else:
                    if event.button == 1:
                        self.attack()

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
        self.sheet = load('data/sprites/mau_sheet.png')        
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
        if not(self.x < 768 and self.Right): self.Right = False
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
 




class Cynthia(object): # The time has come
    def __init__(self, x, y, sprite):
        self.x, self.y = x, y
        self.image = [scale(get_sprite(sprite, 2 + 26 * i, 1, 24, 42), 3) for i in range(3)]
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