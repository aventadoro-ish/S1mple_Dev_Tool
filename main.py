from Microcode import Microcode


def main():
    setup_tools()



def setup_tools():
    from Microcode import text_rom_to_hex
    text_rom_to_hex('datafiles/rom.txt')

    mc = Microcode()
    mc.load_rom_file('datafiles/rom.hex')
    mc.load_control_word_layout_file('datafiles/cw_layout.txt')
    mc.export('datafiles/microcode.json')

    from Assembler import csv_isa_to_json
    csv_isa_to_json('datafiles/isa_v3.4.csv', 'datafiles/isa_v3.4.json')


if __name__ == '__main__':
    main()
