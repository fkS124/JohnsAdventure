import pygame as pg
from .utils import *
from .backend import UI_Spritesheet
from .particle_system import PARTICLE_EFFECTS
import json
from .POSTPROCESSING.lights_manager import LightTypes


DATA_PATH = resource_path("data/database/open_world.json")
with open(DATA_PATH) as datas:
    DATAS = json.load(datas)
COORDS = {name: [DATAS[name]["x"], DATAS[name]["y"], DATAS[name]["w"],
                 DATAS[name]["h"], DATAS[name]["sc"], DATAS[name]["it"]] for name in DATAS}


class PropGetter:

    def __init__(self, player):
        self.player = player
        self.COORDS = {name: self.get_coords(name) for name in DATAS}
        self.PROP_OBJECTS = {
            name: self.make_prop_object_creator(name) for name in DATAS
        }

    def get_coords(self, name):
        if name not in DATAS:
            return False

        coords = DATAS[name]
        # [x, y, width, height, scale, iterations]
        return [coords["x"], coords["y"], coords["w"], coords["h"], coords["sc"], coords["it"]]

    def get_scale(self, name):
        return DATAS[name]["sc"] if name in DATAS else False

    def make_prop_object_creator(self, name):
        datas = DATAS[name]
        custom_rect = datas["crect"] if "crect" in datas else [0, 0, 0, 0]
        for i in range(len(custom_rect)):
            custom_rect[i] *= self.get_scale(name)

        custom_center = datas["ccty"] * self.get_scale(name) if "ccty" in DATAS[name] else None
        collide = datas["col"] if "col" in datas else True
        sort = datas["sort"] if "sort" in datas else True
        reverse = datas["reverse"] if "reverse" in datas else False
        particle = None
        light_sources = []
        light_types = LightTypes()
        if "add_args" in datas:
            if "particle" in datas["add_args"]:
                p_data = datas["add_args"]["particle"]
                args = [p_data[arg] for arg in p_data]
                if args[-1] == "player":
                    final_args = args[1:-1]
                    final_args.append(self.player)
                else:
                    final_args = args[1:]
                particle = PARTICLE_EFFECTS[args[0]](*(final_args))

            for l_type in light_types.light_types:
                if l_type in datas["add_args"]:
                    light_sources.extend(
                        [
                            {"type": l_type, "info": info, "scale": self.get_scale(name)}
                            for info in datas["add_args"][l_type]
                        ]
                    )

        return lambda pos: SimplePropObject(name,
                                            pos,
                                            custom_rect,
                                            custom_center,
                                            collide=collide,
                                            sort=sort,
                                            particle=particle,
                                            light_sources=light_sources,
                                            reverse=reverse)


