import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame


class Sound:
    beep: pygame.mixer.Sound
    is_playing: bool

    def __init__(self):
        pygame.mixer.init()
        self.beep = pygame.mixer.Sound("chip8/beep.wav")
        self.is_playing = False

    def update(self, sound_timer: int):
        if sound_timer > 0 and not self.is_playing:
            self.beep.play()
            self.is_playing = True
        elif sound_timer == 0 and self.is_playing:
            self.beep.stop()
            self.is_playing = False
