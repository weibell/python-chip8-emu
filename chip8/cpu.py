import random
from typing import Callable, List, Dict, Union

from chip8.keyboard import Keyboard
from chip8.screen import Screen

MEMORY_SIZE = 4096


class CPU:
    """
    The following naming convention is used to refer to the nibbles in an instruction,
    which generally follows a ?nnn, ?xnn, or ?xyn form.

    nnn: the lowest 12 bits of the instruction
    nn:  the lowest 8 bits of the instruction
    n:   the lowest 4 bits of the instruction
    x:   the lower 4 bits of the high byte of the instruction
    y:   the upper 4 bits of the low byte of the instruction
    """

    screen: Screen
    keyboard: Keyboard
    waiting_for_keypress: bool

    memory: bytearray
    stack: List[int]
    program_counter: int
    V: List[int]
    I: int
    delay_timer: int
    sound_timer: int
    instruction: int

    opcode_table: Dict[int, Union[Callable, Dict[int, Callable]]]

    def __init__(self, screen: Screen, keyboard: Keyboard, starting_address: int = 0x200):
        self.screen = screen
        self.keyboard = keyboard
        self.waiting_for_keypress = False
        self.starting_address = starting_address

        self.memory = bytearray(MEMORY_SIZE)
        self.memory[0x000:len(font_sprites)] = font_sprites
        self.stack = []
        self.program_counter = starting_address
        self.V = [0x00] * 16
        self.I = 0x000
        self.delay_timer = 0x00
        self.sound_timer = 0x00
        self.instruction = 0x0000

        self.opcode_table = self._build_opcode_table()

    def load(self, rom: bytes):
        self.memory[self.starting_address:self.starting_address + len(rom)] = rom

    def cpu_tick(self):
        self.instruction = self.memory[self.program_counter] << 8 | self.memory[self.program_counter + 1]
        self.program_counter += 2
        self.opcode_handler()

    def decrease_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def key_was_pressed(self, key):
        self.waiting_for_keypress = False
        self.Vx = key

    def _build_opcode_table(self):
        return {
            0x0: {
                0xE0: self._CLS,  # 00E0
                0xEE: self._RET  # 00EE
            },
            0x1: self._JP_nnn,  # 1nnn
            0x2: self._CALL_nnn,  # 2nnn
            0x3: self._SE_Vx_nn,  # 3xnn
            0x4: self._SNE_Vx_nn,  # 4xnn
            0x5: self._SE_Vx_Vy,  # 5xy0
            0x6: self._LD_Vx_nn,  # 6xnn
            0x7: self._ADD_Vx_nn,  # 7xnn
            0x8: {
                0x0: self._LD_Vx_Vy,  # 8xy0
                0x1: self._OR_Vx_Vy,  # 8xy1
                0x2: self._AND_Vx_Vy,  # 8xy2
                0x3: self._XOR_Vx_Vy,  # 8xy3
                0x4: self._ADD_Vx_Vy,  # 8xy4
                0x5: self._SUB_Vx_Vy,  # 8xy5
                0x6: self._SHR_Vx_Vy,  # 8xy6
                0x7: self._SUBN_Vx_Vy,  # 8xy7
                0xE: self._SHL_Vx_Vy  # 8xyE
            },
            0x9: self._SNE_Vx_Vy,  # 9xy0
            0xA: self._LD_I_nnn,  # Annn
            0xB: self._JP_V0_nnn,  # Bnnn
            0xC: self._RND_Vx_nn,  # Cxnn
            0xD: self._DRW_Vx_Vy_n,  # Dxyn
            0xE: {
                0x9E: self._SKP_Vx,  # Ex9E
                0xA1: self._SKNP_Vx  # ExA1
            },
            0xF: {
                0x07: self._LD_Vx_DT,  # Fx07
                0x0A: self._LD_Vx_K,  # Fx0A
                0x15: self._LD_DT_Vx,  # Fx15
                0x18: self._LD_ST_Vx,  # Fx18
                0x1E: self._ADD_I_Vx,  # Fx1E
                0x29: self._LD_F_Vx,  # Fx29
                0x33: self._LD_B_Vx,  # Fx33
                0x55: self._LD_I_Vx,  # Fx55
                0x65: self._LD_Vx_I  # Fx65
            }
        }

    @property
    def opcode_handler(self) -> Callable[[], None]:
        first_nibble = (self.instruction & 0xf000) >> 12
        try:
            if callable(self.opcode_table[first_nibble]):
                return self.opcode_table[first_nibble]
            elif first_nibble == 0x8:
                return self.opcode_table[first_nibble][self.n]
            else:
                return self.opcode_table[first_nibble][self.nn]
        except KeyError:
            raise UnknownInstruction(self.instruction)

    @property
    def x(self) -> int:
        return (self.instruction & 0x0f00) >> 8

    @property
    def y(self) -> int:
        return (self.instruction & 0x00f0) >> 4

    @property
    def n(self) -> int:
        return self.instruction & 0x000f

    @property
    def nn(self) -> int:
        return self.instruction & 0x00ff

    @property
    def nnn(self) -> int:
        return self.instruction & 0x0fff

    @property
    def Vx(self) -> int:
        return self.V[self.x]

    @Vx.setter
    def Vx(self, value: int):
        self.V[self.x] = value & 0xff

    @property
    def Vy(self) -> int:
        return self.V[self.y]

    def _CLS(self):  # 00E0
        for row in self.screen.buffer:
            for x, _ in enumerate(row):
                row[x] = False

    def _RET(self):  # 00EE
        self.program_counter = self.stack.pop()

    def _JP_nnn(self):  # 1nnn
        self.program_counter = self.nnn

    def _CALL_nnn(self):  # 2nnn
        self.stack.append(self.program_counter)
        self.program_counter = self.nnn

    def _SE_Vx_nn(self):  # 3xnn
        if self.Vx == self.nn:
            self.program_counter += 2

    def _SNE_Vx_nn(self):  # 4xnn
        if self.Vx != self.nn:
            self.program_counter += 2

    def _SE_Vx_Vy(self):  # 5xy0
        if self.n != 0:
            raise UnknownInstruction(self.instruction)

        if self.Vx == self.Vy:
            self.program_counter += 2

    def _LD_Vx_nn(self):  # 6xnn
        self.Vx = self.nn

    def _ADD_Vx_nn(self):  # 7xnn
        self.Vx += self.nn

    def _LD_Vx_Vy(self):  # 8xy0
        self.Vx = self.Vy

    def _OR_Vx_Vy(self):  # 8xy1
        self.Vx |= self.Vy

    def _AND_Vx_Vy(self):  # 8xy2
        self.Vx &= self.Vy

    def _XOR_Vx_Vy(self):  # 8xy3
        self.Vx ^= self.Vy

    def _ADD_Vx_Vy(self):  # 8xy4
        self.V[0xf] = 1 if self.Vx + self.Vy > 0xff else 0
        self.Vx += self.Vy

    def _SUB_Vx_Vy(self):  # 8xy5
        self.V[0xf] = 0 if self.Vy > self.Vx else 1
        self.Vx -= self.Vy

    def _SHR_Vx_Vy(self):  # 8xy6
        self.V[0xf] = self.Vy & 0b00000001
        self.Vx = self.Vy >> 1

    def _SUBN_Vx_Vy(self):  # 8xy7
        self.V[0xf] = 0 if self.Vx > self.Vy else 1
        self.Vx = self.Vy - self.Vx

    def _SHL_Vx_Vy(self):  # 8xyE
        self.V[0xf] = self.Vy >> 7
        self.Vx = self.Vy << 1

    def _SNE_Vx_Vy(self):  # 9xy0
        if self.n != 0:
            raise UnknownInstruction(self.instruction)

        if self.Vx != self.Vy:
            self.program_counter += 2

    def _LD_I_nnn(self):  # Annn
        self.I = self.nnn

    def _JP_V0_nnn(self):  # Bnnn
        self.program_counter = self.nnn + self.V[0x0]

    def _RND_Vx_nn(self):  # Cxnn
        self.Vx = random.getrandbits(8) & self.nn

    def _DRW_Vx_Vy_n(self):  # Dxyn
        self.V[0xf] = 0
        sprite = self.memory[self.I:self.I + self.n]
        for byte_number, byte in enumerate(sprite):
            y = (self.Vy + byte_number) % len(self.screen.buffer)
            row = self.screen.buffer[y]

            sprite_bits = [(byte >> bit_number) & 0b00000001 for bit_number in range(7, -1, -1)]
            for bit_number, sprite_bit in enumerate(sprite_bits):
                if not sprite_bit:
                    continue
                x = (self.Vx + bit_number) % len(row)
                if row[x]:
                    self.V[0xf] = 1
                row[x] = not row[x]
        raise UpdateScreen

    def _SKP_Vx(self):  # Ex9E
        if self.Vx in self.keyboard.pressed_keys:
            self.program_counter += 2

    def _SKNP_Vx(self):  # ExA1
        if self.Vx not in self.keyboard.pressed_keys:
            self.program_counter += 2

    def _LD_Vx_DT(self):  # Fx07
        self.Vx = self.delay_timer

    def _LD_Vx_K(self):  # Fx0A
        self.waiting_for_keypress = True
        raise WaitForKeypress

    def _LD_DT_Vx(self):  # Fx15
        self.delay_timer = self.Vx

    def _LD_ST_Vx(self):  # Fx18
        self.sound_timer = self.Vx

    def _ADD_I_Vx(self):  # Fx1E
        self.I += self.Vx
        self.I &= 0xfff

    def _LD_F_Vx(self):  # Fx29
        self.I = self.Vx * 5

    def _LD_B_Vx(self):  # Fx33
        hundreds = self.Vx // 100
        tens = (self.Vx % 100) // 10
        ones = self.Vx % 10
        self.memory[self.I] = hundreds
        self.memory[self.I + 1] = tens
        self.memory[self.I + 2] = ones

    def _LD_I_Vx(self):  # Fx55
        for reg in range(self.x + 1):
            self.memory[self.I + reg] = self.V[reg]
        self.I += self.x + 1

    def _LD_Vx_I(self):  # Fx65
        for reg in range(self.x + 1):
            self.V[reg] = self.memory[self.I + reg]
        self.I += self.x + 1


