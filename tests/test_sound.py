import unittest

from chip8.sound import Sound


class TestSound(unittest.TestCase):
    def test_init(self):
        self.assertFalse(Sound().is_playing)

    def test_update(self):
        sound = Sound()
        sound.update(2)
        self.assertTrue(sound.is_playing)

        sound.update(1)
        self.assertTrue(sound.is_playing)

        sound.update(0)
        self.assertFalse(sound.is_playing)

        sound.update(0)
        self.assertFalse(sound.is_playing)
