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
        self.I = 0x0000
        self.delay_timer = 0x00
        self.sound_timer = 0x00
        self.instruction = 0x0000

        self.opcode_table = self._build_opcode_table()

    def load(self, rom: bytes) -> None:
        self.memory[self.starting_address:self.starting_address + len(rom)] = rom

    def cpu_tick(self) -> None:
        if self.waiting_for_keypress:
            return

        self.instruction = self.memory[self.program_counter] << 8 | self.memory[self.program_counter + 1]
        self.program_counter += 2
        self.opcode_handler()

    def sixty_hertz_tick(self):
        if self.waiting_for_keypress:
            return

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
                0xe0: self._CLS,
                0xee: self._RET
            },
            0x1: self._JP_nnn,
            0x2: self._CALL_nnn,
            0x3: self._SE_Vx_nn,
            0x4: self._SNE_Vx_nn,
            0x5: self._SE_Vx_Vy,
            0x6: self._LD_Vx_nn,
            0x7: self._ADD_Vx_nn,
            0x8: {
                0x0: self._LD_Vx_Vy,
                0x1: self._OR_Vx_Vy,
                0x2: self._AND_Vx_Vy,
                0x3: self._XOR_Vx_Vy,
                0x4: self._ADD_Vx_Vy,
                0x5: self._SUB_Vx_Vy,
                0x6: self._SHR_Vx,
                0x7: self._SUBN_Vx_Vy,
                0xe: self._SHL_Vx
            },
            0x9: self._SNE_Vx_Vy,
            0xa: self._LD_I_nnn,
            0xb: self._JP_V0_nnn,
            0xc: self._RND_Vx_nn,
            0xd: self._DRW_Vx_Vy_n,
            0xe: {
                0x9e: self._SKP_Vx,
                0xa1: self._SKNP_Vx
            },
            0xf: {
                0x07: self._LD_Vx_DT,
                0x0a: self._LD_Vx_K,
                0x15: self._LD_DT_Vx,
                0x18: self._LD_ST_Vx,
                0x1e: self._ADD_I_Vx,
                0x29: self._LD_F_Vx,
                0x33: self._LD_B_Vx,
                0x55: self._LD_I_Vx,
                0x65: self._LD_Vx_I
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
            raise UnknownInstruction(f"{self.instruction:#0{6}x}")

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
    def Vx(self, value: int) -> None:
        self.V[self.x] = value & 0xff

    @property
    def Vy(self) -> int:
        return self.V[self.y]

    @Vy.setter
    def Vy(self, value: int) -> None:
        self.V[self.y] = value & 0xff

    def _CLS(self) -> None:
        for row in self.screen.screen_buffer:
            for x, _ in enumerate(row):
                row[x] = False

    def _RET(self) -> None:
        self.program_counter = self.stack.pop()

    def _JP_nnn(self) -> None:
        self.program_counter = self.nnn

    def _CALL_nnn(self) -> None:
        self.stack.append(self.program_counter)
        self.program_counter = self.nnn

    def _SE_Vx_nn(self) -> None:
        if self.Vx == self.nn:
            self.program_counter += 2

    def _SNE_Vx_nn(self) -> None:
        if self.Vx != self.nn:
            self.program_counter += 2

    def _SE_Vx_Vy(self) -> None:
        if self.Vx == self.Vy:
            self.program_counter += 2

    def _LD_Vx_nn(self) -> None:
        self.Vx = self.nn

    def _ADD_Vx_nn(self) -> None:
        self.Vx += self.nn

    def _LD_Vx_Vy(self) -> None:
        self.Vx = self.Vy

    def _OR_Vx_Vy(self) -> None:
        self.Vx |= self.Vy

    def _AND_Vx_Vy(self) -> None:
        self.Vx &= self.Vy

    def _XOR_Vx_Vy(self) -> None:
        self.Vx ^= self.Vy

    def _ADD_Vx_Vy(self) -> None:
        self.V[0xf] = 1 if self.Vx + self.Vy > 0xff else 0
        self.Vx += self.Vy

    def _SUB_Vx_Vy(self) -> None:
        self.V[0xf] = 0 if self.Vy > self.Vx else 1
        self.Vx -= self.Vy

    def _SHR_Vx(self) -> None:
        self.V[0xf] = self.Vx & 0b00000001
        self.Vx >>= 1

    def _SUBN_Vx_Vy(self) -> None:
        self.V[0xf] = 0 if self.Vx > self.Vy else 1
        self.Vx = self.Vy - self.Vx

    def _SHL_Vx(self) -> None:
        self.V[0xf] = (self.Vx & 0b10000000) >> 7
        self.Vx <<= 1

    def _SNE_Vx_Vy(self) -> None:
        if self.Vx != self.Vy:
            self.program_counter += 2

    def _LD_I_nnn(self) -> None:
        self.I = self.nnn

    def _JP_V0_nnn(self) -> None:
        self.program_counter = self.nnn + self.V[0x0]

    def _RND_Vx_nn(self) -> None:
        self.Vx = random.getrandbits(8) & self.nn

    def _DRW_Vx_Vy_n(self) -> None:
        self.V[0xf] = 0
        sprite = self.memory[self.I:self.I + self.n]
        for byte_number, byte in enumerate(sprite):
            y = (self.Vy + byte_number) % len(self.screen.screen_buffer)
            row = self.screen.screen_buffer[y]

            sprite_bits = [(byte >> bit_number) & 0b00000001 for bit_number in range(7, -1, -1)]
            for bit_number, sprite_bit in enumerate(sprite_bits):
                if not sprite_bit:
                    continue
                x = (self.Vx + bit_number) % len(row)
                if row[x]:
                    self.V[0xf] = 1
                row[x] = not row[x]
        raise UpdateScreen

    def _SKP_Vx(self) -> None:
        if self.Vx in self.keyboard.pressed_keys:
            self.program_counter += 2

    def _SKNP_Vx(self) -> None:
        if self.Vx not in self.keyboard.pressed_keys:
            self.program_counter += 2

    def _LD_Vx_DT(self) -> None:
        self.Vx = self.delay_timer

    def _LD_Vx_K(self) -> None:
        self.waiting_for_keypress = True
        raise WaitForKeypress

    def _LD_DT_Vx(self) -> None:
        self.delay_timer = self.Vx

    def _LD_ST_Vx(self) -> None:
        self.sound_timer = self.Vx

    def _ADD_I_Vx(self) -> None:
        self.I += self.Vx
        self.I &= 0xffff  # TODO

    def _LD_F_Vx(self) -> None:
        self.I = self.Vx * 5

    def _LD_B_Vx(self) -> None:
        hundreds = self.Vx // 100
        tens = (self.Vx % 100) // 10
        ones = self.Vx % 10
        self.memory[self.I] = hundreds
        self.memory[self.I + 1] = tens
        self.memory[self.I + 2] = ones

    def _LD_I_Vx(self) -> None:
        for reg in range(self.x + 1):
            self.memory[self.I + reg] = self.V[reg]

    def _LD_Vx_I(self) -> None:
        for reg in range(self.x + 1):
            self.V[reg] = self.memory[self.I + reg]


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
    pass


class UpdateScreen(Exception):
    pass


class WaitForKeypress(Exception):
    pass
