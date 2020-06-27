import unittest

from chip8 import cpu
from chip8.cpu import CPU
from chip8.keyboard import Keyboard
from chip8.screen import Screen


class TestCPU(unittest.TestCase):
    def setUp(self) -> None:
        self.cpu = CPU(Screen(), Keyboard())

    def test_init(self):
        self.assertEquals(cpu.MEMORY_SIZE, len(self.cpu.memory))
        self.assertEquals(bytearray(cpu.font_sprites), self.cpu.memory[0:len(cpu.font_sprites)])
        self.assertEquals([], self.cpu.stack)
        self.assertEquals(0x200, self.cpu.program_counter)
        self.assertEquals(0x600, CPU(Screen(), Keyboard(), starting_address=0x600).program_counter)
        self.assertEquals([0x00] * 16, self.cpu.V)
        self.assertEquals(0x0000, self.cpu.I)
        self.assertEquals(0x0000, self.cpu.I)
        self.assertEquals(0x00, self.cpu.delay_timer)
        self.assertEquals(0x00, self.cpu.sound_timer)
