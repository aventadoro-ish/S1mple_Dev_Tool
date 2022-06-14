import json
import re
import string
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

    def identify(self, name: str, pattern: str) -> int:
        return self.fast_id_dict[f'{name} {pattern}']

    def __getitem__(self, item):
        if type(item) is not int:
            raise Exception('Non-int key given to get Instruction from ISA.'
                            'Integer opcode expected!')

        for idx, inst in enumerate(self.instructions):
            if inst.opcode == item:
                return self.instructions[idx]

        raise KeyError(f'Unable to find Instruction with opcode {item} '
                       f'in the ISA.')

    def printout(self):
        for inst in self.instructions:
            print(inst)


class LineType(Enum):
    COMMENT = auto()
    INSTRUCTION = auto()
    EMPTY = auto()
    ASM_CMD = auto()
    LABEL = auto()
    DATA = auto()


class AddrMode(Enum):
    #     - no prefix                   -> no mode,
    #     - prefix #                    -> immediate mode, load this value
    #     - prefix @                    -> absolute mode, load from address
    #     - prefix $ and , REG notation -> relative mode, address high byte + REG

    NO_MODE = auto()
    IMMEDIATE = auto()
    RELATIVE = auto()
    ABSOLUTE = auto()
    REGISTERS = auto()
    IMM_ABS = auto()


class AsmDataTypes(Enum):
    STRING = 'ds'
    BYTE = 'db'
    BYTE_ARRAY = 'dba'

    # TODO: pointers as data

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Line:
    ISA_: ISA = None

    def __init__(self, line: str | None = None):
        self.type_ = None  # LineType.COMMENT
        self.addr_mode = None
        self.data_type = None
        self.has_comment = False
        self.line = line
        self.tokens: list[str] = []

        if line is not None:
            self.process()

    def process(self):
        # TODO: I think I had a better tokenizer somewhere
        self.tokens = self.line.split()

        self.type_ = self.determine_type()

        if self.type_ is LineType.INSTRUCTION:
            self.addr_mode = self.determine_addr_mode()

        elif self.type_ is LineType.DATA:
            self.data_type = self.determine_data_type()

        if ';' in self.line:
            self.has_comment = True

    def determine_data_type(self) -> AsmDataTypes:
        return AsmDataTypes(self.tokens[0])

    def determine_type(self) -> LineType:
        if self.line is None:
            print(f"*Line: Unable to determine line type. self.line is None!")
            raise Exception(f"*Line: Unable to determine line type. self.line is None!")

        if self.line.strip().startswith(';'):
            return LineType.COMMENT

        if len(self.line) == 0:
            return LineType.EMPTY

        if self.tokens[0] == '.org':
            return LineType.ASM_CMD

        if self.tokens[0].endswith(':'):
            return LineType.LABEL

        if self.tokens[0] in self.ISA_.valid_words:
            return LineType.INSTRUCTION

        if AsmDataTypes.has_value(self.tokens[0]):
            return LineType.DATA

        print(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")
        raise Exception(f"*Line: Unable to determine line type. Unknown type! \"{self.line}\"")

    def determine_addr_mode(self) -> AddrMode:
        if self.line is None:
            print(f"*Line: Unable to determine addressing mode. self.line is None!")
            raise Exception(f"*Line: Unable to determine addressing mode. self.line is None!")

        if self.line_contains_special_operand() and '$' in self.line:
            return AddrMode.RELATIVE
        if '#' in self.line and '@' in self.line:
            return AddrMode.IMM_ABS

        if self.line_contains_special_operand():
            return AddrMode.REGISTERS
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

    def get_non_comment_tokens(self) -> list[str]:
        if self.has_comment:
            # TODO: this won't work with comments like ';comment'
            n_inst_tokens = self.tokens.index(';')
        else:
            n_inst_tokens = len(self.tokens)

        return self.tokens[:n_inst_tokens]

    def get_instruction_pattern(self) -> str:
        if self.type_ is not LineType.INSTRUCTION:
            raise Exception(f'Trying to get instruction pattern form line of type '
                            f'{self.type_}.')

        pattern = []
        for token in self.get_non_comment_tokens():
            if token in self.ISA_.special_ops:
                pattern.append(token)
            elif token.startswith('@'):
                pattern.append('# #')
            elif token.startswith(('$', '#')):
                pattern.append('#')

        return ' '.join(pattern)

    def get_string_data(self) -> str:
        if self.data_type is not AsmDataTypes.STRING:
            raise Exception(f'trying to extract string data from line with '
                            f'type {self.type_} {self.data_type}. '
                            f'{LineType.DATA} {AsmDataTypes.STRING} expected!')

        idx1 = self.line.index('"') + 1
        idx2 = self.line.index('"', idx1)
        # print(self.line[idx1:idx2])
        return self.line[idx1:idx2] + '\0'

    def __repr__(self):
        if self.type_ is LineType.INSTRUCTION:
            return f'Line("{self.line}", type={self.type_},' \
                   f' addr_mode={self.addr_mode}, {self.has_comment=})'

        if self.type_ is LineType.DATA:
            return f'Line("{self.line}", type={self.type_},' \
                   f' data_type={self.data_type}, {self.has_comment=})'

        if self.type_ is LineType.COMMENT:
            return f'Line("{self.line}", type={self.type_})'

        return f'Line("{self.line}", type={self.type_},' \
               f' {self.has_comment=})'


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
    _is_finalized: bool = False

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, a):
        # TODO address validation
        self._address = a
        if type(self.address) is int:
            self._is_finalized = True

    @property
    def is_finalized(self):
        return self._is_finalized

    @staticmethod
    def from_line(line: Line, address: int | None = None):
        name = line.line.split()[0].strip(':')
        return AsmTypesLabel(name, address)

    def __str__(self):
        return f'Label({self.name} -> {self._address})'


