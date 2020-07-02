import os
import unittest

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame

from chip8.chip8 import Chip8, SIXTY_HERTZ_CLOCK


class TestChip8(unittest.TestCase):
    def test_load(self):
        chip8 = Chip8(1, 1, starting_address=0x042)
        self.assertEqual(0x042, chip8.cpu.program_counter)

    def test_step(self):
        chip8 = Chip8(1, 1, starting_address=0x000)
        ld_V0_41 = b"\x60\x41"
        ld_DT_V0 = b"\xf0\x15"
        jp_0x042 = b"\x10\x42"
        chip8.load(ld_V0_41 + ld_DT_V0 + jp_0x042)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.step()
        self.assertEqual(0x002, chip8.cpu.program_counter)
        self.assertEqual(0x41, chip8.cpu.V[0])

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.step()
        self.assertEqual(0x004, chip8.cpu.program_counter)
        self.assertEqual(0x41, chip8.cpu.delay_timer)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.step()
        self.assertEqual(0x042, chip8.cpu.program_counter)