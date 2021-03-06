import os
from typing import List

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame

WIDTH = 64
HEIGHT = 32

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Screen:
    surface: pygame.Surface
    buffer: List[List[bool]]
    scaling_factor: int

    def __init__(self, scaling_factor: int = 1):
        self.surface = pygame.display.set_mode((WIDTH * scaling_factor, HEIGHT * scaling_factor))
        self.buffer = [[False] * WIDTH for _ in range(HEIGHT)]
        self.scaling_factor = scaling_factor
        pygame.display.set_caption("CHIP-8")

    def update(self):
        self.surface.fill(BLACK)
        self._draw_pixels()
        pygame.display.flip()

    def _draw_pixels(self):
        for y, row in enumerate(self.buffer):
            for x, pixel in enumerate(row):
                if pixel:
                    rect = (x * self.scaling_factor, y * self.scaling_factor,
                            self.scaling_factor, self.scaling_factor)
                    pygame.draw.rect(self.surface, WHITE, rect)
