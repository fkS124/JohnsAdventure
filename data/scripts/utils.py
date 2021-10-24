'''
 Credits @Marios325346

 Functions to reduce typing :rofl:

'''
import pygame, sys, os, pathlib

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, str(pathlib.Path(relative_path)))

def l_path(relative_path, alpha = None):
    ''' Upgraded load function for PyInstaller '''
    if alpha:
        return pygame.image.load(resource_path(relative_path)).convert_alpha()
    return pygame.image.load(resource_path(relative_path)).convert()

@lru_cache(1000)
def load(path, alpha = None):
    if alpha:
        return pygame.image.load(path).convert_alpha()
    return pygame.image.load(path).convert()

@lru_cache(1000)
def scale(img, n):
    return pygame.transform.scale(img, (img.get_width() * n, img.get_height() * n))

@lru_cache(1000)
def smooth_scale(img, n: float):
    return pygame.transform.smoothscale(img, (img.get_width() * n, img.get_height() * n))

@lru_cache(1000)
def double_size(img):
    return pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))

@lru_cache(1000)
def flip_vertical(img):
    return pygame.transform.flip(img, True, False)

def get_sprite(spritesheet, x, y, w, h): # Gets NPC from spritesheet
        sprite = pygame.Surface((w, h)).convert()
        sprite.set_colorkey((255, 255, 255))
        sprite.blit(spritesheet, (0, 0), (x, y, w, h))
        return sprite
