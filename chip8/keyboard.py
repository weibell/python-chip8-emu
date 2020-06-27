from typing import Set, Union

import pygame

KEY_MAPPING = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xc,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xd,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xe,
    pygame.K_z: 0xa, pygame.K_x: 0x0, pygame.K_c: 0xb, pygame.K_v: 0xf
}


class Keyboard:
    pressed_keys: Set[int]

    def __init__(self):
        self.pressed_keys = set()

    def keydown(self, event):
        if event.key in KEY_MAPPING:
            self.pressed_keys.add(KEY_MAPPING[event.key])

    def keyup(self, event) -> Union[int, None]:
        if event.key in KEY_MAPPING:
            self.pressed_keys.discard(KEY_MAPPING[event.key])
            return KEY_MAPPING[event.key]
        else:
            return None
