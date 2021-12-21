from enum import Enum
from dataclasses import dataclass


@dataclass
class QueueEntry:
    active_tab: str
    element: str
    data: str


class EnumStr(str, Enum):   # TODO: how does adding 'str' fixes my problem?
    def __str__(self):
        return self.value


class Tabs(EnumStr):
    ASSEMBLER = 'Assembler'
    SOFT_EMU = 'Software Emulator'
    HARD_EMU = 'Hardware Emulator'
    MICROCODE = 'Microcode'
    EEPROM = 'EEPROM'


class AsmElements(EnumStr):
    FILENAME = '-asm_filename-'
    FB = '-asm_fb-'
    SAVE_BTN = '-asm_save_btn-'
    INP_MULTILINE = '-asm_inp-'
    OUT_MULTILINE = '-asm_out-'


class SEmuElements(EnumStr):
    LOAD_ASM_PROG = '-s_emu_ld_asm-'
    FB = '-s_emu_fb-'
    FILENAME = '-s_emu_filename-'
    MEM_LOCATION = '-s_emu_mem_loc-'
    MEM_TABLE = '-s_emu_memory-'
    PROFILER = '-s_emu_profiler-'
    GPIO_TABLE = '-s_emu_gpio-'
    SCHEMATIC = '-s_emu_schematic-'
