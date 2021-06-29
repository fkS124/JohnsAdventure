'''
 Functions to reduce typing :rofl:

'''
import pygame

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

@lru_cache(1000)
def load(path, alpha = None):
    if alpha:
        return pygame.image.load(path).convert_alpha()
    return pygame.image.load(path).convert()
   
@lru_cache(1000)
def double_size(img):
    return pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))

@lru_cache(1000)
def flip_vertical(img):
    return pygame.transform.flip(img, True, False)


@lru_cache(1000)
def smooth_scale(surface, n: int):
    return pygame.transform.smoothscale(surface, (surface.get_width() * n, surface.get_height() * n))