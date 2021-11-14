import pygame as pg
import json
from ..utils import scale, resource_path

class Interface:
    def __init__(self, screen, ui, f, dt):
        self.screen, self.f, self.dt = screen, f, dt
        self.icon = scale(ui.parse_sprite('interface_button.png').convert(), 8)
        self.current_text_index = self.timer = 0
        self.text_pos = ( screen.get_width() // 2 - 420, screen.get_height() // 2 + 110) # Position of the first sentence
        
        with open(resource_path('data/database/language.json')) as f: 
            self.data = json.load(f); f.close() # Read Json and close it
        
        self.sound = pg.mixer.Sound(resource_path('data/sound/letter_sound.wav')); self.sound.set_volume(0.2) # Insert music and change sound
        self.text_display = ['' for i in range(4)] # Create 4 empty text renders
        self.text_surfaces = [self.f.render(self.text_display[i], True, (0,0,0)) for i in range(4)] # font render each of them

    def reset(self): self.current_text_index  =  -1  # Resets text

    def draw(self, path):

        # Blit Background UI
        self.screen.blit(self.icon, (155 , self.screen.get_height() // 2 + 80))
        
        # Tries to take text from npc json else its custom text
        try: 
            text = self.data[path]['text']
        except KeyError:
            text = path

        self.timer += self.dt # Speed of text/delta_time


        if self.timer > 0.030 * 2:
            self.current_text_index += 1 # Next letter
            if self.current_text_index < len(text) - 1:

                # Goes to the next key
                self.current_text_index += 1

                # This is for playing sounds in all keys except space
                # if text[self.current_text_index] != ' ':  
                #    self.sound.play()
            
            
            # --- UPDATE CONTENT ---
            
            self.text_display = [text[44 * i : min(self.current_text_index, 44 * (i + 1))] for i in range(4)] # Update letters strings
            
            self.text_surfaces = [self.f.render(text, True, (0,0,0)) for text in self.text_display]  # Transform them into a surface
            
            # Reset timer
            self.timer = 0

        # Display the keywords
        for i, surface in enumerate(self.text_surfaces): 
            self.screen.blit(surface, (self.text_pos[0], self.text_pos[1] + i * 30))