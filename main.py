from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from chip8.chip8 import Chip8


def main():
    # noinspection PyTypeChecker
    parser = ArgumentParser(description="CHIP-8 interpreter", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("rom", type=str, help="ROM file")
    parser.add_argument("--scaling-factor", metavar='n', type=int, default=8, help="Screen scaling factor")
    parser.add_argument("--cycles-per-frame", metavar='n', type=int, default=10,
                        help="CPU cycles per frame (at 60 fps)")
    parser.add_argument("--starting-address", metavar='n', type=lambda x: int(x, 0), default=0x200,
                        help="Starting address")
    args = parser.parse_args()

    with open(args.rom, "rb") as f:
        rom = f.read()
    chip8 = Chip8(args.scaling_factor, args.cycles_per_frame, args.starting_address)
    chip8.load(rom)
    chip8.run()


if __name__ == "__main__":
    main()
