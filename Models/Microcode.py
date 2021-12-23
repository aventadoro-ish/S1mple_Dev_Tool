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
    name: str
    formula: str
    steps: list[SubInstruction]


class Microcode:
    def __init__(self):
        self.control_lines: list[tuple(str, int)] = []
        self.instructions: list[Instruction]

    def save_microcode_file(self, filename: str):
        pass
