import pygame as pg
from pygame import sprite
from .utils import *
from .backend import UI_Spritesheet


class Prop:

    """Motionless thing like tree, chest, fence..."""

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
        self.name = "default"
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
        self.static_image = image_path != ""
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
        self.index_anim = 0

        if self.interaction_type == "unique":
            if not self.has_interacted:
                self.has_interacted = True

                self.interact(player_instance=player_instance)
        else:
            self.interact(player_instance=player_instance)

    def interact(self, player_instance=None):
        
        # WRITE THE INTERACTION HERE -> including sounds, etc
        
        pass

    def animate(self):
        current_anim = self.anim_manager[self.state]
        if current_anim[0] is not None:
            if pg.time.get_ticks() - self.delay > self.delay_bt_frames:
                self.delay = pg.time.get_ticks()
                if current_anim[1] == "loop":
                    self.index_anim = (self.index_anim + 1) % len(current_anim[0])
                else:
                    if self.index_anim + 1 < len(current_anim[0]):
                        self.index_anim += 1
                    else:
                        if self.state == "interaction":
                            if self.interaction_type == "several":
                                self.state = "idle"
                                self.index_anim = 0

            self.current_frame = current_anim[0][self.index_anim]

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

        # ------------- INTERACTION -------------
        self.name = "chest"

        # form :
        # {"coins": int, "items": [Item1, Item2, ...] or Item}
        self.rewards = rewards        
        self.interaction_time = 0

        # ------------ ANIMATION ----------------
        self.UI_button = [scale(get_sprite(load(resource_path('data/ui/UI_spritesheet.png')), 147 + 41 * i,31,40,14) ,2) for i in range(2)]
        self.id_button = 0
        self.delay_button = 0

        self.font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 12)
        self.font2 = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 14)
        self.animation_ended = False
        self.dy = 0
        self.dy_max = 50
        self.delay_dy = 0

        self.coin = l_path("data/sprites/items/coin1.png", alpha=True)
        self.ui = UI_Spritesheet('data/ui/UI_spritesheet.png')
        self.item_bg = scale(self.ui.parse_sprite('reward.png'),3)
        self.new = self.font.render("NEW !", True, (255, 255, 0))

        self.coin_txt = self.font.render(f"{self.rewards['coins']}", True, (255,255,255))   

    def animate_new_items(self, screen, scroll):

        if self.has_interacted:

            if pg.time.get_ticks()-self.delay_dy>25 and self.dy <= self.dy_max:
                self.delay_dy = pg.time.get_ticks()
                self.dy += 1

            # gets a real rect for the player
            r = pg.Rect(*self.player.rect.topleft-scroll-pg.Vector2(50, 40), *self.player.rect.size)
            dep_x = r.centerx - (len(self.rewards)*2-1)*self.item_bg.get_width()//2
            for i, key in enumerate(self.rewards):
                pos = (dep_x+(2*i)*(self.item_bg.get_width()), r.y-self.dy)
                screen.blit(self.item_bg, pos)  # blit a background image
            
                if self.rewards[key].__class__.__name__ not in [item.__class__.__name__ for item in self.player.inventory.items] and key != "coins":  # show up a new item
                    screen.blit(self.new, self.new.get_rect(topleft=(pos+pg.Vector2(0, self.item_bg.get_height()))))

                if key == "coins":  # shows a special display if it's coin ("coin_log"+"n_coins")
                    screen.blit(self.coin_txt, self.coin_txt.get_rect(x=pos[0],centery=pos[1]+self.item_bg.get_height()//2))
                    screen.blit(self.coin, self.coin.get_rect(x=pos[0]+self.coin_txt.get_width(), centery=pos[1]+self.item_bg.get_height()//2))
                else:  # shows tje icon of the item
                    screen.blit(self.rewards[key].icon, self.rewards[key].icon.get_rect(center=pg.Rect(*pos, *self.item_bg.get_size()).center))

            if pg.time.get_ticks() - self.interaction_time > 4000:  # after x seconds, end the animation
                self.animation_ended = True

    def on_interaction(self, player_instance=None):
        self.interaction_time = pg.time.get_ticks()
        return super().on_interaction(player_instance=player_instance)

    def interact(self, player_instance=None):
        self.player = player_instance

    def update_popup_button(self, screen, scroll):
        position = (self.player.rect.topleft - scroll)
        itr_box = pg.Rect(*position, self.player.rect.w//2, self.player.rect.h//2)

        if self.interaction_rect.colliderect(itr_box) and not self.has_interacted:
            if pg.time.get_ticks() - self.delay_button > 500:
                self.id_button = (self.id_button + 1) % len(self.UI_button)
                self.delay_button = pg.time.get_ticks()

            screen.blit(self.UI_button[self.id_button], self.UI_button[self.id_button].get_rect(center=self.rect.center-scroll-pg.Vector2(0, 75)))
            txt = self.font2.render(pg.key.name(self.player.data["controls"]["interact"]), True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=self.UI_button[self.id_button].get_rect(center=self.rect.center-scroll-pg.Vector2(0, 78-((self.id_button)*2))).center))

    def update(self, screen, scroll, player):
        self.player = player
        
        # Draw and move Chest
        super().update(screen, scroll)
        self.update_popup_button(screen, scroll)

        # Debug interact rect
        pg.draw.rect(screen, (0, 255, 255), self.interaction_rect, 1)

        if not self.animation_ended:
            self.animate_new_items(screen, scroll)
        else:  # fill the inventory with the rewards 
            for reward in self.rewards:
                if reward == "coins":
                    self.player.data['coins'] += self.rewards[reward]
                else:
                    if type(self.rewards[reward]) is list:
                        for item in self.rewards[reward]:
                            self.player.inventory.items.append(item)
                    else:
                        self.player.inventory.items.append(self.rewards[reward])   
            self.rewards = {}

                

        
        
            



        