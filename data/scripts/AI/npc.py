'''
Credits @Marios325346

This script contains our lovely npcs! 


'''
from random import choice
import pygame as p
import pygame as pg
from pygame import sprite
from ..utils import load, get_sprite, flip_vertical, scale, resource_path
from ..backend import UI_Spritesheet


class NPC:

    """Base class for every NPC."""

    def __init__(self, 
                 moving:bool,
                 pos:pg.Vector2,
                 sprite_sheet_path:str,
                 idle:bool=False,
                 idle_left=None,
                 idle_right=None,
                 idle_down=None,
                 idle_up=None,
                 move_anim:bool=False,
                 move_left=None,
                 move_right=None,
                 move_down=None,
                 move_up=None
                 ):

        self.IDENTITY = "NPC"  # -> useful to check fastly the type of object we're dealing with

        self.move_ability = {
            "left": True,
            "right": True,
            "up": True,
            "down": True
        }

        # STATE
        self.state = "move" if moving else "idle"
        self.moving = moving
        self.velocity = pg.Vector2(1, 1)
        self.interacting = False
        self.interactable = True

        # SPRITESHEET
        self.sprite_sheet = load(resource_path(sprite_sheet_path))
        
        # ANIMATION
        self.anim_delay = 0
        self.anim_index = 0
        self.anim_duration = 100

        self.idle = idle
        self.move_anim = move_anim
        self.direction = "left"
        self.it_re_size = (100, 100)
        self.interaction_rect = None
        
        self.move_manager = {
            "right": self.load_from_spritesheet(move_right) if self.move_anim else None,
            "left": self.load_from_spritesheet(move_left) if self.move_anim else None,
            "up": self.load_from_spritesheet(move_up) if self.move_anim else None,
            "down": self.load_from_spritesheet(move_down) if self.move_anim else None
        }

        self.idle_manager = {
            "right": self.load_from_spritesheet(idle_right) if self.idle else None,
            "left": self.load_from_spritesheet(idle_left) if self.idle else None,
            "up": self.load_from_spritesheet(idle_up) if self.idle else None,
            "down": self.load_from_spritesheet(idle_down) if self.idle else None
        }

        self.anim_manager = {
            "idle": self.idle_manager,
            "move": self.move_manager
        }

        # IMAGES AND COORDINATES
        self.image = pg.Surface((1, 1))
        self.rect = self.image.get_rect(center=pos)

    def load_from_spritesheet(self, coords):
        if coords == [0, 0, 0, 0, 0, 0] or coords is None:
            return None
        if coords[-1] == "flip":
            return [flip_vertical(scale(get_sprite(self.sprite_sheet, coords[0]+coords[2]*i, coords[1], coords[2], coords[3]), coords[4])) for i in range(coords[5])]
        return [scale(get_sprite(self.sprite_sheet, coords[0]+coords[2]*i, coords[1], coords[2], coords[3]), coords[4]) for i in range(coords[5])]
    
    def state_manager(self):
        if self.interacting:
            self.state = "idle"
        elif self.moving:
            self.state = "move"
        else:
            self.state = "idle"

    def animate(self):
        
        current_anim = self.anim_manager[self.state]
        if type(current_anim) is dict:
            current_anim = current_anim[self.direction]

        if pg.time.get_ticks() - self.anim_delay > self.anim_duration:
            self.anim_delay = pg.time.get_ticks()
            self.anim_index = (self.anim_index + 1) % len(current_anim)
            self.image = current_anim[self.anim_index]
            self.rect = self.image.get_rect(center=self.rect.center)

    def update_interaction_rect(self, scroll):
        match self.direction:
            case "left":
                self.interaction_rect = pg.Rect(self.rect.x-self.it_re_size[0], self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
            case "right":
                self.interaction_rect = pg.Rect(self.rect.right, self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
            case "up":
                self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.y-self.it_re_size[1], *self.it_re_size)
            case "down":
                self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.bottom, *self.it_re_size)
        self.interaction_rect.topleft-=scroll

    def logic(self, scroll):
        self.state_manager()
        self.animate()
        self.update_interaction_rect(scroll)

    def update(self, screen, scroll):
        self.logic(scroll)
        screen.blit(self.image, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        pg.draw.rect(screen, (0, 0, 255), self.interaction_rect, 1)


class MovingNPC(NPC):

    def __init__(self, 
                 movement:str,  # "random" | "lateral" | "vertical"
                 range_rect:pg.Rect,  # basically the delimitations of the npc's movements
                 velocity:pg.Vector2,
                 pos:pg.Vector2,
                 sprite_sheet_path:str,
                 idle:bool=False,
                 idle_left=None,
                 idle_right=None,
                 idle_down=None,
                 idle_up=None,
                 move_anim:bool=False,
                 move_left=None,
                 move_right=None,
                 move_down=None,
                 move_up=None
                 ):

        super().__init__(
            True,pos,sprite_sheet_path,idle,idle_left,idle_right,idle_down,idle_up,move_anim,move_left,move_right,move_down,move_up
        )

        self.movement = movement
        self.range_rect = range_rect
        self.velocity = velocity

    def check_outside_rect(self):
        match self.direction:
            case "left":
                return True if not pg.Rect(self.rect.x-self.velocity[0], self.rect.y, *self.rect.size).colliderect(self.range_rect) else False
            case "right":
                return True if not pg.Rect(self.rect.x+self.velocity[0], self.rect.y, *self.rect.size).colliderect(self.range_rect) else False
            case "up":
                return True if not pg.Rect(self.rect.x, self.rect.y-self.velocity[1], *self.rect.size).colliderect(self.range_rect) else False
            case "down":
                return True if not pg.Rect(self.rect.x, self.rect.y+self.velocity[1], *self.rect.size).colliderect(self.range_rect) else False

    def move(self):
        match self.direction:
            case "left":
                self.rect.x -= self.velocity[0] if self.move_ability["left"] else 0
            case "right":
                self.rect.x += self.velocity[0] if self.move_ability["right"] else 0
            case "down":
                self.rect.y += self.velocity[1] if self.move_ability["up"] else 0
            case "up":
                self.rect.y -= self.velocity[1] if self.move_ability["down"] else 0

    def switch_directions(self, blocked_direction=None):
        directions = ["left", "right", "down", "up"]
        directions.remove(self.direction)
        if blocked_direction is not None and blocked_direction in directions:
            directions.remove(blocked_direction)

        match self.movement:
            case "random":
                self.direction = choice(directions)
            case "lateral":
                if blocked_direction is not None :
                    if self.direction == blocked_direction == "left":
                        self.direction = "right"
                    elif self.direction == blocked_direction == "right":
                        self.direction = "left"
                else:
                    self.direction = "right" if self.direction == "left" else "left"

            case "vertical":
                if blocked_direction is not None :
                    if self.direction == blocked_direction == "up":
                        self.direction = "down"
                    elif self.direction == blocked_direction == "down":
                        self.direction = "up"
                else:
                    self.direction = "up" if self.direction == "down" else "down"

    def logic(self, scroll):
        super().logic(scroll)

        if self.check_outside_rect():

            self.switch_directions()

        self.move()

    def update(self, screen, scroll):
        return super().update(screen, scroll)


class Mau(MovingNPC):

    def __init__(self, dep_pos, range_):

        super().__init__(
            pos=dep_pos,
            movement="lateral", 
            range_rect=pg.Rect(*dep_pos, *range_),
            velocity=pg.Vector2(1.25, 1.25),
            sprite_sheet_path='data/sprites/mau_sheet.png',
            idle=True, 
            idle_right=[43*3, 0, 43, 33, 2, 3],
            idle_left=[43*3, 0, 43, 33, 2, 3, "flip"],
            move_anim=True,
            move_right=[0, 0, 43, 33, 2, 3],
            move_left=[0, 0, 43, 33, 2, 3, "flip"])
        self.it_re_size = (75, 100)


class Cynthia(NPC):

    def __init__(self, pos):
        super().__init__(
            moving=False,
            pos=pos,
            sprite_sheet_path='data/sprites/npc_spritesheet.png',
            idle=True,
            idle_right=[0, 1, 26, 42, 3, 3]
        )
        self.direction = "right"
        self.state = "idle"
        self.anim_duration = 750
        self.it_re_size = (100, 125)


"""
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

"""