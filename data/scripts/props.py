import pygame as pg
from pygame import sprite
from .utils import *


class Prop:

    def __init__(self,
                 pos: pg.Vector2 | tuple[int, int],
                 image_path:str="",
                 sprite_sheet:str="",
                 idle_coord:tuple=None,
                 interaction:bool=False,
                 interaction_direction:str="",
                 interaction_rect_size:tuple[int,int]=(100,100),
                 interaction_animation_coord:tuple=None,
                 type_of_interaction:str="unique",  # unique or several
                 ):
        
        self.IDENTITY = "PROP"
        if image_path == sprite_sheet == "":
            return ValueError("Prop must at least include an image or a spritesheet")

        # ---------------- SPRITE SHEET LOADING -----------------------
        if sprite_sheet != "":
            self.sprite_sheet = l_path(sprite_sheet)

            if idle_coord is not None:
                self.idle = self.load_from_spritesheet(idle_coord)
            
            if interaction_animation_coord is not None and interaction:
                self.interaction_anim = self.load_from_spritesheet(interaction_animation_coord)

        # -------------------- INTERACTION ---------------------------
        self.interaction = interaction
        
        if self.interaction:
            self.interaction_type = type_of_interaction
            if self.interaction_type == "unique":
                self.has_interacted = False
            self.rect = self.interaction_anim[0].get_rect()
            self.it_re_size = interaction_rect_size
            self.interaction_direction = interaction_direction
            match interaction_direction:
                case "left":
                    self.interaction_rect = pg.Rect(self.rect.x-self.it_re_size[0], self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
                case "right":
                    self.interaction_rect = pg.Rect(self.rect.right, self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
                case "up":
                    self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.y-self.it_re_size[1], *self.it_re_size)
                case "down":
                    self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.bottom, *self.it_re_size)
        
        # ------------------- ANIMATION ------------------------------
        self.anim_manager = {
            "idle": (self.idle if hasattr(self, "idle") else None, "loop"),
            "interaction": (self.interaction_anim if hasattr(self, "interaction_anim") else None, "single"),
        }
        self.state = "idle"
        self.delay = 0
        self.index_anim = 0  
        self.delay_bt_frames = 100

        # ---------------- SPRITES AND RECT --------------------------
        self.static_image = not image_path != ""
        if image_path != "":
            self.current_frame = l_path(image_path)
        else:
            self.current_frame = self.idle[0]
        self.rect = self.current_frame.get_rect(topleft=pos)

    def update_interaction_rect(self, scroll):
        if self.interaction:
            match self.interaction_direction:
                case "left":
                    self.interaction_rect = pg.Rect(self.rect.x-self.it_re_size[0], self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
                case "right":
                    self.interaction_rect = pg.Rect(self.rect.right, self.rect.centery-self.it_re_size[1]//2, *self.it_re_size)
                case "up":
                    self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.y-self.it_re_size[1], *self.it_re_size)
                case "down":
                    self.interaction_rect = pg.Rect(self.rect.centerx-self.it_re_size[0]//2, self.rect.bottom, *self.it_re_size)
            self.interaction_rect.topleft-=scroll

    def on_interaction(self, player_instance=None):
        
        """This function is called when an interaction appear with the player.
        Passing the player as an argument can for instance be helpful to give him 
        objects."""

        self.state = "interaction"  # start animation

        if self.interaction_type == "unique":
            if not self.has_interacted:
                self.has_interacted = True

                self.interaction(player_instance=player_instance)

        else:

            self.interaction(player_instance=player_instance)

    def interaction(self, player_instance=None):
        
        # WRITE THE INTERACTION HERE -> including sounds, etc
        
        pass

    def animate(self):
        current_anim = self.anim_manager[self.state]
        if current_anim[0] is not None:
            if pg.time.get_ticks() - self.delay > self.delay_bt_frames:
                self.delay = pg.time.get_ticks()
                if current_anim[1] == "loop":
                    self.index_anim = (self.index_anim + 1) % len(current_anim)
                else:
                    if self.index_anim + 1 < len(current_anim):
                        self.index_anim += 1
                    else:
                        if self.state == "interaction":
                            if self.interaction_type == "several":
                                self.state = "idle"
                                self.index_anim = 0

            self.current_frame = current_anim[self.index_anim]

    def update(self, screen, scroll):
        if not self.static_image:
            self.animate()
        self.update_interaction_rect(scroll)
        screen.blit(self.current_frame, (self.rect.topleft-scroll))

    def load_from_spritesheet(self, coords):
        if coords == [0, 0, 0, 0, 0, 0] or coords is None:
            return None
        if coords[-1] == "flip":
            return [flip_vertical(scale(get_sprite(self.sprite_sheet, coords[0]+coords[2]*i, coords[1], coords[2], coords[3]), coords[4])) for i in range(coords[5])]
        return [scale(get_sprite(self.sprite_sheet, coords[0]+coords[2]*i, coords[1], coords[2], coords[3]), coords[4]) for i in range(coords[5])]


class Chest(Prop):

    def __init__(self, pos, rewards):
        super().__init__(
            pos,
            sprite_sheet='data/sprites/items/chest.png',
            interaction=True,
            idle_coord=[0, 0, 74, 90, 1, 1],
            interaction_animation_coord=[0, 0, 74, 90, 1, 4],
            interaction_direction="down",
            interaction_rect_size=(100, 50),
            type_of_interaction="unique"
        )

        self.rewards = rewards
        # form :
        # {"coins": int, "items": [Item1, Item2, ...] or Item}

    def interaction(self, player_instance=None):

        # START ANIMATION INFORMING ON WHAT YOU GOT FROM THE CHEST

        for reward in self.rewards:
            if reward == "coins":
                player_instance.data['coins'] += self.rewards[reward]
            elif reward == "items":
                if type(self.rewards[reward]) is list:
                    for item in self.rewards[reward]:
                        player_instance.inventory.items.append(item)
                else:
                    player_instance.inventory.items.append(self.rewards[reward])
        
    def update(self, screen, scroll):
        pg.draw.rect(screen, (0, 255, 255), self.interaction_rect, 1)
        return super().update(screen, scroll)