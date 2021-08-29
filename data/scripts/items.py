import pygame as pg
from pygame import display
from pygame.event import post
from .utils import load, get_sprite



class Chest:
    def __init__(self, x, y):
        self.x, self.y, self.sheet = x, y, load('data/items/chest.png')
        self.img = [get_sprite(self.sheet,  0, 0, 74 * i, 90) for i in range(4)]
        self.Rect = pg.Rect(0,0,0,0) # Empty rect that will be filled later
        self.a = 0 # Animation counter
    
    def update(self, screen, scroll, player, index):
        self.Rect = self.img[self.a // 7].get_rect(topleft = (self.x - 74, self.y))
        self.a += 1 # Run animation
        if self.a >= 26: self.a = 0 # 0 resets it, so if I want the last frame you will put 26
        
        screen.blit(self.img[self.a // 7], self.Rect)
        
        #screen.blit(self.reverse_image[self.animation_counter // 9], self.Rect)     
                
        


'''
class Chest:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sheet = load('data/items/chest.png')
        
        self.img = [get_sprite(self.sheet,  0, 0, 74 * i, 90) for i in range(4)]
        
        self.Rect = self.img[0].get_rect(center = pg.Vector2(x,y))
        self.interact_rect = pg.Rect(self.x, self.y, 0,0)
        self.interact_text = ''
        self.opened = False
        self.ac = 0 # Animation counter
        print(self.img)

    def grab_item(self, index):
        weapons = [Weapons.TrainingSword()]
        coins = [30]
        return weapons[index], coins[index]
    
    def update(self, DISPLAY, scroll, player, index):
        
        if self.ac >= 26: self.ac = 0
        self.ac += 1
    
        if self.interact_rect.colliderect(player.Rect):
            item = self.grab_item(index)
            self.interact_text = f'You found {item[1]} coins and a {item[0].__class__.__name__} ! '
            if self.opened is False and player.InteractPoint == 2:              
                player.inventory.items.append(item[0])
                player.data["coins"] += item[1]
                self.opened = not self.opened
            
        self.interact_rect = pg.Rect(self.x - scroll[0], self.y - scroll[1], 32, 64)
        
        DISPLAY.blit(self.img[self.ac // 7], self.Rect)
'''

class Items:
    """This class will contain all the objects"""

    class NullItem:  # Reference Model

        def __init__(self):
            font = pg.font.Font("data/database/pixelfont.ttf", 24)
            self.text = font.render("NullItem", True, (0, 0, 0))
            self.image = pg.Surface((self.text.get_size()))
            self.image.fill((255, 204, 0))
            self.image.blit(self.text, (0, 0))
            self.rect = self.image.get_rect()

        def handle_clicks(self, pos):
            pass

        def update(self, surf, pos):
            self.rect.topleft = pos
            surf.blit(self.image, pos)


class Weapons:

    class TrainingSword: # Reference Model

        def __init__(self):
            
            self.font = pg.font.Font("data/database/pixelfont.ttf", 18)  
            self.text = self.font.render(self.__class__.__name__, True, (0, 0, 0))
            self.stat = self.font.render(" +1", True, (255, 0, 255))
            self.eq = self.font.render(">", True, (255, 0, 0))  # to replace with an image later on
            self.damage = 15

            self.image = pg.Surface((self.text.get_width()+self.stat.get_width()+self.eq.get_width(), self.text.get_height()))
            self.image.fill((255, 204, 0))
            self.image.blit(self.text, (0, 0))
            self.image.blit(self.stat, (self.text.get_width(), 0))
            self.equiped = False
            self.rect = self.image.get_rect()

        def update(self, surf, pos, dmg):
            d_dmg = self.damage - dmg  # getting the difference from the player's damages and the current item's damages
            txt_stat = (" +" if d_dmg >= 0 else " ")+str(d_dmg)
            color = (0, 255, 0) if d_dmg > 0 else ((100 if d_dmg == 0 else 255), (100 if d_dmg == 0 else 0), (100 if d_dmg == 0 else 0))  # grey if the d_dmg is 0, green if > 0, red if < 0
            self.stat = self.font.render(txt_stat, True, color)  # resetting the stat rendering

            self.image.fill((255, 204, 0))
            if not self.equiped:
                self.image.blit(self.text, (0, 0))
                self.image.blit(self.stat, (self.text.get_width(), 0))
            else:
                self.image.blit(self.eq, (0, 0))
                self.image.blit(self.text, (self.eq.get_width(), 0))
                self.image.blit(self.stat, (self.text.get_width()+self.eq.get_width(), 0))
            self.rect.topleft = pos
            surf.blit(self.image, pos)

        def handle_clicks(self, pos):
            if self.rect.collidepoint(pos): self.set_equiped() # Un/Equips clicked item

        def set_equiped(self):
            self.equiped = not self.equiped