import pygame as pg
from pygame import display
from pygame.constants import WINDOWLEAVE
from pygame.event import post
from .utils import load, get_sprite, smooth_scale, scale

class Chest:
    def __init__(self, x, y, index):
        self.x, self.y, self.sheet = x, y, load('data/items/chest.png')
        self.img = [get_sprite(self.sheet,  74*i, 0, 74, 90) for i in range(4)]
        self.anim_counter = 0 # Animation counter
        self.Rect = self.img[self.anim_counter].get_rect(topleft=(x,y))
        self.delay = pg.time.get_ticks()
        self.opened = False
        self.interact_rect = pg.Rect(0, self.y, 148, 110)
        self.interact_rect.centerx=self.x
        self.animating_started = False
        self.font = pg.font.Font("data/database/pixelfont.ttf", 16)
        self.pu_font = pg.font.Font("data/database/pixelfont.ttf", 16)
        self.popup_txt = ""
        self.pu_render = self.pu_font.render(self.popup_txt, True, (0, 0, 0))
        self.delay_popup = 0      
        self.UI_button = [ scale(get_sprite(load('data/ui/UI_spritesheet.png'), 147 + 41 * i,31,40,14) ,2) for i in range(2)]
        
        self.reward_index = index # Index for the sublists below
        self.rewards = [
            [Weapons.Training_Sword(), 30] # Kitchen Chest
        ] 
        self.btn_a = 0
    
    def start_anim(self, backpack, wallet):
        self.animating_started = True
        self.delay = pg.time.get_ticks()
        
        # Items   
        
        coins = self.rewards[self.reward_index][1]
        weapon = self.rewards[self.reward_index][0]

        wallet += coins
        backpack.append(weapon)
        
        if weapon is None:
            self.popup_txt = f"You got {coins} from the chest"
        else:
            weapon_name = weapon.__class__.__name__
            self.popup_txt += f' You got {coins} from the chest and a {weapon_name.replace("_", " ")}' 
        
        self.pu_render = self.pu_font.render(self.popup_txt, True, (0, 0, 0))
        self.delay_popup = pg.time.get_ticks()

    def end_anim(self):
        self.opened = True
        

    def update(self, screen, scroll, player):
        cur_time = pg.time.get_ticks()  # get current time

        # if the player interact with the chest, start the anim
        if player.Interactable and self.interact_rect.colliderect(player.Rect) and not self.animating_started:
            self.start_anim(player.inventory.items, player.data['coins'])
        
        # animate the opening of the chest
        if not self.opened and self.animating_started:
            if cur_time - self.delay > 100:
                self.delay = cur_time
                if self.anim_counter < len(self.img)-1:
                    self.anim_counter += 1
                else:
                    self.end_anim()
        
        # managing the positions considering the scroll
        self.Rect = self.img[self.anim_counter].get_rect(center=(self.x-scroll[0],self.y-scroll[1]))
        self.interact_rect.centerx, self.interact_rect.y = self.x-scroll[0], self.y-scroll[1]
        screen.blit(self.img[self.anim_counter], self.Rect)

        # show the key to press in order to interact
        if not self.opened and self.interact_rect.colliderect(player.Rect):
            txt = self.font.render(pg.key.name(player.data["controls"][4]), True, (255, 255, 255))
            rct = txt.get_rect(center=(self.x-scroll[0],self.y-scroll[1]-75))
            
            if self.btn_a >= 13: self.btn_a = 0
            self.btn_a += 1
            screen.blit(self.UI_button[self.btn_a // 7], (rct[0] - 7, rct[1])) # The UI behind the text
            screen.blit(txt, rct) # Interact Key Text

        # show the popup saying what item you got from the chest
        if self.animating_started and cur_time - self.delay_popup < 2000: # -> delay of 2 secs before it disapear
            pu_rect = self.pu_render.get_rect(center=(player.Rect.centerx, player.Rect.y-100))
            pg.draw.rect(screen, (255, 255, 255), pu_rect)
            screen.blit(self.pu_render, pu_rect)
                

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

    class Training_Sword: # Reference Model

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