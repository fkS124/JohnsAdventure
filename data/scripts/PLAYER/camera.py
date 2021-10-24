# Load Pygame
import pygame

# Abstract method
from abc import ABC, abstractmethod

vec = pygame.math.Vector2 # To simplify things :')

'''
##################################

         Games's Camera

##################################
'''

class Camera:
    def __init__(self, player, screen: pygame.surface):
        '''
            The Player is given a upgraded camera system,
            to make the gameplay look better
        '''
        self.player = player

        # The gap between the player and camera
        self.offset = vec(0,0)

        # We use float to get the precice location
        self.offset_float = vec(0,0)

        # Sceen Surface
        self.screen = screen.get_size()

        # Keep track of the Player
        self.CONST = vec(

        #Camera X Position
        -screen.get_width()/2,

        #Camera Y Position (ndecided)
        -screen.get_height()/2

        ) # end of CONST

    def set_method(self, method):
        '''
        The gear to switch between Camera types
        1.   Auto: Camera moves on its own
        2. Follow: Camera follows X object
        3. Border: Camera is locked player cant go outside of it
        '''
        self.method = method

    def scroll(self):
        self.method.scroll()

'''
##################################

    Camera Function Methods

All below share the same principle with different tweaks
##################################
'''

class CamScroll(ABC):
      '''
         Camera Movement
      '''
      def __init__(self, camera, player):
          self.camera = camera
          self.player = player

      @abstractmethod
      def scroll(self):
          '''
          if this is empty abstractmethod
          will tell us something went wrong
          '''
          pass


class Follow(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self):
        '''
        Formula to follow the player

        It takes the difference player did to the screen
        and adds it to camera's offset updating camera's
        position.

        '''

        # X Axis
        self.camera.offset_float.x += (
        self.player.rect.x - self.camera.offset_float.x
        +
        self.camera.CONST.x
        )

        # Y Axis
        self.camera.offset_float.y += (
        self.player.rect.y - self.camera.offset_float.y
        +
        self.camera.CONST.y
        )

        # Turn the numbers back to pixels
        self.camera.offset.x = int(self.camera.offset_float.x)
        self.camera.offset.y = int(self.camera.offset_float.y)


class Border(CamScroll):
    '''

    Once player has reached a specific point,
    the camera will stop moving.

    '''
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self):
        '''
        Formula to follow the player

        It takes the difference player did to the screen
        and adds it to camera's offset updating camera's
        position.
        '''

    def scroll(self):
        self.camera.offset_float.x += (self.player.rect.x - self.camera.offset_float.x + self.camera.CONST.x)
        self.camera.offset_float.y += (self.player.rect.y - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)

        # Lock X side
        self.camera.offset.x = max(self.camera.screen[0], self.camera.offset.x)
        self.camera.offset.x = min(self.camera.offset.x, 0)

        # Lock Y side
        self.camera.offset.y = max(self.camera.screen[1], self.camera.offset.y)
        self.camera.offset.y = min(self.camera.offset.y, 0)

class Auto(CamScroll):
    '''
    Screen moves independently
    '''
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self):
        '''
        Moving the camera
        (coords will be tweaked later)
        '''
        self.camera.offset.x += 1
