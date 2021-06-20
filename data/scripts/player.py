import pygame, sys
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
            if event.type == pygame.K_ESCAPE:  # Exit
                pygame.quit(), sys.exit()
