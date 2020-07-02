import unittest

from chip8.screen import Screen

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


class TestScreen(unittest.TestCase):
    def test_init(self):
        screen = Screen()
        self.assertEqual(32, len(screen.buffer))
        for row in range(32):
            self.assertEqual([False] * 64, screen.buffer[row])

    def test_update(self):
        screen = Screen()
        screen.update()
        for row in range(32):
            for col in range(64):
                self.assertEqual(BLACK, screen.surface.get_at((col, row)))
        for row in range(32):
            for col in range(64):
                screen.buffer[row][col] = True
        screen.update()
        for row in range(32):
            for col in range(64):
                self.assertEqual(WHITE, screen.surface.get_at((col, row)))

    def test_scaling_factor(self):
        screen = Screen(scaling_factor=3)
        self.assertEqual(64 * 3, screen.surface.get_width())
        self.assertEqual(32 * 3, screen.surface.get_height())
        screen.buffer[1][2] = True
        screen.update()
        for y in range(screen.surface.get_height()):
            for x in range(screen.surface.get_width()):
                if x in [6, 7, 8] and y in [3, 4, 5]:
                    self.assertEqual(WHITE, screen.surface.get_at((x, y)))
                else:
                    self.assertEqual(BLACK, screen.surface.get_at((x, y)))
