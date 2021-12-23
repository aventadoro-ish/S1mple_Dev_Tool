from dataclasses import dataclass


@dataclass()
class SubInstruction:
    """ """
    flags: list[str]
    steps: list[int]


@dataclass()
class Instruction:
    comment: str
    opcode: int
    name: str           # 'LDA'
    formula: str        # 'LDA AC #H', 'LDA #H #L', 'MOV PCL A', 'LDA #v'
    steps: list[SubInstruction]


class Microcode:
    def __init__(self):
        self.control_lines: list[tuple[str, int]] = []
        self.instructions: list[Instruction]

    def save_master_file(self, filename: str):
        # .csv-type file with first line listing control_lines values
        # second serves as headers for instruction table
        #
        pass

    def load_isa_file(self, filename: str):
        """ Loads .csv with instruction set description.
            First row is treated as header-like filters for the table:
            'name', 'opcode', 'operands', 'comment', 'flags'.
            The rest is the table itself."""
        pass

    def load_microcode_file(self, filename: str, base: int):
        """ .txt file with memory for control word rom """
        pass

    def load_descriptor_file(self, filename: str):
        """ control line grouping, control line/value pairs, flags,
            rom address-space layout """
        pass

