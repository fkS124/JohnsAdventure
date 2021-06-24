import pygame, sys, random, math
pygame.font.init()
font = pygame.font.Font("data/database/pixelfont.ttf", 16)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        self.x, self.y = x, y
        self.pos = [self.x, self.y]  # Player's position (debugging)
        self.screen = screen
        self.speed = 6  # Player's speed
        self.paused = False  # if player has paused the game
        self.click = False  # when Player clicks
        self.Interactable = False  # Player's interaction with the environment
        self.InteractPoint = 0
        # Movement
        self.Right = False
        self.Left = False
        self.Up = False
        self.Down = False
        self.Player = pygame.image.load('player_beta.png').convert()
        self.PlayerRect = self.Player.get_rect(center=(self.x, self.y))

    def update(self):
        self.controls()
        self.InfoText = font.render(f'Position:{self.pos}', True, (255, 255, 255))
        # Movement
        if self.Up:
            self.y -= self.speed
        elif self.Down:
            self.y += self.speed
        if self.Left:
            self.x -= self.speed
        elif self.Right:
            self.x += self.speed
        self.pos = [self.x, self.y]  # DEBUGGING FOR WORLD POSITION
        self.screen.blit(self.InfoText, (self.PlayerRect[0] - 80, self.PlayerRect[1] - 30))
        return self.screen.blit(self.Player, self.PlayerRect)

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click = True
            else:
                self.click = False
            if event.type == pygame.KEYDOWN:
                self.Interactable = False # If player clicks any button the interaction will stop
                if event.key == pygame.K_SPACE:
                    #print(self.InteractPoint)
                    self.Interactable = True
                    if self.InteractPoint != 2:
                        self.InteractPoint += 1
                    else:
                        self.InteractPoint = 0
                if event.key == pygame.K_ESCAPE: # Toggle Pause screen
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                if event.key == pygame.K_d:
                    self.Right = True
                if event.key == pygame.K_a:
                    self.Left = True
                if event.key == pygame.K_s:
                    self.Down = True
                if event.key == pygame.K_w:
                    self.Up = True
                if event.key == pygame.K_F12:
                    pygame.display.toggle_fullscreen() # Toggle fullscreen
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.Right = False
                if event.key == pygame.K_a:
                    self.Left = False
                if event.key == pygame.K_s:
                    self.Down = False
                if event.key == pygame.K_w:
                    self.Up = False


class Mau(object): # LOOK AT HIM GOOOOO
    def __init__(self, x , y):
        self.x, self.y = x, y
        self.image = [pygame.image.load('data/sprites/mau/mau1.png').convert_alpha(), pygame.image.load('data/sprites/mau/mau2.png').convert_alpha(), pygame.image.load('data/sprites/mau/mau1.png').convert_alpha()]
        self.ScaledImg = [pygame.transform.scale(image, (image.get_width() * 2, image.get_height()* 2 )) for image in self.image]
        self.Rect = self.ScaledImg[0].get_rect()
        self.Left = self.Right = self.Up = self.down = False   
        self.animation_counter = 0
        # Τριγονομετρία :'(
        self.dx = self.dy = self.distance = 0
        # New pos
        self.mx = self.my = 0
        self.cooldown = 0
        self.switchConter = 0
    

    ''' Reference
    cos = -1  Left (dx)
    sin = -1 (dy) Up
    syn = 1 (dy) down
    cos = 1 (dx) Right 
    _
    '''
    def move(self, scroll):
        # Update rect
        self.Rect = self.ScaledImg[0].get_rect(topleft=(self.x - scroll[0], self.y - scroll[1]))

        # Calculations
        if self.cooldown > 100:
            self.mx, self.my = random.randint(int(self.x) - 50, int(self.x) + 50), random.randint(int(self.y) - 50, int(self.y + 50))
            radians = math.atan2(self.my - self.x, self.my - self.y)
            self.distance = int(math.hypot(self.mx - self.x, self.my - self.y))
            self.dx = math.cos(radians)
            self.dy = math.sin(radians)
            self.cooldown = 0
        else:
            self.switchConter = 0
            self.cooldown += 1
            self.mx = self.my = 0   
        # Moving Mau
        if self.distance:
            self.distance -= 1
            self.x += self.dx * 1.25
            self.y += self.dy * 1.25

        self.active()

    def active(self):
        self.animation_counter += 1
        if self.mx != 0:
            if self.dx < 0:
                while self.switchConter < 1:
                    print('Mau is moving left')
                    self.ScaledImg = [pygame.transform.flip(image, True, False) for image in self.ScaledImg]
                    self.switchConter = 1
            if self.dx > 0:
                while self.switchConter < 1:
                    print('Mau is moving Right')  
                    self.ScaledImg = [pygame.transform.flip(image, False, False) for image in self.ScaledImg]
                    self.switchConter = 1  
    def update(self, screen, scroll):
        if self.animation_counter >= 52: self.animation_counter = 0 # Reset Animation
        self.move(scroll)
        # pygame.draw.rect(DISPLAY, (124,252,0), self.Characters[1].Rect, 1)# Mau hitbox
        screen.blit(self.ScaledImg[self.animation_counter // 18], self.Rect)
