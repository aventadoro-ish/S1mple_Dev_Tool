from Dev_Tools_GUI_Events import *
import PySimpleGUI as sg
from enum import Enum
from queue import Queue


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


LAYOUT_TAB_MICROCODE = [
    [sg.Text(Tabs.MICROCODE), sg.FileBrowse()]
]

TABLE = [['Acc', 0], ['R', 0], ['IR', 0], ['PCL', 0], ['PCH', 0], ['PC', 0],
         ['MAL', 0], ['MAH', 0], ['MAR', 0]]

SOFT_EMU_COL_REGISTERS = [
    [sg.Text('Registers')],
    [sg.Table(values=TABLE[:][:], headings=['register', 'value'],
              auto_size_columns=False, display_row_numbers=True, justification='right',
              key='-TABLE-', size=(48, 16), hide_vertical_scroll=True)],
]

SOFT_EMU_COL_MEMORY = [
    [sg.Text('Memory:', key=SEmuElements.MEM_LOCATION)],
    [sg.Multiline('MEMORY', key=SEmuElements.MEM_TABLE, size=(48, 11))],
    [sg.Multiline('GPIO', key=SEmuElements.GPIO_TABLE, size=(48, 5))]
]

LAYOUT_TAB_SOFT_EMULATOR = [
    # Tools
    [sg.Text(Tabs.SOFT_EMU),
     sg.Button('Asm', key=SEmuElements.LOAD_ASM_PROG),
     sg.FileBrowse('Open', key=SEmuElements.FB, target=SEmuElements.FB, change_submits=True),
     sg.Text('Asm', key=SEmuElements.FILENAME),
     sg.Button('Profiler', key=SEmuElements.PROFILER)],

    [sg.Column(SOFT_EMU_COL_REGISTERS, size=(250, 320)),
     sg.Column(SOFT_EMU_COL_MEMORY, justification='centertop', size=(370, 320))]
]

LAYOUT_TAB_HARD_EMULATOR = [
    [sg.Text(Tabs.HARD_EMU)]
]

LAYOUT_TAB_ASSEMBLER = [
    [sg.Text('New file', key=AsmElements.FILENAME),
     sg.FileBrowse('Open', key=AsmElements.FB, target=AsmElements.FB, change_submits=True),
     sg.Button('Save', key=AsmElements.SAVE_BTN)],
    [sg.Multiline(size=(44, 20), autoscroll=True, enable_events=True,
                  key=AsmElements.INP_MULTILINE, enter_submits=True),
     sg.Multiline(size=(44, 20), key=AsmElements.OUT_MULTILINE, disabled=True, no_scrollbar=True)
     ]
]

LAYOUT_TAB_EEPROM_PROGRAMMER = [
    [sg.Text('Arduino EEPROM Programmer')]
]

LAYOUT_TAB_GROUP = [
    [sg.TabGroup(
        [
            [sg.Tab(Tabs.ASSEMBLER, LAYOUT_TAB_ASSEMBLER, title_color='Red', border_width=10,
                    background_color='Lightgray', key=Tabs.ASSEMBLER.value),
             sg.Tab(Tabs.SOFT_EMU, LAYOUT_TAB_SOFT_EMULATOR, title_color='Blue',
                    background_color='Lightgray'),
             sg.Tab(Tabs.HARD_EMU, LAYOUT_TAB_HARD_EMULATOR, title_color='Black',
                    background_color='Lightgray'),
             sg.Tab(Tabs.MICROCODE, LAYOUT_TAB_MICROCODE, title_color='Black',
                    background_color='Lightgray'),
             sg.Tab(Tabs.EEPROM, LAYOUT_TAB_EEPROM_PROGRAMMER)
             ]
        ], key='-tab_grp-', tab_location='centertop', title_color='Black', tab_background_color='White',
        selected_title_color='Black', selected_background_color='Gray',
        border_width=0)
    ]
]


def open_window() -> sg.Window:
    window = sg.Window('S1mple Dev Tools', LAYOUT_TAB_GROUP, finalize=True)
    window[AsmElements.INP_MULTILINE].bind("<Return>", "_Enter")

    return window


def event_loop(window: sg.Window, q: Queue) -> None:
    # TODO: asyncio investigation
    while True:
        event, values = window.read()

        if event in (None, 'Exit', 'Cancel'):
            q.put('Exit')
            break

        tab = values['-tab_grp-']
        if tab == Tabs.ASSEMBLER:
            event_loop_tab_asm(window, values, event, q)

        elif tab == Tabs.SOFT_EMU:
            event_loop_tab_soft_emu(window, values, event, q)

        else:
            print('Undefined tab event!')


def event_loop_tab_asm(window: sg.Window, values, event, q: Queue):
    if event == AsmElements.INP_MULTILINE + "_Enter":
        asm_change_event(window, values, q)

    elif event == AsmElements.FB.value:
        asm_file_choice_event(window, values, q)

    elif event == AsmElements.SAVE_BTN:
        asm_save_file_event(window, values, q)

    elif event != AsmElements.INP_MULTILINE:
        print(f'{event=}, {values=}')


def event_loop_tab_soft_emu(window: sg.Window, values, event, q: Queue):
    if event == SEmuElements.FB:
        soft_emu_file_choice_event(window, values, q)
    elif event == SEmuElements.LOAD_ASM_PROG:
        soft_emu_load_event(window, values, q)
    elif event == SEmuElements.PROFILER:
        print('PROFILER')
        soft_emu_profiler_event(window, values, q)
    else:
        print(f'{event=}, {values=}')


