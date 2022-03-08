import jsbeautifier as jsbeautifier
from intelhex import IntelHex
import json


class Microcode:
    def __init__(self):
        self.rom: IntelHex = None

    def load_rom_file(self, filename: str = None):
        if filename is None:
            filename = 'rom.hex'

        if not filename.endswith('.hex'):
            filename += '.hex'

        self.rom = IntelHex(filename)

    def export(self, filename: str = None) -> None:
        if filename is None:
            filename = 'rom.json'

        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w+') as file:
            # TODO:  self.rom.tobinarray().tolist() kinda memory-inefficient.
            #  Find a way to serialize array to JSON
            microcode_json = {'rom': self.rom.tobinarray().tolist()}

            beautifier_options = jsbeautifier.default_options()
            beautifier_options.indent_size = 2
            beautifier_options.wrap_line_length = 120

            file.write(jsbeautifier.beautify(json.dumps(microcode_json), beautifier_options))


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

    ih.write_hex_file(hex_filename)
