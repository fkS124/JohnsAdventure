import pygame as pg




class Items:
    
    """This class will contain all the objects"""

    class NullItem:

        def __init__(self):

            font = pg.font.Font("data/database/pixelfont.ttf", 25)

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

    class BasicSword:

        def __init__(self):
            
            font = pg.font.Font("data/database/pixelfont.ttf", 25)

            self.text = font.render("Basic Sword", True, (0, 0, 0))
            self.stat = font.render(" +1", True, (255, 0, 255))
            self.eq = font.render("* ", True, (255, 0, 0))  # to replace with an image later on

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
            if self.rect.collidepoint(pos):
                self.set_equiped()

        def set_equiped(self):
            self.equiped = not self.equiped