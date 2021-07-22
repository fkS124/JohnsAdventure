import pygame as pg
import data.scripts.items as items
from .utils import *
from random import choice


class Inventory:

    def __init__(self, screen, sprite_sheet):

        # unpack variables
        self.spr_sh = sprite_sheet
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        # invetory button
        self.button_inv = scale(self.spr_sh.parse_sprite("inventory"), 5)
        self.bi_rect = self.button_inv.get_rect(right=self.w-10, y=100)

        # the menu where all the items in the inventory will be displayed
        # only if the player is currently in this state
        self.inv_menu = pg.Surface((self.w // 3, self.h // 3), pg.SRCALPHA)
        self.im_rect = self.inv_menu.get_rect(right=self.bi_rect.x-10, y=self.bi_rect.y)  # center

        # ui piece for the inventory
        self.ui_inv = scale(self.spr_sh.parse_sprite("catalog_button.png"), 5)
        self.uii_rect = self.ui_inv.get_rect(right=self.inv_menu.get_width(), y=0)

        # inventory is shown if it's True
        self.show_menu = False

        # list all items :
        self.items = [choice([items.Items.NullItem(), items.Weapons.BasicSword()]) for i in range(15)]

        # useful to track the scrolling
        self.index_scroll = 0

        self.items.append(items.Weapons.BasicSword())

    def scroll_down(self):
        self.index_scroll += 1 * (self.index_scroll < len(self.items)-1)

    def scroll_up(self):
        self.index_scroll -= 1 * (self.index_scroll > 0)

    def update(self):

        # blit the inventory button
        self.screen.blit(self.button_inv, self.bi_rect)

        # if it shows the menu, then it does not show the down bar
        if self.show_menu:
            
            # blit the inventory ui
            self.inv_menu.blit(self.ui_inv, self.uii_rect)

            # loop through the items
            for index in range(len(self.items)):
                # avoid errors where the scroll applied is too far away 
                if index + self.index_scroll > len(self.items)-1:
                    break

                # getting the item, the first item is 0 + scroll
                item = self.items[index+self.index_scroll]

                # track if the item is blitted outside of the ui, if so it breaks the loop
                if index*item.image.get_height()+16 > self.uii_rect.height - 15:
                    break

                # display the item on the screen
                item.update(self.inv_menu, (self.uii_rect.x+25, index*item.image.get_height()+12))

            # showing a scroll bar
            h = self.uii_rect.height / len(self.items)
            step = (h / len(self.items)) * self.index_scroll * 13
            pg.draw.rect(self.inv_menu, (255, 0, 0), [self.uii_rect.right-10, step+10, 5, h*2])

            # show menu
            self.screen.blit(self.inv_menu, self.im_rect)

    def handle_clicks(self, pos):
        # check if the inventory button is clicked if the inventory is not active
        if not self.show_menu:
            if self.bi_rect.collidepoint(pos):
                self.set_active()
        else:
            # if a click happens outside of the inventory, it desactivate it
            if not self.im_rect.collidepoint(pos):
                self.set_active()

        # get the pos of the click on the surface
        pos -= pg.Vector2(*self.im_rect.topleft)
        # handle the clicks for all items
        for item in self.items:
            item.handle_clicks(pos)

    def set_active(self):
        # switch state of the invetory
        self.show_menu = not self.show_menu