class AsmTableLabels:
    def __init__(self):
        self.labels: list[AsmTypesLabel] = []

    def __getitem__(self, item) -> AsmTypesLabel:
        if type(item) is int:
            return self._idx_lookup_(item)

        if type(item) is str:
            return self._name_lookup_(item)

        raise Exception(f'')

    def _idx_lookup_(self, idx) -> AsmTypesLabel:
        return self.labels[idx]

    def _name_lookup_(self, name) -> AsmTypesLabel:
        for idx, label in enumerate(self.labels):
            if name == label.name:
                return self.labels[idx]

        self.labels.append(AsmTypesLabel(name, None))
        return self.labels[-1]

    def fully_finalized(self) -> bool:
        for label in self.labels:
            if not label.is_finalized:
                return False

        return True

    def printout(self):
        for label in self.labels:
            print(label)


class Assembler:
    DEFAULT_PADDING = 0

    def __init__(self, filename: str, isa: ISA):
        Line.ISA_ = isa
        self.isa = isa
        with open(filename, 'r') as prog:
            self.input_text = ''.join(prog.readlines())

        # TODO: this is not very memory efficient, but 0.26 MB is not much
        self.intermediate_code = [None] * 2**15

        self.labels = AsmTableLabels()

        self.pass1()

        print()
        self.pretty_printout()
        print()
        self.labels.printout()
        print(f'Label finalization: {self.labels.fully_finalized()}')

        self.pass2()

    def pass1(self):
        pc = 0

        for line in AsmLineIterator(self.input_text):
            if line.type_ in (LineType.EMPTY, LineType.COMMENT):
                continue

            print(repr(line))
            # TODO: code cleanup here

            if line.type_ is LineType.ASM_CMD:
                # TODO: better organisation for assembler directives
                if line.tokens[0] == '.org':
                    pc = int(line.tokens[1], 16)
                    print(pc)

            elif line.type_ is LineType.INSTRUCTION:
                opcode = self.isa.identify(
                    name=line.tokens[0],
                    pattern=line.get_instruction_pattern()
                )

                instruction = self.isa[opcode]

                snippet = [x for x in line.get_non_comment_tokens() if x not in self.isa.special_ops]
                snippet[0] = opcode

                for byte in snippet[1:]:
                    if re.match(r'\b[0123456789abcdef].[0123456789abcdef]+',
                                byte.strip('@#$')):
                        # TODO: convert to int explicit values
                        pass

                self._protected_intermediate_modification_(pc, snippet)
                pc += instruction.n_byte_ops + 1

                print(instruction, 'bytes len =', instruction.n_byte_ops + 1, '; pc = ', pc)

            elif line.type_ is LineType.DATA:
                if line.data_type is AsmDataTypes.BYTE:
                    snippet = (int(line.tokens[1], 16), )

                elif line.data_type is AsmDataTypes.STRING:
                    # TODO: string literals support
                    string_ = line.get_string_data()
                    snippet = string_.encode('ascii')
                    print(snippet)

                elif line.data_type is AsmDataTypes.BYTE_ARRAY:
                    snippet = line.get_non_comment_tokens()[1:]
                    snippet = [int(x.strip(','), 16) for x in snippet]

                self._protected_intermediate_modification_(pc, snippet)

                data_len = self._get_data_len(line)
                pc += data_len

                print(f'data line: {line.line} of length '
                      f'{data_len}, new {pc=}')

            elif line.type_ is LineType.LABEL:
                label = AsmTypesLabel.from_line(line, pc)
                self.labels[label.name].address = pc

            print()

    @staticmethod
    def _get_data_len(line: Line) -> int:
        if line.data_type is AsmDataTypes.BYTE:
            return 1

        if line.data_type is AsmDataTypes.STRING:
            # TODO: string literals support
            # + 1 is a Null-terminator
            return len(line.get_string_data())

        if line.data_type is AsmDataTypes.BYTE_ARRAY:
            return len(line.get_non_comment_tokens()) - 1

    def _protected_intermediate_modification_(self,
                                              start_addr: int,
                                              insert_list: list[int | str | None]):
        for addr in range(start_addr, start_addr+len(insert_list)):
            if self.intermediate_code[addr] is not None:
                # TODO: more info for debugging
                raise Exception(f'Collision of data at address {addr}')

            idx = addr - start_addr
            self.intermediate_code[addr] = insert_list[idx]

            # print('*', insert_list[idx], self.intermediate_code[addr],
            #       type(self.intermediate_code[addr]))

    def pretty_printout(self):
        for address in range(0, 2**15, 16):
            snippet = self.intermediate_code[address:address+15]
            if any([True for x in snippet if x is not None]):
                snippet_str = ''
                ascii_repr = ''

                for x in snippet:
                    if type(x) is int:
                        snippet_str += f'{x:0>2x} '
                        if chr(x) in string.printable and x != 9:
                            ascii_repr += chr(x)
                        else:
                            ascii_repr += '.'

                    elif x is None:
                        snippet_str += f'{Assembler.DEFAULT_PADDING:0>2x} '
                        ascii_repr += '.'

                    else:
                        snippet_str += str(x)[0:2] + ' '
                        ascii_repr += '.'

                print(f'{address:0>4x}\t{snippet_str}\t[{ascii_repr}]')

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


