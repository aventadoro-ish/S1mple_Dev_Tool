from Microcode import Microcode


def main():
    pass


def setup_tools():
    from Microcode import text_rom_to_hex
    text_rom_to_hex('datafiles/rom.txt')

    mc = Microcode()
    mc.load_rom_file('datafiles/rom.hex')
    mc.export('datafiles/microcode.json')


if __name__ == '__main__':
    main()
