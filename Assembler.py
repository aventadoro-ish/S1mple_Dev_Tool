import json
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache
from typing import Iterator


class AssemblyError(Exception):
    pass


@dataclass
class Instruction:
    opcode: int
    name: str
    n_byte_ops: int
    operand_order: str

    def __str__(self):
        return f'Instruction({self.name}, {self.opcode} "{self.operand_order}")'

    def to_json(self):
        return {'name': self.name, 'opcode': self.opcode,
                'pattern': self.operand_order, '# byte ops': self.n_byte_ops}


class ISA:
    def __init__(self, json_isa: dict):
        # {id_str: opcode}
        # {'NOP 0 ': 0, ... 'MOV 0 AC R': 19...}
        self.fast_id_dict: dict[str: int] = {}

        # {opcode, (name, nob, nso, comment}
        self.descriptive_dict: dict[int: tuple] = {}

        # (NOP, LDR, PSR ...)
        self.valid_words: tuple = ()
        valid_words_temp = []

        for opcode, item in json_isa.items():
            name = item['name']
            n_byte_operands = item['n_byte_operands']
            special_operands = item['special_operands']

            comment = item['comment']

            id_str = f'{name} {special_operands}'
            self.fast_id_dict[id_str] = int(opcode)

            self.descriptive_dict[int(opcode)] = (name, n_byte_operands,
                                                  special_operands, comment)
            if name not in valid_words_temp:
                valid_words_temp.append(name)

        self.valid_words: set[str] = set(valid_words_temp)

    @cache
    def identify(self, name: str, addressing_mode_prefix: str, special_operands: str) -> int:
        """
        Get instruction opcode
        :param name: Assembly-name
        :type name: str
        :param addressing_mode_prefix: '', '#', '@', '$', '@#'
        :type addressing_mode_prefix: str
        :param special_operands: what special operands were used
        :type special_operands: str
        :return: instruction opcode
        :rtype: int
        """
        id_str = f'{name} {addressing_mode_prefix} {special_operands}'
        try:
            return self.fast_id_dict[id_str]
        except KeyError:
            raise AssemblyError('ERROR! Could not identify instruction: '
                                f'{name=}, {addressing_mode_prefix=}, {special_operands=}.')


class Configuration(ISA):
    # TODO: add more optional data: address space size, rom and ram address bounds
    def __init__(self):
        with open('config.json', 'r') as file:
            config = json.load(file)

            self.special_operands: tuple[str] = (config['special_operands'])
            # self.addressing_modes = AddressingModes(config['addressing_modes'])
            self.isa = ISA(config['ISA'], self.addressing_modes)


class LineType(Enum):
    COMMENT = auto()
    INSTRUCTION = auto()
    EMPTY = auto()
    ASM_CMD = auto()
    LABELED_INSTRUCTION = auto()
    LABEL = auto()


class AddrMode(Enum):
    #     - no prefix                   -> no mode,
    #     - prefix #                    -> immediate mode, load this value
    #     - prefix @                    -> absolute mode, load from address
    #     - prefix $ and , REG notation -> relative mode, address high byte + REG

    NO_MODE = auto()
    IMMEDIATE = auto()
    RELATIVE = auto()
    ABSOLUTE = auto()
    IMM_ABS = auto()


class Line:
    CONFIG: Configuration = 'todo config'

    def __init__(self, line: str | None = None):
        self.type_ = None  # LineType.COMMENT
        self.addr_mode = None
        self.has_comment = False
        self.line = line

        if line is not None:
            self.process()

    def process(self):
        self.determine_type()

        if self.type_ in (LineType.INSTRUCTION, LineType.LABELED_INSTRUCTION):
            self.determine_addr_mode()

        if ';' in self.line:
            self.has_comment = True

    def determine_type(self):
        if self.line is None:
            print(f"*Line: Unable to determine line type. self.line is None!")
            raise Exception(f"*Line: Unable to determine line type. self.line is None!")

        if self.line.strip().startswith(';'):
            self.type_ = LineType.COMMENT
            return

        if len(self.line) == 0:
            self.type_ = LineType.EMPTY
            return

        # TODO: I think I had a better tokenizer somewhere
        tokens = self.line.split()

        # TODO: why doesn't self.CONFIG.valid_words work? fix.
        if tokens[0] in self.CONFIG.isa.valid_words:
            self.type_ = LineType.INSTRUCTION
            return

        if tokens[0] == '.PC:':
            self.type_ = LineType.ASM_CMD
            return

        if tokens[0].endswith(':') and tokens[1] in self.CONFIG.isa.valid_words:
            self.type_ = LineType.LABELED_INSTRUCTION
            return

        print(tokens)

        print(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")
        raise Exception(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")

    def determine_addr_mode(self):
        if self.line is None:
            print(f"*Line: Unable to determine addressing mode. self.line is None!")
            raise Exception(f"*Line: Unable to determine addressing mode. self.line is None!")

        # TODO: the following if-elif chain does not handle ambitious addr_mode. fix it!

        # TODO: change to registers listed in the config
        if any([x in self.line.split() for x in self.CONFIG.special_operands]):
            self.addr_mode = AddrMode.RELATIVE

        elif '#' in self.line:
            self.addr_mode = AddrMode.IMMEDIATE

        elif '@' in self.line:
            self.addr_mode = AddrMode.ABSOLUTE

        else:
            self.addr_mode = AddrMode.NO_MODE

    def pprint(self):
        print(f'Line("{self.line}", type={self.type_}, addr_mode={self.addr_mode}, {self.has_comment=})')


class LineProcessor:
    def __init__(self, prog_text: str):
        self.prog_text = prog_text
        self.line_buf = ''
        self._char_idx = 0

    def __iter__(self) -> Iterator[Line]:
        self.line_buf = ''
        self._char_idx = 0
        return self

    def __next__(self) -> Line:
        # TODO: this exit condition requires the program to end with an empty line
        while self._char_idx < len(self.prog_text):
            char = self.prog_text[self._char_idx]

            prev_char = ''
            if self._char_idx > 1:
                prev_char = self.prog_text[self._char_idx - 1]

            self._char_idx += 1

            if prev_char == '\\' and char == '\n':
                continue

            self.line_buf += char

            if char == '\n':
                copy = self.line_buf[:-1]
                self.line_buf = ''

                return Line(copy)

        raise StopIteration


def csv_isa_to_json(csv_filename: str | None = None, json_filename: str | None = None,
                    name_col=2, opcode_col=0, n_byte_ops_col=4, special_ops_col=5,
                    skip_header=1) -> None:
    """
    Converts the table with the instruction set to the json format used in by rest of the tools

    :param csv_filename:
    :type csv_filename: str or None
    :param json_filename:
    :type json_filename: str or None
    :param skip_header:
    :type skip_header:
    :param special_ops_col:
    :type special_ops_col:
    :param n_byte_ops_col:
    :type n_byte_ops_col:
    :param opcode_col:
    :type opcode_col:
    :param name_col:
    :type name_col:
    :return:
    :rtype: None
    """
    import csv

    isa = []

    with open(csv_filename, 'r') as file:
        csv_reader = csv.reader(file)

        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            inst = Instruction(int(row[opcode_col]), row[name_col],
                               int(row[n_byte_ops_col]), row[special_ops_col])

            isa.append(inst.to_json())

    with open(json_filename, 'w') as file:
        import jsbeautifier
        beautifier_options = jsbeautifier.default_options()
        beautifier_options.indent_size = 2

        file.write(jsbeautifier.beautify(json.dumps(isa), beautifier_options))


