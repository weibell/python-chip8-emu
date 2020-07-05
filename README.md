# python-chip8-emu
[![codecov](https://codecov.io/gh/weibell/python-chip8-emu/branch/master/graph/badge.svg)](https://codecov.io/gh/weibell/python-chip8-emu)

[CHIP-8](https://en.wikipedia.org/wiki/CHIP-8) emulation in Python


<div align="center">
    <img src="images/screenshot_logo.png?raw=true">
</div>


#### Introduction
This interpreter aims to be compatible with the original CHIP-8 instruction set for the COSMAC VIP with no extensions, with the exception of the `0nnn` instruction to execute a machine language subroutine.
In total, 34 opcodes are supported.
It was tested on Python 3.8 using [pygame 2.0.0.dev10](https://pypi.org/project/pygame/2.0.0.dev10/).

#### Usage
```commandline
$ python3 main.py -h
usage: main.py [-h] [--scaling-factor n] [--cycles-per-frame n] [--starting-address n] rom

CHIP-8 interpreter

positional arguments:
  rom                   ROM file

optional arguments:
  -h, --help            show this help message and exit
  --scaling-factor n    Screen scaling factor (default: 8)
  --cycles-per-frame n  CPU cycles per frame (at 60 fps) (default: 10)
  --starting-address n  Starting address (default: 512)
```

The following keyboard mapping is used:

```
Keyboard:    CHIP-8:

1 2 3 4      1 2 3 C
Q W E R      4 5 6 D
A S D F      7 8 9 E
Z X C V      A 0 B F
```


#### Screenshots

```commandline
$ python3 main.py "roms/games/Pong (alt).ch8"
```
<div align="center">
    <img src="images/screenshot_pong.png?raw=true">
</div>
<br>

```commandline
$ python3 main.py "roms/games/Tetris [Fran Dachille, 1991].ch8"
```
<div align="center">
    <img src="images/screenshot_tetris.png?raw=true">
</div>
<br>


[test_opcode.ch8](https://github.com/corax89/chip8-test-rom) results:
<div align="center">
    <img src="images/screenshot_test_opcode.png?raw=true">
</div>



#### Resources
Opcode descriptions for method names are based on [Cowgod's technical reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM).
Since this includes a few errors (for example with the description of opcodes `8xy6`, `8xyE`, `Fx55` and `Fx65`), [Matthew Mikolay's instruction set table](https://github.com/mattmikolay/chip-8/wiki/CHIP%E2%80%908-Instruction-Set) and [chip-8.github.io](https://chip-8.github.io/extensions/#chip-8) were used as the primary sources for the technical implementation.