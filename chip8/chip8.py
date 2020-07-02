import os
import sys

from chip8.sound import Sound

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame

from chip8.cpu import CPU, UpdateScreen, WaitForKeypress
from chip8.keyboard import Keyboard
from chip8.screen import Screen

SIXTY_HERTZ_CLOCK = pygame.USEREVENT
SIXTY_HERTZ = 60


class Chip8:
    screen: Screen
    keyboard: Keyboard
    sound: Sound
    cpu: CPU
    cycles_per_frame: int

    def __init__(self, scaling_factor: int, cycles_per_frame: int, starting_address: int):
        pygame.init()
        self.screen = Screen(scaling_factor)
        self.keyboard = Keyboard()
        self.sound = Sound()
        self.cpu = CPU(self.screen, self.keyboard, starting_address)
        self.cycles_per_frame = cycles_per_frame

        sixty_hertz_ms = round(1000 / SIXTY_HERTZ)
        pygame.time.set_timer(SIXTY_HERTZ_CLOCK, sixty_hertz_ms)
        print(f"Target CPU speed: {cycles_per_frame * SIXTY_HERTZ} instructions per second")
        print(f"Screen scaling factor: {scaling_factor}")

    def load(self, rom: bytes):
        self.cpu.load(rom)

    def run(self):
        while True:
            self.step()

    def step(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.keyboard.keydown(event)

            elif event.type == pygame.KEYUP:
                key = self.keyboard.keyup(event)
                if self.cpu.waiting_for_keypress and key is not None:
                    self.cpu.key_was_pressed(key)

            elif event.type == SIXTY_HERTZ_CLOCK:
                if self.cpu.waiting_for_keypress:
                    continue

                has_screen_changed = False
                self.cpu.decrease_timers()
                for _ in range(self.cycles_per_frame):
                    try:
                        self.cpu.cpu_tick()
                    except UpdateScreen:
                        has_screen_changed = True
                    except WaitForKeypress:
                        break
                self.sound.update(self.cpu.sound_timer)
                if has_screen_changed:
                    self.screen.update()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
