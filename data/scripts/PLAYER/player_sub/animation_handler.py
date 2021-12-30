import pygame as p
import math

from .dash import update_dash


def animate_level_up_ring(player):
    if player.ring_lu:
        if p.time.get_ticks() - player.delay_rlu > 150:
            player.delay_rlu = p.time.get_ticks()

            if player.id_rlu + 1 < len(player.lvl_up_ring):
                player.id_rlu += 1
            else:
                player.ring_lu = False
                player.id_rlu = 0

            player.curr_frame_ring = player.lvl_up_ring[player.id_rlu]
            player.screen.blit(player.curr_frame_ring, player.curr_frame_ring.get_rect(
                center=player.rect.topleft - player.camera.offset.xy + p.Vector2(15, 80)
            ))


def animation_handing(player, dt, m, pos):
    player.dust_particle_effet.update(player.screen)

    # Draw the Ring
    angle = math.atan2(
        m[1] - (player.rect.top + 95 - player.camera.offset.y),
        m[0] - (player.rect.left + 10 - player.camera.offset.x),
    )
    x, y = pos[0] - math.cos(angle), pos[1] - math.sin(angle) + 10
    angle = abs(math.degrees(angle)) + 90 if angle < 0 else 360 - math.degrees(angle) + 90
    image = p.transform.rotate(player.attack_pointer, angle)
    ring_pos = (x - image.get_width() // 2 + 69, y - image.get_height() // 2 + 139)

    # Blit attack ring only on this condition
    if not player.ring_lu and player.camera_status != "auto":
        player.screen.blit(image, ring_pos)

    update_attack(player, pos)

    if not player.attacking and not player.dashing:
        angle = math.atan2(
            m[1] - (player.rect.top + 95 - player.camera.offset.y),
            m[0] - (player.rect.left + 10 - player.camera.offset.x),
        )
        angle = abs(math.degrees(angle)) if angle < 0 else 360 - math.degrees(angle)

        if player.walking:
            if p.time.get_ticks() - player.delay_animation > 100:
                player.index_animation = (player.index_animation + 1) % len(player.anim["right"])
                player.delay_animation = p.time.get_ticks()

        else:
            if p.time.get_ticks() - player.delay_animation > 350:
                player.index_animation = (player.index_animation + 1) % len(player.anim["idle_r"])
                player.delay_animation = p.time.get_ticks()

        if player.camera_status != "auto" and not player.inventory.show_menu and not player.upgrade_station.show_menu:
            if 135 >= angle > 45:
                set_looking(player, "up", pos)
            elif 225 >= angle > 135:
                set_looking(player, "left", pos)
            elif 315 >= angle > 225:
                set_looking(player, "down", pos)
            else:
                set_looking(player, "right", pos)
        else:
            "we will put a str from camera instead of 'right' later on."
            set_looking(player, "right", pos)

    update_dash(player, dt, pos)

    # Level UP ring
    animate_level_up_ring(player)


def set_looking(player, dir_: str, pos):
    """
        This function is for coordinating the hit box
        and also playing the looking animation
    """
    if dir_ == "up":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = True, False, False, False
    elif dir_ == "down":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, True, False, False
    elif dir_ == "left":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, False, False, True
    elif dir_ == "right":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, False, True, False

    if player.walking:
        temp_anim = player.anim[dir_]
    else:
        temp_anim = player.anim["".join(["idle_", dir_[0]])]
    if player.index_animation > len(temp_anim)-1:
        player.index_animation = 0

    player.screen.blit(temp_anim[player.index_animation], pos)


def user_interface(player, m, player_pos, dt):
    if player.camera_status != "auto":
        # Health bar
        p.draw.rect(player.screen, (255, 0, 0),
                    p.Rect(player.hp_box_rect.x+10, player.hp_box_rect.y + 10, player.health, 40))

        # Dash Cool down bar
        p.draw.rect(player.screen, (0, 255, 0),
                    p.Rect(player.hp_box_rect.x+10, player.hp_box_rect.y + 80, player.dash_width,
                           15))

        # Experience bar
        p.draw.rect(player.screen, (0, 255, 255), p.Rect(player.hp_box_rect.x + 10, player.hp_box_rect.y + 110, player.experience_width, 20))

        # Player UI
        player.screen.blit(player.health_box, player.hp_box_rect)

        # Level status button goes here
        player.upgrade_station.update(player)

        # Inventory Icon
        player.inventory.update(player)
        # sending its own object in order that the inventory can access to the player's damages

    # recalculate the damages, considering the equipped weapon
    player.modified_damages = player.damage + (player.inventory.get_equipped("Weapon").damage
                                               if player.inventory.get_equipped("Weapon") is not None else 0)
    equipped = player.inventory.get_equipped("Weapon")
    if hasattr(equipped, "special_effect"):
        equipped.special_effect(player)

    # if player presses interaction key and is in a interaction zone
    if player.Interactable and player.is_interacting:
        player.npc_catalog.draw(player.npc_text, dt)


def update_attack(player, pos):
    """ This function is for updating the players hit box based on the mouse position and also updating his animation"""

    if player.attacking and player.camera_status != "auto":

        # sets the attacking hitbox according to the direction
        rect = p.Rect(player.rect.x - player.camera.offset.x - 50, player.rect.y - player.camera.offset.y - 40,
                      *player.rect.size)

        # Some tweaks to attacking sprite
        temp = pos

        if player.looking_up:
            player.attacking_hitbox = p.Rect(rect.x, rect.y - player.attacking_hitbox_size[0],
                                             player.attacking_hitbox_size[1], player.attacking_hitbox_size[0])
        elif player.looking_down:
            player.attacking_hitbox = p.Rect(rect.x, rect.bottom, player.attacking_hitbox_size[1],
                                             player.attacking_hitbox_size[0])
        elif player.looking_left:
            player.attacking_hitbox = p.Rect(rect.x - player.attacking_hitbox_size[1], rect.y,
                                             player.attacking_hitbox_size[1], player.attacking_hitbox_size[0])
            temp = pos[0] - 2, pos[1]  # Fix Image position
        elif player.looking_right:
            player.attacking_hitbox = p.Rect(rect.right, rect.y, player.attacking_hitbox_size[1],
                                             player.attacking_hitbox_size[0])
            temp = pos[0] + 2, pos[1]  # Fix Image position

        # p.draw.rect(player.screen, (255, 0, 0), player.attacking_hitbox, 2)
        # p.draw.rect(player.screen, (0, 255, 0), rect, 2)

        # animation delay of 100 ms
        if p.time.get_ticks() - player.delay_attack_animation > 100 and player.restart_animation:

            # select the animation list according to where the player's looking at
            a = player.anim
            if player.looking_right:
                curr_anim = a['right_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['right_a_2']
            elif player.looking_left:
                curr_anim = a['left_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['left_a_2']
            elif player.looking_down:
                curr_anim = a['down_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['down_a_2']
            elif player.looking_up:
                curr_anim = a['up_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['up_a_2']

            if player.index_attack_animation + 1 < len(curr_anim):  # check if the animation didn't reach its end
                player.delay_attack_animation = p.time.get_ticks()  # reset the delay
                player.attacking_frame = curr_anim[
                    player.index_attack_animation + 1]  # change the current animation frame
                player.index_attack_animation += 1  # increment the animation index
            else:
                player.restart_animation = False   # don't allow the restart of the animation until a next combo is reached
                player.index_attack_animation = 0   # reset the animation index, without changing the frame in order to stay in "pause"
                player.next_combo_available = True  # allow to attack again

        # p.draw.rect(player.screen, (255,255,255), player.Rect)

        # ----- Blit Animation ------

        player.screen.blit(player.attacking_frame, temp)

        print(player.current_combo)
        # reset the whole thing if the combo reach his end and the animation of the last hit ended too
        if player.current_combo == player.last_attack and not player.restart_animation and \
                not player.index_attack_animation:
            player.attacking = False  # stop attack
            player.current_combo = 0  # reset combo number
            player.next_combo_available = True  # allow to attack again
            player.restart_animation = True  # allow to restart an animation

        # p.draw.rect(player.screen, (255, 0, 0), player.attacking_hitbox) show hitbox

        # End of the attack animation
        if p.time.get_ticks() - player.last_attacking_click > player.attack_speed:
            player.attacking = False
            player.current_combo = 0
            player.next_combo_available = True
            player.restart_animation = True
            # RESET ANIMATION HERE
