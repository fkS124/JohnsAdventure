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

    def reset(self): self.current_text_index  =  0  # Resets text

    def draw(self, path):
        if not path: # If string is not empty
            return
        self.screen.blit(self.icon, (155 , self.screen.get_height() // 2 + 80)) # UI
        
        try: # I want something from the json file
            text = self.data[path]['text'] # Import from Json the AI/UI 's text
        except PathNotFound: # I make my own text
            text = path

        self.timer += self.dt # Speed of text/delta_time
        if self.timer > 0.030:
            self.current_text_index += 1 # Next letter
            if self.current_text_index < len(text):
                self.current_text_index += 1
                if text[self.current_text_index] != ' ':  self.sound.play()  # if there isn't space
            # --- UPDATE CONTENT ---
            self.text_display = [text[44 * i : min(self.current_text_index, 44 * (i + 1))] for i in range(4)] # Update letters strings
            self.text_surfaces = [self.f.render(text, True, (0,0,0)) for text in self.text_display]  # Transform them into a surface
            self.timer = 0 # Reset timer /  End of if statement
        for i, surface in enumerate(self.text_surfaces): # Blits the text
            self.screen.blit(surface, (self.text_pos[0], self.text_pos[1] + i * 30))