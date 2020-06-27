import sys

import pygame

from chip8.cpu import CPU, UpdateScreen, WaitForKeypress
from chip8.keyboard import Keyboard
from chip8.screen import Screen

CPU_CLOCK = pygame.USEREVENT
CPU_CYCLES_PER_TICK = 10

SIXTY_HERTZ_CLOCK = pygame.USEREVENT + 1
SIXTY_HERTZ = 60


class Chip8:
    screen: Screen
    keyboard: Keyboard
    cpu: CPU

    def __init__(self, cpu_frequency: int, scaling_factor: int, starting_address: int):
        self.screen = Screen(scaling_factor)
        self.keyboard = Keyboard()
        self.cpu = CPU(self.screen, self.keyboard, starting_address)

        cpu_clock_ms = round(CPU_CYCLES_PER_TICK * 1000 / cpu_frequency) or 1
        sixty_hertz_ms = round(1000 / SIXTY_HERTZ)
        pygame.time.set_timer(CPU_CLOCK, cpu_clock_ms)
        pygame.time.set_timer(SIXTY_HERTZ_CLOCK, sixty_hertz_ms)
        print(f"Target CPU frequency: {CPU_CYCLES_PER_TICK * 1000 // cpu_clock_ms} Hz")
        print(f"The screen will be scaled with a factor of {scaling_factor}")

    def load(self, rom: bytes):
        self.cpu.load(rom)

    def run(self):
        self._main_loop()

    def _main_loop(self):

        def cpu_clock_event():
            has_screen_changed = False
            for _ in range(CPU_CYCLES_PER_TICK):
                try:
                    self.cpu.cpu_tick()
                except UpdateScreen:
                    has_screen_changed = True
                except WaitForKeypress:
                    break
            if has_screen_changed:
                self.screen.update()

        while True:
            for event in pygame.event.get():
                if self.cpu.waiting_for_keypress and not event.type == pygame.KEYDOWN:
                    continue

                if event.type == CPU_CLOCK:
                    cpu_clock_event()

                elif event.type == SIXTY_HERTZ_CLOCK:
                    self.cpu.sixty_hertz_tick()

                elif event.type == pygame.KEYDOWN:
                    self.keyboard.keydown(event)

                elif event.type == pygame.KEYUP:
                    key = self.keyboard.keyup(event)
                    if key is not None:
                        self.cpu.key_was_pressed(key)

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
