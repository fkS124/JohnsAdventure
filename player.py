import pygame, sys
pygame.font.init()
font = pygame.font.Font("data/fonts/pixelfont.ttf", 16)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.pos = [self.x, self.y]  # Player's position
        self.screen = screen
        self.speed = 4  # Player's speed
        self.paused = False  # if player has paused the game
        self.click = False  # when Player clicks
        # Movement
        self.Right = False
        self.Left = False
        self.Up = False
        self.Down = False
        self.Player = pygame.image.load('player_beta.png').convert()
        self.PlayerRect = self.Player.get_rect()
        self.PlayerRect.center = (self.x, self.y)

    def update(self, scroll):
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
        self.pos = [self.x, self.y]  # Update player's pos
        self.screen.blit(self.InfoText, (self.PlayerRect[0] - 80, self.PlayerRect[1] - 30))
        return self.screen.blit(self.Player, self.PlayerRect)

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click = True
            else:
                self.click = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                if event.key == pygame.K_RIGHT:
                    self.Right = True
                if event.key == pygame.K_LEFT:
                    self.Left = True
                if event.key == pygame.K_DOWN:
                    self.Down = True
                if event.key == pygame.K_UP:
                    self.Up = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.Right = False
                if event.key == pygame.K_LEFT:
                    self.Left = False
                if event.key == pygame.K_DOWN:
                    self.Down = False
                if event.key == pygame.K_UP:
                    self.Up = False
            if event.type == pygame.K_ESCAPE:  # Exit
                pygame.quit(), sys.exit()
