from argparse import ArgumentParser

from chip8.chip8 import Chip8


def main():
    parser = ArgumentParser(description="CHIP-8 interpreter written in Python")
    parser.add_argument("rom", type=str, help="ROM file")
    parser.add_argument("--cpu-frequency", type=int, default=250, help="CPU frequency in Hz")
    parser.add_argument("--scaling-factor", type=int, default=8, help="Integer scaling factor")
    parser.add_argument("--starting-address", type=lambda x: int(x, 0), default=0x200, help="Starting address")
    args = parser.parse_args()

    with open(args.rom, "rb") as f:
        rom = f.read()
    chip8 = Chip8(args.cpu_frequency, args.scaling_factor, args.starting_address)
    chip8.load(rom)
    chip8.run()


if __name__ == "__main__":
    main()
