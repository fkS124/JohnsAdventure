# Load Pygame
import pygame
import random, math

from ..utils import resource_path

# Abstract method
from abc import ABC, abstractmethod

vec = pygame.math.Vector2  # To simplify things :')

'''
##################################

         Games' Camera

##################################
'''


class Camera:
    def __init__(self, player, screen: pygame.surface):
        """
            The Player is given a upgraded camera system,
            to make the gameplay look better
        """

        self.player = player
        self.method = None

        # The gap between the player and camera
        self.offset = vec(0, 0)

        # Field of view
        self.fov = vec(0, 0)
        self.changing = False  # Event when fov changing occurs

        # We use float to get the precice location
        self.offset_float = vec(0, 0)

        # Screen Surface
        self.display = screen

        # Screen Size
        self.screen = screen.get_size()

        # Keep track of the Player
        self.CONST = vec(

            # Camera X Position
            -screen.get_width() / 2,

            # Camera Y Position (ndecided)
            -screen.get_height() / 2

        )  # end of CONST

    def set_method(self, method):
        """
        The gear to switch between Camera types
        1.   Auto: Camera moves on its own
        2. Follow: Camera follows X object
        3. Border: Camera is locked player cant go outside of it
        """
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
    """
         Camera Movement
    """

    def __init__(self, camera, player, status):
        self.camera = camera
        self.player = player
        self.status = status

        self.fov = 1
        self.capture_rect = pygame.Rect(0, 0, 1280, 720)

    @abstractmethod
    def scroll(self):
        """
          if this is empty abstractmethod
          will tell us something went wrong
          """
        pass

    def draw(self):
        if self.fov != 1:  # if fov == 1 (normal res), we don't apply this mechanic to save performances

            # get the current screen
            surface = self.camera.display.subsurface(self.capture_rect)

            # scale it according to fov -> size * fov = new_size => fov ∈ [1, 2] where 2 is 100% zoom.
            scaled = pygame.transform.smoothscale(
                surface,
                (surface.get_width()*self.fov, surface.get_height()*self.fov)
            )

            dw = surface.get_width()*self.fov - surface.get_width()
            dh = surface.get_height()*self.fov - surface.get_height()

            # blit it
            self.camera.display.blit(
                scaled, (-dw / 2, -dh / 2)
            )


class Follow(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player, status="Follow")

    def scroll(self):
        """
        Formula to follow the player

        It takes the difference player did to the screen
        and adds it to camera's offset updating camera's
        position.

        """

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
    """

    Once player has reached a specific point,
    the camera will stop moving.

    """

    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player, status="Border")

    def scroll(self):
        """
        Formula to follow the player

        It takes the difference player did to the screen
        and adds it to camera's offset updating camera's
        position.
        """

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
    """
    Screen moves independently
    """

    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player, status="Auto")
        self.screen = camera.display

        self.W, self.H = self.screen.get_size()
        sur = pygame.Surface((camera.screen[0], 92))
        sur.fill((0, 0, 0))
        self.cinema_bar = sur

        # Bar Y position before the camera
        self.bar_y = -self.cinema_bar.get_height()

        self.bar_speed = 64

        self.dx, self.dy = (0, 0)
        self.target = (0, 0)
        self.looking_at = (0, 0)
        self.delay_mvt = 0
        self.moving_cam = False

        self.font = pygame.font.Font(resource_path("data/database/pixelfont.ttf"), 20)
        self.text = ""

        self.start = 0
        self.duration = 0

        self.fov = 1
        self.capture_rect = pygame.Rect(
            0,
            self.bar_y+self.cinema_bar.get_height(),
            self.screen.get_width(),
            self.screen.get_height() - 2 * abs(self.bar_y + self.cinema_bar.get_height())
        )

        self.zooming_out = False
        self.target_zoom_out = 1
        self.duration_zoom_out = 0
        self.start_time_zoom_out = 0
        self.d_fov = 0
        self.delay_zmo = 0

    def look_at(self, pos):
        self.camera.offset.xy = [pos[0] - self.screen.get_width() // 2, pos[1] - self.screen.get_height() // 2]

    def set_text(self, txt: str):
        self.text = txt

    def go_to(self, pos, duration=1000):

        self.start = pygame.time.get_ticks()
        self.duration = duration

        if not duration:
            self.looking_at = pos
            return self.look_at(self.looking_at)

        angle = math.atan2(
            pos[1] - self.looking_at[1],
            pos[0] - self.looking_at[0]
        )

        distx, disty = abs(pos[0] - self.looking_at[0]), abs(pos[1] - self.looking_at[1])
        self.dx = math.cos(angle) * abs(distx / (duration / 20 * math.cos(angle)))
        self.dy = math.sin(angle) * abs(disty / (duration / 20 * math.sin(angle)))
        self.delay_mvt = pygame.time.get_ticks()
        self.target = pos

        self.moving_cam = True

    def draw(self):
        super(Auto, self).draw()

        # Bottom Cinema Bar
        b_pos = self.screen.get_height() - (self.cinema_bar.get_height() - abs(self.bar_y))
        self.screen.blit(self.cinema_bar, (0, b_pos))
        self.screen.blit(self.cinema_bar, (0, self.bar_y))
        render = self.font.render(self.text, True, (255, 255, 255))
        if self.bar_y > 0:
            self.screen.blit(render, render.get_rect(center=(self.W // 2, self.H - self.cinema_bar.get_height() // 2)))
        """ Debug:
        pygame.draw.line(self.screen, (255, 255, 255), (0, 0), (self.W, self.H))
        pygame.draw.line(self.screen, (255, 255, 255), (self.W, 0), (0, self.H))
        pygame.draw.circle(self.screen, (255, 255, 0), self.target-self.camera.offset.xy, 6)
        """

    def start_zoom_out(self, value, duration):
        self.duration_zoom_out = duration
        self.target_zoom_out = value
        self.zooming_out = True
        self.start_time_zoom_out = pygame.time.get_ticks()
        self.d_fov = 20 * (self.target_zoom_out - self.fov) / duration
        self.delay_zmo = self.start_time_zoom_out

    def scroll(self):
        """
        Moving the camera

        We have to somehow find a way to put x, y cords and dt and then use them to move the camera
        """
        dt = pygame.time.Clock().tick(35) / 1000

        if self.bar_y < 0:
            self.bar_y += self.bar_speed * dt

            # Top Cinema Bar
        self.screen.blit(self.cinema_bar, (0, self.bar_y))

        self.look_at(self.looking_at)

        if self.moving_cam:

            dx, dy = self.target[0] - self.looking_at[0], self.target[1] - self.looking_at[1]
            if pygame.time.get_ticks() - self.delay_mvt > 20:
                self.delay_mvt = pygame.time.get_ticks()
                if abs(dx) < abs(self.dx) or abs(dy) < abs(self.dy):
                    self.looking_at += vec(dx, dy)

                else:
                    self.looking_at += vec(self.dx, self.dy)

            if -3 < dx < 3 and -3 < dy < 3:
                self.moving_cam = False
                self.looking_at = self.target

            # print(dx, dy, self.dx, self.dy, self.looking_at, self.target)

        if self.zooming_out:

            if abs(self.fov-self.target_zoom_out) < 0.01:
                self.zooming_out = False
                self.fov = self.target_zoom_out

            if pygame.time.get_ticks() - self.delay_zmo > 20:
                self.delay_zmo = pygame.time.get_ticks()
                self.fov += self.d_fov
