

'''
Credits @Marios325346

This class is for takes a sprite from the sheet based on its coordinates from the json file

'''

import json, pygame

from .utils import resource_path

class UI_Spritesheet:
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(resource_path(filename)).convert()
        with open(resource_path('data/database/ui.json')) as f:
            self.data = json.load(f)

    def get_sprite(self, x, y, w, h):  # Data from the json file
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((255, 255, 255))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        return self.get_sprite(sprite["x"], sprite["y"], sprite["w"], sprite["h"])