import os
import unittest

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame

from chip8.keyboard import Keyboard


class TestKeyboard(unittest.TestCase):
    def test_init(self):
        keyboard = Keyboard()
        self.assertEqual(set(), keyboard.pressed_keys)

    def test_keydown(self):
        keyboard = Keyboard()
        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.assertEqual(set(), keyboard.pressed_keys)

        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        self.assertEqual({0x1}, keyboard.pressed_keys)

        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
        self.assertEqual({0x1, 0x2}, keyboard.pressed_keys)

        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
        self.assertEqual({0x1, 0x2}, keyboard.pressed_keys)

    def test_keyup(self):
        keyboard = Keyboard()
        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        key = keyboard.keyup(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.assertEqual(set(), keyboard.pressed_keys)
        self.assertIsNone(key)

        keyboard.keydown(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        key = keyboard.keyup(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        self.assertEqual(set(), keyboard.pressed_keys)
        self.assertEqual(0x1, key)

        key = keyboard.keyup(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        self.assertEqual(set(), keyboard.pressed_keys)
        self.assertEqual(0x1, key)
