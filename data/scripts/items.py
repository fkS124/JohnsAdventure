import pygame as pg
from pygame.event import post


class Chest:
    def __init__(self, img, x, y):
        self.x, self.y = x, y
        self.surface = pg.Surface((img.get_size()))
        self.surface.blit(img,(0,0))
        self.Rect = self.surface.get_rect(center = pg.Vector2(x,y))
        self.interact_rect = pg.Rect(self.x, self.y, 0,0)
        self.interact_text = ''
        self.opened = False

    def grab_item(self, index):
        weapons = [Weapons.TrainingSword()]
        coins = [30]

        return weapons[index], coins[index]
    
    def update(self, DISPLAY, scroll, player, index):
        if self.interact_rect.colliderect(player.Rect):
            item = self.grab_item(index)
            self.interact_text = f'You found {item[1]} coins and a {item[0].__class__.__name__} ! '
            if self.opened is False and player.InteractPoint == 2:              
                player.inventory.items.append(item[0])
                player.data["coins"] += item[1]
                self.opened = not self.opened
            
        self.interact_rect = pg.Rect(self.x - scroll[0], self.y - scroll[1], 32, 64)
        self.Rect = self.surface.get_rect(center = pg.Vector2(self.x - scroll[0], self.y - scroll[1]))
        DISPLAY.blit(self.surface, self.Rect)


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
            
            font = pg.font.Font("data/database/pixelfont.ttf", 18)  
            self.text = font.render(self.__class__.__name__, True, (0, 0, 0))
            self.stat = font.render(" +1", True, (255, 0, 255))
            self.eq = font.render(">", True, (255, 0, 0))  # to replace with an image later on

            self.image = pg.Surface((self.text.get_width()+self.stat.get_width()+self.eq.get_width(), self.text.get_height()))
            self.image.fill((255, 204, 0))
            self.image.blit(self.text, (0, 0))
            self.image.blit(self.stat, (self.text.get_width(), 0))
            self.equiped = False
            self.rect = self.image.get_rect()

        def update(self, surf, pos):
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