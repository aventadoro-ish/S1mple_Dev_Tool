import json
import re
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
        return f'Instruction({self.name}, {self.opcode}, "{self.operand_order}")'

    def to_json(self):
        return {'name': self.name, 'opcode': self.opcode,
                'pattern': self.operand_order, '# byte ops': self.n_byte_ops}


class ISA:
    def __init__(self, json_isa: dict):
        # {id_str: opcode}
        # {'NOP 0 ': 0, ... 'MOV 0 AC R': 19...}
        self.fast_id_dict: dict[str: int] = {}

        self.instructions: list[Instruction] = []

        # (NOP, LDR, PSR ...)
        self.valid_words: tuple = ()
        valid_words_temp = []

        self.special_ops = []

        for item in json_isa:
            name: str = item['name']
            n_byte_ops: int = int(item['# byte ops'])
            pattern: str = item['pattern']
            opcode = int(item['opcode'])

            for operand in pattern.split():
                if operand.startswith('#'):
                    pattern = pattern.replace(operand, '#')
                    continue

                if operand not in self.special_ops:
                    self.special_ops.append(operand)

            id_str = f'{name} {pattern}'
            self.fast_id_dict[id_str] = opcode

            self.instructions.append(Instruction(
                opcode, name, n_byte_ops, pattern
            ))

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

    def printout(self):
        for inst in self.instructions:
            print(inst)


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
    ISA_: ISA = None

    def __init__(self, line: str | None = None):
        self.type_ = None  # LineType.COMMENT
        self.addr_mode = None
        self.has_comment = False
        self.line = line

        if line is not None:
            self.process()

    def process(self):
        self.type_ = self.determine_type()

        if self.type_ in (LineType.INSTRUCTION, LineType.LABELED_INSTRUCTION):
            self.addr_mode = self.determine_addr_mode()

        if ';' in self.line:
            self.has_comment = True

    def determine_type(self) -> LineType:
        if self.line is None:
            print(f"*Line: Unable to determine line type. self.line is None!")
            raise Exception(f"*Line: Unable to determine line type. self.line is None!")

        if self.line.strip().startswith(';'):
            return LineType.COMMENT

        if len(self.line) == 0:
            return LineType.EMPTY

        # TODO: I think I had a better tokenizer somewhere
        tokens = self.line.split()

        if tokens[0] == '.org':
            return LineType.ASM_CMD

        if tokens[0].endswith(':'):
            return LineType.LABEL

        if tokens[0].endswith(':') and tokens[1] in self.ISA_.valid_words:
            return LineType.LABELED_INSTRUCTION

        # TODO: why doesn't self.CONFIG.valid_words work? fix.
        if tokens[0] in self.ISA_.valid_words:
            return LineType.INSTRUCTION

        print(tokens)

        print(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")
        raise Exception(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")

    def determine_addr_mode(self) -> AddrMode:
        if self.line is None:
            print(f"*Line: Unable to determine addressing mode. self.line is None!")
            raise Exception(f"*Line: Unable to determine addressing mode. self.line is None!")

        # TODO: the following if-elif chain does not handle ambitious addr_mode. fix it!

        if self.line_contains_special_operand():
            return AddrMode.RELATIVE

        if '#' in self.line:
            return AddrMode.IMMEDIATE

        if '@' in self.line:
            return AddrMode.ABSOLUTE

        return AddrMode.NO_MODE

    def line_contains_special_operand(self):
        tokens = self.line.split()

        for token in tokens[:-1]:
            if token in self.ISA_.special_ops:
                return True

        return False

    def __repr__(self):
        return f'Line("{self.line}", type={self.type_},' \
               f' addr_mode={self.addr_mode}, {self.has_comment=})'


class AsmLineIterator:
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
            self.line_buf += char
            self._char_idx += 1

            if self.line_buf.endswith(('\\\r\n', '\\\n')):
                self.line_buf = self.line_buf.replace('\\\r\n', '')
                self.line_buf = self.line_buf.replace('\\\n', '')
                continue

            if self.line_buf.endswith(('\r\n', '\n')):
                copy = self.line_buf.strip('\r\n')
                self.line_buf = ''
                # print(copy)
                return Line(copy)

        raise StopIteration


@dataclass
class AsmTypesLabel:
    name: str
    _address: int

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, a):
        # TODO address validation
        self._address = a


class Assembler:
    def __init__(self, filename: str, isa: ISA):
        Line.ISA_ = isa

        with open(filename, 'r') as prog:
            self.input_text = ''.join(prog.readlines())
        # print(self.input_text)

        self.labels: list[AsmTypesLabel] = []

        self.pass1()
        self.pass2()

    def pass1(self):
        pc = 0

        for line in AsmLineIterator(self.input_text):
            print(repr(line))
            tokens = line.line.split()

            if line.type_ == LineType.ASM_CMD:
                if tokens[0] == '.org':
                    pc = int(tokens[1], 16)
                    print(pc)

            if line.type_ in (LineType.INSTRUCTION, LineType.LABELED_INSTRUCTION):
                print(pc)
                pc += 1

            if line.type_ in (LineType.LABEL, LineType.LABELED_INSTRUCTION):
                pass

    def pass2(self):
        pass


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

        for x in range(skip_header):
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


