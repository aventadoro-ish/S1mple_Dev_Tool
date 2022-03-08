from intelhex import IntelHex
import json


class Microcode:
    def __init__(self):
        self.microcode: IntelHex = None

    def load_rom_file(self, filename: str = None):
        if filename is None:
            filename = 'rom.hex'

        if not filename.endswith('.hex'):
            filename += '.hex'

        self.microcode = IntelHex(filename)

    def export(self, filename: str = None) -> None:
        if filename is None:
            filename = 'microcode.json'

        if not filename.endswith('.json'):
            filename += '.json'


def text_rom_to_hex(txt_filename: str = None, hex_filename: str = None):
    """Convert .txt rom dump to .hex"""
    if txt_filename is None:
        txt_filename = 'rom.txt'

    if not txt_filename.endswith('.txt'):
        txt_filename += '.txt'

    if hex_filename is None:
        hex_filename = txt_filename.strip('.txt') + '.hex'

    ih = IntelHex()

    with open(txt_filename, 'r') as file:
        idx: int = 0
        for line in file:
            for byte in line.split():
                ih[idx] = int(byte)
                idx += 1

    # with open(hex_filename, 'w+') as file:
    ih.write_hex_file(hex_filename)