class Prop:
    """Motionless thing like tree, chest, fences..."""

    def __init__(self,
                 pos: pg.Vector2,
                 image_path: str = "",
                 sprite_sheet: str = "",
                 idle_coord: tuple = None,
                 interaction: bool = False,
                 interaction_direction: str = "",
                 interaction_rect_size: tuple[int, int] = (100, 100),
                 interaction_animation_coord: tuple = None,
                 type_of_interaction: str = "unique",  # unique or several
                 collision: bool = True,
                 custom_collide_rect: list = None,
                 custom_center=None,
                 status: str = "static"
                 ):

        # either "static" or "breakable"
        self.status = status

        # Take spritesheet location data (Will be used soon)
        with open(resource_path('data/database/open_world.json')) as f:
            self.data = json.load(f)

        self.IDENTITY = "PROP"
        self.collidable = collision
        if custom_collide_rect is not None:
            self.d_collision = custom_collide_rect
        if custom_center is not None:
            self.custom_center = custom_center
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
                    self.interaction_rect = pg.Rect(self.rect.x - self.it_re_size[0],
                                                    self.rect.centery - self.it_re_size[1] // 2, *self.it_re_size)
                case "right":
                    self.interaction_rect = pg.Rect(self.rect.right, self.rect.centery - self.it_re_size[1] // 2,
                                                    *self.it_re_size)
                case "up":
                    self.interaction_rect = pg.Rect(self.rect.centerx - self.it_re_size[0] // 2,
                                                    self.rect.y - self.it_re_size[1], *self.it_re_size)
                case "down":
                    self.interaction_rect = pg.Rect(self.rect.centerx - self.it_re_size[0] // 2, self.rect.bottom,
                                                    *self.it_re_size)

        # ------------------- ANIMATION ------------------------------
        self.anim_manager = {
            "idle": [self.idle if hasattr(self, "idle") else None, "loop"],
            "interaction": [self.interaction_anim if hasattr(self, "interaction_anim") else None, "single"],
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
                    self.interaction_rect = pg.Rect(self.rect.x - self.it_re_size[0],
                                                    self.rect.centery - self.it_re_size[1] // 2, *self.it_re_size)
                case "right":
                    self.interaction_rect = pg.Rect(self.rect.right, self.rect.centery - self.it_re_size[1] // 2,
                                                    *self.it_re_size)
                case "up":
                    self.interaction_rect = pg.Rect(self.rect.centerx - self.it_re_size[0] // 2,
                                                    self.rect.y - self.it_re_size[1], *self.it_re_size)
                case "down":
                    self.interaction_rect = pg.Rect(self.rect.centerx - self.it_re_size[0] // 2, self.rect.bottom,
                                                    *self.it_re_size)
            self.interaction_rect.topleft -= scroll

    def on_interaction(self, player_instance=None):

        """This function is called when an interaction appear with the player.
        Passing the player as an argument can for instance be helpful to give him 
        objects."""

        if self.interaction_type == "unique":
            if not self.has_interacted:
                self.state = "interaction"  # start animation
                self.index_anim = 0

                self.has_interacted = True

                self.interact(player_instance=player_instance)
        else:
            self.state = "interaction"  # start animation
            self.index_anim = 0

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
        screen.blit(self.current_frame, (self.rect.topleft - scroll))

    def load_from_spritesheet(self, coords):
        if coords == [0, 0, 0, 0, 0, 0] or coords is None:
            return None
        if coords[-1] == "flip":
            return [flip_vertical(
                scale(get_sprite(self.sprite_sheet, coords[0] + coords[2] * i, coords[1], coords[2], coords[3]),
                      coords[4])) for i in range(coords[5])]
        return [
            scale(get_sprite(self.sprite_sheet, coords[0] + coords[2] * i, coords[1], coords[2], coords[3]), coords[4])
            for i in range(coords[5])]


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
        self.rewarded = False

        # ------------ ANIMATION ----------------
        self.UI_button = [
            scale(get_sprite(load(resource_path('data/ui/UI_spritesheet.png')), 147 + 41 * i, 31, 40, 14), 2) for i in
            range(2)]
        self.id_button = 0
        self.delay_button = 0

        self.font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 12)
        self.font2 = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 14)
        self.animation_ended = False
        self.dy = 0
        self.dy_max = 30
        self.delay_dy = 0

        self.coin = l_path("data/sprites/items/coin1.png", alpha=True)
        self.ui = UI_Spritesheet('data/ui/UI_spritesheet.png')
        self.item_bg = scale(self.ui.parse_sprite('reward.png'), 3)
        self.new = self.font.render("NEW !", True, (255, 255, 0))

        self.coin_txt = self.font.render(f"{self.rewards['coins']}", True, (255, 255, 255))

    def animate_new_items(self, screen, scroll):

        if self.has_interacted:

            if pg.time.get_ticks() - self.delay_dy > 20 and self.dy <= self.dy_max:
                self.delay_dy = pg.time.get_ticks()
                self.dy += 1

            # gets a real rect for the player
            r = pg.Rect(*self.player.rect.topleft - scroll - pg.Vector2(48, 70), *self.player.rect.size)
            dep_x = r.centerx - (len(self.rewards) * 2 - 1) * self.item_bg.get_width() // 2
            for i, key in enumerate(self.rewards):
                pos = (dep_x + (2 * i) * (self.item_bg.get_width()), r.y - self.dy)
                screen.blit(self.item_bg, pos)  # blit a background image

                if self.rewards[key].__class__.__name__ not in [item.__class__.__name__ for item in
                                                                self.player.inventory.items] and key != "coins":  # show up a new item
                    screen.blit(self.new, self.new.get_rect(topleft=(pos + pg.Vector2(0, self.item_bg.get_height()))))

                if key == "coins":  # shows a special display if it's coin ("coin_log"+"n_coins")
                    # Coin Image
                    screen.blit(self.coin, self.coin.get_rect(x=pos[0] + self.coin_txt.get_width() // 2,
                                                              centery=pos[1] + self.item_bg.get_height() // 3))

                    # Coin Text
                    screen.blit(self.coin_txt,
                                self.coin_txt.get_rect(x=pos[0] + self.coin_txt.get_width() // 2, centery=pos[1] + 33))
                else:  # shows tje icon of the item
                    screen.blit(self.rewards[key].icon,
                                self.rewards[key].icon.get_rect(center=pg.Rect(*pos, *self.item_bg.get_size()).center))

            if pg.time.get_ticks() - self.interaction_time > 4000:  # after x seconds, end the animation
                self.animation_ended = True
                # Empty out Chest
                self.rewards = {}

    def on_interaction(self, player_instance=None):
        return super().on_interaction(player_instance=player_instance)

    def interact(self, player_instance=None):
        self.interaction_time = pg.time.get_ticks()
        self.player = player_instance

    def update_popup_button(self, screen, scroll):
        position = (self.player.rect.topleft - scroll)
        itr_box = pg.Rect(*position, self.player.rect.w // 2, self.player.rect.h // 2)

        if self.interaction_rect.colliderect(itr_box) and not self.has_interacted:
            if pg.time.get_ticks() - self.delay_button > 500:
                self.id_button = (self.id_button + 1) % len(self.UI_button)
                self.delay_button = pg.time.get_ticks()

            screen.blit(self.UI_button[self.id_button],
                        self.UI_button[self.id_button].get_rect(center=self.rect.center - scroll - pg.Vector2(0, 75)))
            txt = self.font2.render(pg.key.name(self.player.data["controls"]["interact"]), True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=self.UI_button[self.id_button].get_rect(
                center=self.rect.center - scroll - pg.Vector2(0, 78 - ((self.id_button) * 2))).center))

    def update(self, screen, scroll, player):
        self.player = player

        # Draw and move Chest
        super().update(screen, scroll)
        self.update_popup_button(screen, scroll)

        # Debug interact rect
        # pg.draw.rect(screen, (0, 255, 255), self.interaction_rect, 1)

        if not self.animation_ended and self.has_interacted:
            self.animate_new_items(screen, scroll)
            if not self.rewarded:
                self.rewarded = True
                for reward in self.rewards:
                    # Browse though the chest and add items
                    if reward == "coins":
                        self.player.data['coins'] += self.rewards[reward]
                    else:
                        if type(self.rewards[reward]) is list:
                            for item in self.rewards[reward]:
                                self.player.inventory.items.append(item)
                        else:
                            self.player.inventory.items.append(self.rewards[reward])


class SimplePropObject(Prop):

    def __init__(self,
                 name,
                 pos,
                 custom_rect,
                 custom_center,
                 collide=True,
                 sort=True,
                 particle=None,
                 light_sources=[],
                 reverse=False):

        super().__init__(
            pos=pos, sprite_sheet='data/sprites/world/world_sheet.png',
            idle_coord=COORDS[name],
            custom_collide_rect=(custom_rect if custom_rect != [0, 0, 0, 0] else None),
            custom_center=custom_center,
            collision=collide
        )
        self.sort = sort
        self.particle_effect = particle
        if particle is not None:
            self.particle_effect.pos[0] = self.particle_effect.pos[0] * 3 + self.rect.x
            self.particle_effect.pos[1] = self.particle_effect.pos[1] * 3 + self.rect.y
        self.light_sources = [
            LightTypes().get_light_object(light["type"], light["info"], light["scale"])
            for light in light_sources
        ]
        for l_source in self.light_sources:
            l_source.pos += pg.Vector2(self.rect.topleft)

        if reverse:
            for anim in self.anim_manager:
                new_anim = []
                if type(self.anim_manager[anim][0]) is list:
                    for frame in self.anim_manager[anim][0]:
                        new_anim.append(flip_vertical(frame))
                    self.anim_manager[anim][0] = new_anim

    def update(self, screen, scroll):
        update = super(SimplePropObject, self).update(screen, scroll)
        if self.particle_effect is not None:
            self.particle_effect.update(screen)
        return update