font_sprites = [
    0xf0, 0x90, 0x90, 0x90, 0xf0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xf0, 0x10, 0xf0, 0x80, 0xf0,  # 2
    0xf0, 0x10, 0xf0, 0x10, 0xf0,  # 3
    0x90, 0x90, 0xf0, 0x10, 0x10,  # 4
    0xf0, 0x80, 0xf0, 0x10, 0xf0,  # 5
    0xf0, 0x80, 0xf0, 0x90, 0xf0,  # 6
    0xf0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xf0, 0x90, 0xf0, 0x90, 0xf0,  # 8
    0xf0, 0x90, 0xf0, 0x10, 0xf0,  # 9
    0xf0, 0x90, 0xf0, 0x90, 0x90,  # A
    0xe0, 0x90, 0xe0, 0x90, 0xe0,  # B
    0xf0, 0x80, 0x80, 0x80, 0xf0,  # C
    0xe0, 0x90, 0x90, 0x90, 0xe0,  # D
    0xf0, 0x80, 0xf0, 0x80, 0xf0,  # E
    0xf0, 0x80, 0xf0, 0x80, 0x80,  # F
]


class UnknownInstruction(Exception):
    def __init__(self, instruction):
        super().__init__(f"{instruction:0{4}X}")


class UpdateScreen(Exception):
    pass


class WaitForKeypress(Exception):
    pass
