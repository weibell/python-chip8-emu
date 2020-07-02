import os
import unittest

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame

from chip8.chip8 import Chip8, SIXTY_HERTZ_CLOCK


class TestChip8(unittest.TestCase):
    def test_load(self):
        chip8 = Chip8(scaling_factor=1, cycles_per_frame=1, starting_address=0x042)
        self.assertEqual(0x042, chip8.cpu.program_counter)

    def test_handle_events(self):
        chip8 = Chip8(scaling_factor=1, cycles_per_frame=1, starting_address=0x000)
        ld_V0_41 = b"\x60\x41"
        ld_DT_V0 = b"\xf0\x15"
        jp_0x042 = b"\x10\x42"
        chip8.load(ld_V0_41 + ld_DT_V0 + jp_0x042)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertEqual(0x002, chip8.cpu.program_counter)
        self.assertEqual(0x41, chip8.cpu.V[0])

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertEqual(0x004, chip8.cpu.program_counter)
        self.assertEqual(0x41, chip8.cpu.delay_timer)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertEqual(0x042, chip8.cpu.program_counter)

        pygame.event.post(pygame.event.Event(pygame.QUIT))
        with self.assertRaises(SystemExit):
            chip8.handle_events()

    def test_key_was_pressed(self):
        chip8 = Chip8(scaling_factor=1, cycles_per_frame=1, starting_address=0x000)
        ld_V0_K = b"\xf0\x0A"
        chip8.load(ld_V0_K)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertTrue(chip8.cpu.waiting_for_keypress)

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        chip8.handle_events()

        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_1))
        chip8.handle_events()
        self.assertFalse(chip8.cpu.waiting_for_keypress)
        self.assertEqual(0x01, chip8.cpu.V[0])

    def test_has_screen_changed(self):
        chip8 = Chip8(scaling_factor=1, cycles_per_frame=1, starting_address=0x000)
        ld_I_0x042 = b"\xa0\x42"
        drw_Vx_Vy_n = b"\xd0\x01"
        chip8.load(ld_I_0x042 + drw_Vx_Vy_n)
        chip8.cpu.memory[0x42] = 0b10000000

        BLACK = (0, 0, 0, 255)
        WHITE = (255, 255, 255, 255)

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertEqual(BLACK, chip8.screen.surface.get_at((0, 0)))

        pygame.event.post(pygame.event.Event(SIXTY_HERTZ_CLOCK))
        chip8.handle_events()
        self.assertEqual(WHITE, chip8.screen.surface.get_at((0, 0)))
