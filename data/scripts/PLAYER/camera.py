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

        # Screen Surface
        self.display = screen
        
        # Screen Size
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
      def __init__(self, camera, player, status):
          self.camera = camera
          self.player = player
          self.status = status

      @abstractmethod
      def scroll(self):
          '''
          if this is empty abstractmethod
          will tell us something went wrong
          '''
          pass


class Follow(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player, status="Follow")

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
        CamScroll.__init__(self, camera, player, status="Border")


    def scroll(self):
        '''
        Formula to follow the player

        It takes the difference player did to the screen
        and adds it to camera's offset updating camera's
        position.
        '''

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
        CamScroll.__init__(self, camera, player, status="Auto")
        self.screen = camera.display
        self.camera_speed = 10 # Camera speeds that we multiply with dt

        sur = pygame.Surface((camera.screen[0], 92)) 
        sur.fill((0,0,0))
        self.cinema_bar = sur

        # Bar Y position before the camera
        self.bar_y = -self.cinema_bar.get_height()
        
        self.bar_speed = 64

    def scroll(self):
        '''
        Moving the camera

        We have to somehow find a way to put x, y cords and dt and then use them to move the camera 
        ''' 
        dt = pygame.time.Clock().tick(35)/1000

        if self.bar_y < 0:
           self.bar_y += self.bar_speed * dt 

        # Top Cinema Bar
        self.screen.blit(self.cinema_bar, (0, self.bar_y))


        # Bottom Cinema Bar
        b_pos = self.screen.get_height() - (self.cinema_bar.get_height() - abs(self.bar_y))
        self.screen.blit(self.cinema_bar, (0, b_pos))