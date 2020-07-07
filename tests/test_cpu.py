import unittest

from chip8 import cpu
from chip8.cpu import CPU, UpdateScreen, WaitForKeypress
from chip8.keyboard import Keyboard
from chip8.screen import Screen


class TestCPU(unittest.TestCase):
    def setUp(self):
        self.screen = Screen()
        self.keyboard = Keyboard()
        self.cpu = CPU(self.screen, self.keyboard)

    def test_init(self):
        self.assertEqual(cpu.MEMORY_SIZE, len(self.cpu.memory))
        self.assertEqual(bytearray(cpu.font_sprites), self.cpu.memory[0:len(cpu.font_sprites)])
        self.assertEqual([], self.cpu.stack)
        self.assertEqual(0x200, self.cpu.pc)
        self.assertEqual(0x600, CPU(Screen(), Keyboard(), starting_address=0x600).pc)
        self.assertEqual([0x00] * 16, self.cpu.V)
        self.assertEqual(0x000, self.cpu.I)
        self.assertEqual(0x000, self.cpu.I)
        self.assertEqual(0x00, self.cpu.delay_timer)
        self.assertEqual(0x00, self.cpu.sound_timer)

        self.assertEqual(0x042, CPU(Screen(), Keyboard(), starting_address=0x042).pc)

    def test_decrease_timers(self):
        self.cpu.delay_timer = 0x01
        self.cpu.sound_timer = 0x01
        self.cpu.decrease_timers()
        self.assertEqual(0x00, self.cpu.delay_timer)
        self.assertEqual(0x00, self.cpu.sound_timer)

        self.cpu.decrease_timers()
        self.assertEqual(0x00, self.cpu.delay_timer)
        self.assertEqual(0x00, self.cpu.sound_timer)

    def test_CLS(self):  # 00E0
        for row in self.screen.buffer:
            for x, _ in enumerate(row):
                row[x] = True
        self.cpu._CLS()
        for row in self.screen.buffer:
            self.assertTrue(not any(row))

    def test_RET(self):  # 00EE
        self.cpu.stack.append(0x42)
        self.cpu._RET()
        self.assertEqual(0x42, self.cpu.pc)
        self.assertEqual([], self.cpu.stack)

    def test_JP_nnn(self):  # 1nnn
        self.cpu.instruction = 0x1042
        self.cpu._JP_nnn()
        self.assertEqual(0x42, self.cpu.pc)

    def test_CALL_nnn(self):  # 2nnn
        self.cpu.instruction = 0x2042
        self.cpu.pc = 0x1234
        self.cpu._CALL_nnn()
        self.assertEqual(0x42, self.cpu.pc)
        self.assertEqual([0x1234], self.cpu.stack)

    def test_SE_Vx_nn(self):  # 3xnn
        addr = self.cpu.pc
        self.cpu.V[0x1] = 0x42

        self.cpu.instruction = 0x3042
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr, self.cpu.pc)

        self.cpu.instruction = 0x3141
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr, self.cpu.pc)

        self.cpu.instruction = 0x3142
        self.cpu._SE_Vx_nn()
        self.assertEqual(addr + 2, self.cpu.pc)

    def test_SNE_Vx_nn(self):  # 4xnn
        addr = self.cpu.pc
        self.cpu.V[0x1] = 0x42

        self.cpu.instruction = 0x4142
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr, self.cpu.pc)

        self.cpu.instruction = 0x4042
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr + 2, self.cpu.pc)

        self.cpu.instruction = 0x4141
        self.cpu._SNE_Vx_nn()
        self.assertEqual(addr + 4, self.cpu.pc)

    def test_SE_Vx_Vy(self):  # 5xy0
        self.cpu.instruction = 0x5120
        addr = self.cpu.pc

        self.cpu.V[0x1] = 0x41
        self.cpu.V[0x2] = 0x42
        self.cpu._SE_Vx_Vy()
        self.assertEqual(addr, self.cpu.pc)

        self.cpu.V[0x1] = 0x42
        self.cpu._SE_Vx_Vy()
        self.assertEqual(addr + 2, self.cpu.pc)

    def test_LD_Vx_nn(self):  # 6xnn
        self.cpu.instruction = 0x6142
        self.cpu._LD_Vx_nn()
        self.assertEqual(0x42, self.cpu.V[0x1])

        self.cpu._LD_Vx_nn()
        self.assertEqual(0x42, self.cpu.V[0x1])

    def test_ADD_Vx_nn(self):  # 7xnn
        self.cpu.instruction = 0x7101
        self.cpu.V[0x1] = 0xfe

        self.cpu._ADD_Vx_nn()
        self.assertEqual(0xff, self.cpu.V[0x1])
        self.assertEqual(0x00, self.cpu.V[0xf])

        self.cpu._ADD_Vx_nn()
        self.assertEqual(0x00, self.cpu.V[0x1])
        self.assertEqual(0x00, self.cpu.V[0xf])

    def test_LD_Vx_Vy(self):  # 8xy0
        self.cpu.instruction = 0x8010
        self.cpu.V[0x1] = 0x42
        self.cpu._LD_Vx_Vy()
        self.assertEqual(0x42, self.cpu.V[0x0])

    def test_OR_Vx_Vy(self):  # 8xy1
        self.cpu.instruction = 0x8121
        self.cpu.V[0x1] = 0b01010101
        self.cpu.V[0x2] = 0b00001111
        self.cpu._OR_Vx_Vy()
        self.assertEqual(0b01011111, self.cpu.V[0x1])

    def test_AND_Vx_Vy(self):  # 8xy2
        self.cpu.instruction = 0x8122
        self.cpu.V[0x1] = 0b01010101
        self.cpu.V[0x2] = 0b00001111
        self.cpu._AND_Vx_Vy()
        self.assertEqual(0b00000101, self.cpu.V[0x1])

    def test_XOR_Vx_Vy(self):  # 8xy3
        self.cpu.instruction = 0x8123
        self.cpu.V[0x1] = 0b01010101
        self.cpu.V[0x2] = 0b00001111
        self.cpu._XOR_Vx_Vy()
        self.assertEqual(0b01011010, self.cpu.V[0x1])

    def test_ADD_Vx_Vy(self):  # 8xy4
        self.cpu.instruction = 0x8124
        self.cpu.V[0x1] = 0xfe
        self.cpu.V[0x2] = 0x01

        self.cpu._ADD_Vx_Vy()
        self.assertEqual(0xff, self.cpu.V[0x1])
        self.assertEqual(0x00, self.cpu.V[0xf])

        self.cpu._ADD_Vx_Vy()
        self.assertEqual(0x00, self.cpu.V[0x1])
        self.assertEqual(0x01, self.cpu.V[0xf])

    def test_SUB_Vx_Vy(self):  # 8xy5
        self.cpu.instruction = 0x8125
        self.cpu.V[0x1] = 0x01
        self.cpu.V[0x2] = 0x01

        self.cpu._SUB_Vx_Vy()
        self.assertEqual(0x00, self.cpu.V[0x1])
        self.assertEqual(0x01, self.cpu.V[0xf])

        self.cpu._SUB_Vx_Vy()
        self.assertEqual(0xff, self.cpu.V[0x1])
        self.assertEqual(0x00, self.cpu.V[0xf])

    def test_SHR_Vx_Vy(self):  # 8xy6
        self.cpu.instruction = 0x8126
        self.cpu.V[0x2] = 0b11110000
        self.cpu._SHR_Vx_Vy()
        self.assertEqual(0b01111000, self.cpu.V[0x1])
        self.assertEqual(0b00000000, self.cpu.V[0xf])

        self.cpu.V[0x2] = 0b00001111
        self.cpu._SHR_Vx_Vy()
        self.assertEqual(0b00000111, self.cpu.V[0x1])
        self.assertEqual(0b00000001, self.cpu.V[0xf])

    def test_SUBN_Vx_Vy(self):  # 8xy7
        self.cpu.instruction = 0x8127
        self.cpu.V[0x1] = 0x01
        self.cpu.V[0x2] = 0x01

        self.cpu._SUBN_Vx_Vy()
        self.assertEqual(0x00, self.cpu.V[0x1])
        self.assertEqual(0x01, self.cpu.V[0xf])

        self.cpu.V[0x1] = 0x02
        self.cpu._SUBN_Vx_Vy()
        self.assertEqual(0xff, self.cpu.V[0x1])
        self.assertEqual(0x00, self.cpu.V[0xf])

    def test_SHL_Vx_Vy(self):  # 8xyE
        self.cpu.instruction = 0x812E
        self.cpu.V[0x2] = 0b11110000
        self.cpu._SHL_Vx_Vy()
        self.assertEqual(0b11100000, self.cpu.V[0x1])
        self.assertEqual(0b00000001, self.cpu.V[0xf])

        self.cpu.V[0x2] = 0b00001111
        self.cpu._SHL_Vx_Vy()
        self.assertEqual(0b00011110, self.cpu.V[0x1])
        self.assertEqual(0b00000000, self.cpu.V[0xf])

    def test_SNE_Vx_Vy(self):  # 9xy0
        self.cpu.instruction = 0x9120
        addr = self.cpu.pc

        self.cpu.V[0x1] = 0x42
        self.cpu.V[0x2] = 0x42
        self.cpu._SNE_Vx_Vy()
        self.assertEqual(addr, self.cpu.pc)

        self.cpu.V[0x1] = 0x41
        self.cpu._SNE_Vx_Vy()
        self.assertEqual(addr + 2, self.cpu.pc)

    def test_LD_I_nnn(self):  # Annn
        self.cpu.instruction = 0xA042
        self.cpu._LD_I_nnn()
        self.assertEqual(0x42, self.cpu.I)

    def test_JP_V0_nnn(self):  # Bnnn
        self.cpu.instruction = 0xB042
        self.cpu.V[0x0] = 0x42
        self.cpu._JP_V0_nnn()
        self.assertEqual(0x42 + 0x42, self.cpu.pc)

    def test_RND_Vx_nn(self):  # Cxnn
        numbers = set()
        for mask in range(0xff + 1):
            self.cpu.instruction = 0xC100 | mask
            self.cpu._RND_Vx_nn()
            rnd = self.cpu.V[0x1]
            self.assertEqual(rnd & mask, rnd)
            numbers.add(rnd)
        self.assertGreater(len(numbers), 50)

    def test_DRW_Vx_Vy_n(self):  # Dxyn
        to_int = lambda bool_list: sum([val << (7 - pos) for pos, val in enumerate(bool_list)])
        x = 4
        y = 2
        digit = 7

        self.cpu.instruction = 0xD125
        self.cpu.I = digit * 5
        self.cpu.V[0x1] = x
        self.cpu.V[0x2] = y

        with self.assertRaises(UpdateScreen):
            self.cpu._DRW_Vx_Vy_n()
        for line in range(5):
            self.assertEqual(cpu.font_sprites[digit * 5 + line], to_int(self.screen.buffer[y + line][x:x + 8]))
        self.assertEqual(0x00, self.cpu.V[0xf])

        with self.assertRaises(UpdateScreen):
            self.cpu._DRW_Vx_Vy_n()
        for line in range(5):
            self.assertEqual(0x00, to_int(self.screen.buffer[y + line][x:x + 8]))
        self.assertEqual(0x01, self.cpu.V[0xf])

        self.cpu.V[0x1] = 62
        self.cpu.V[0x2] = 30
        with self.assertRaises(UpdateScreen):
            self.cpu._DRW_Vx_Vy_n()
        self.assertEqual([True, True], self.screen.buffer[30][62:64])
        self.assertEqual([False, False], self.screen.buffer[31][62:64])
        self.assertEqual([False, False], self.screen.buffer[0][62:64])
        self.assertEqual([False, True], self.screen.buffer[1][62:64])
        self.assertEqual([False, True], self.screen.buffer[2][62:64])

        self.assertEqual([True, True], self.screen.buffer[30][0:2])
        self.assertEqual([False, True], self.screen.buffer[31][0:2])
        self.assertEqual([True, False], self.screen.buffer[0][0:2])
        self.assertEqual([False, False], self.screen.buffer[1][0:2])
        self.assertEqual([False, False], self.screen.buffer[2][0:2])

    def test_SKP_Vx(self):  # Ex9E
        self.cpu.instruction = 0xE19E
        addr = self.cpu.pc

        self.cpu.V[0x1] = 0x1

        self.cpu._SKP_Vx()
        self.assertEqual(addr, self.cpu.pc)

        self.keyboard.pressed_keys.add(0x1)
        self.cpu._SKP_Vx()
        self.assertEqual(addr + 2, self.cpu.pc)

    def test_SKNP_Vx(self):  # ExA1
        self.cpu.instruction = 0xE1A1
        addr = self.cpu.pc

        self.cpu.V[0x1] = 0x1

        self.keyboard.pressed_keys.add(0x1)
        self.cpu._SKNP_Vx()
        self.assertEqual(addr, self.cpu.pc)

        self.keyboard.pressed_keys.remove(0x1)
        self.cpu._SKNP_Vx()
        self.assertEqual(addr + 2, self.cpu.pc)

    def test_LD_Vx_DT(self):  # Fx07
        self.cpu.instruction = 0xF107
        self.cpu.delay_timer = 0x42
        self.cpu._LD_Vx_DT()
        self.assertEqual(0x42, self.cpu.V[0x1])

    def test_LD_Vx_K(self):  # Fx0A
        self.cpu.instruction = 0xF10A
        with self.assertRaises(WaitForKeypress):
            self.cpu._LD_Vx_K()
        self.assertTrue(self.cpu.waiting_for_keypress)

        self.cpu.key_was_pressed(0x1)
        self.assertFalse(self.cpu.waiting_for_keypress)
        self.assertEqual(0x1, self.cpu.V[0x1])

    def test_LD_DT_Vx(self):  # Fx15
        self.cpu.instruction = 0xF115
        self.cpu.V[0x1] = 0x42
        self.cpu._LD_DT_Vx()
        self.assertEqual(0x42, self.cpu.delay_timer)

    def test_LD_ST_Vx(self):  # Fx18
        self.cpu.instruction = 0xF118
        self.cpu.V[0x1] = 0x42
        self.cpu._LD_ST_Vx()
        self.assertEqual(0x42, self.cpu.sound_timer)

    def test_ADD_I_Vx(self):  # Fx1E
        self.cpu.instruction = 0xF11E
        self.cpu.V[0x1] = 0x1
        self.cpu.I = 0xffe
        self.cpu._ADD_I_Vx()
        self.assertEqual(0xfff, self.cpu.I)

        self.cpu._ADD_I_Vx()
        self.assertEqual(0x000, self.cpu.I)

    def test_LD_F_Vx(self):  # Fx29
        self.cpu.instruction = 0xF129
        self.cpu.V[0x1] = 7
        self.cpu._LD_F_Vx()
        self.assertEqual(7 * 5, self.cpu.I)

    def test_LD_B_Vx(self):  # Fx33
        self.cpu.instruction = 0xF133
        self.cpu._LD_B_Vx()

    def test_LD_I_Vx(self):  # Fx55
        self.cpu.instruction = 0xF755
        self.cpu.I = 0x123
        for reg in range(0x7 + 1):
            self.cpu.V[reg] = reg * 2
        self.cpu._LD_I_Vx()
        for reg in range(0x7 + 1):
            self.assertEqual(reg * 2, self.cpu.memory[0x123 + reg])
        self.assertEqual(0x123 + 0x7 + 1, self.cpu.I)

    def test_LD_Vx_I(self):  # Fx65
        self.cpu.instruction = 0xF765
        self.cpu.I = 0x123
        for reg in range(0x7 + 1):
            self.cpu.memory[0x123 + reg] = reg * 2
        self.cpu._LD_Vx_I()
        for reg in range(0x7 + 1):
            self.assertEqual(reg * 2, self.cpu.V[reg])
        self.assertEqual(0x123 + 0x7 + 1, self.cpu.I)
