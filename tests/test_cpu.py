import unittest

from chip8 import cpu
from chip8.cpu import CPU
from chip8.keyboard import Keyboard
from chip8.screen import Screen


class TestCPU(unittest.TestCase):
    def setUp(self) -> None:
        self.screen = Screen()
        self.keyboard = Keyboard()
        self.cpu = CPU(self.screen, self.keyboard)

    def test_init(self):
        self.assertEqual(cpu.MEMORY_SIZE, len(self.cpu.memory))
        self.assertEqual(bytearray(cpu.font_sprites), self.cpu.memory[0:len(cpu.font_sprites)])
        self.assertEqual([], self.cpu.stack)
        self.assertEqual(0x200, self.cpu.program_counter)
        self.assertEqual(0x600, CPU(Screen(), Keyboard(), starting_address=0x600).program_counter)
        self.assertEqual([0x00] * 16, self.cpu.V)
        self.assertEqual(0x0000, self.cpu.I)
        self.assertEqual(0x0000, self.cpu.I)
        self.assertEqual(0x00, self.cpu.delay_timer)
        self.assertEqual(0x00, self.cpu.sound_timer)

    @unittest.skip("not implemented")
    def test_JP_MC(self):  # 0nnn
        self.cpu.JP_MP()

    def test_CLS(self):  # 00E0
        for row in self.screen.screen_buffer:
            for x, _ in enumerate(row):
                row[x] = True
        self.cpu._CLS()
        for row in self.screen.screen_buffer:
            self.assertTrue(not any(row))

    def test_RET(self):  # 00EE
        self.cpu.stack.append(0x42)
        self.cpu._RET()
        self.assertEqual(0x42, self.cpu.program_counter)
        self.assertEqual([], self.cpu.stack)

    def test_JP_nnn(self):  # 1nnn
        self.cpu.instruction = 0x1042
        self.cpu._JP_nnn()
        self.assertEqual(0x42, self.cpu.program_counter)

    def test_CALL_nnn(self):  # 2nnn
        self.cpu.instruction = 0x2042
        self.cpu.program_counter = 0x1234
        self.cpu._CALL_nnn()
        self.assertEqual(0x42, self.cpu.program_counter)
        self.assertEqual([0x1234], self.cpu.stack)

    def test_SE_Vx_nn(self):  # 3xnn
        addr = self.cpu.program_counter
        self.cpu.V[1] = 0x42

        self.cpu.instruction = 0x3042
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr, self.cpu.program_counter)

        self.cpu.instruction = 0x3141
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr, self.cpu.program_counter)

        self.cpu.instruction = 0x3142
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr + 2, self.cpu.program_counter)

    def test_SNE_Vx_nn(self):  # 4xnn
        addr = self.cpu.program_counter
        self.cpu.V[1] = 0x42

        self.cpu.instruction = 0x4142
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr, self.cpu.program_counter)

        self.cpu.instruction = 0x4042
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr + 2, self.cpu.program_counter)

        self.cpu.instruction = 0x4141
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr + 4, self.cpu.program_counter)

    def test_SE_Vx_Vy(self):  # 5xy0
        addr = self.cpu.program_counter
        self.cpu.V[1] = 0x42
        self.cpu.V[2] = 0x42

        self.cpu.instruction = 0x5010
        self.cpu._SE_Vx_Vy()
        self.assertEqual(addr, self.cpu.program_counter)

        self.cpu.instruction = 0x5120
        self.cpu._SE_Vx_Vy()
        self.assertEqual(addr + 2, self.cpu.program_counter)
