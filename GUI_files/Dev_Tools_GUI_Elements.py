import PySimpleGUI as sg
from Dev_Tools_Commons import EnumStr


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


class MicrocodeElements(EnumStr):
    LOAD_DEF_MICROCODE = '-mcc_ld_def-'
    OPEN_MICROCODE = '-mcc_open-'
    NEW_MICROCODE = '-mcc_new-'
    SAVE = '-mcc_save-'
    SAVE_AS = '-mcc_save_as-'
    IMPORT = '-mcc_import-'
    EXPORT = '-mcc_export-'
    FLAGS = '-mcc_flags-'
    ONE_STEP = '-mcc_step-'
    CONT_STEP = '-mcc_cont-'
    SPEED = '-mcc_speed-'
    DATA_MENU = '-mcc_data-'


MICROCODE_UPPER_CONTROL_PANEL = [
    sg.Button('Load Default', key=MicrocodeElements.LOAD_DEF_MICROCODE),
    sg.FileBrowse('Open', key=MicrocodeElements.OPEN_MICROCODE,
                  target=MicrocodeElements.OPEN_MICROCODE, change_submits=True),
    sg.Button('Save', key=MicrocodeElements.SAVE),
    sg.FolderBrowse('Save as', key=MicrocodeElements.SAVE_AS,
                    target=MicrocodeElements.SAVE_AS, change_submits=True),
    sg.FolderBrowse('New', key=MicrocodeElements.NEW_MICROCODE,
                    target=MicrocodeElements.NEW_MICROCODE, change_submits=True),
    sg.Button('Data', key=MicrocodeElements.DATA_MENU),

]

MICROCODE_CENTRAL_COLUMN = [
    [sg.Multiline('Info:', disabled=True, size=(21, 5), no_scrollbar=True)],
    [sg.Input(size=(21, 1), key=MicrocodeElements.FLAGS, tooltip='flags',
              change_submits=True)],
    [sg.Table(values=[['', '', '']], headings=['origin', 'dst', 'special'],
              col_widths=[5, 5, 5], auto_size_columns=False,
              size=(11, 11))]
]


LAYOUT_TAB_MICROCODE = [
    MICROCODE_UPPER_CONTROL_PANEL,
    [sg.Column([[sg.Table(values=[['', '']], headings=['#', 'name'], col_widths=[4, 8],
                          auto_size_columns=False, size=(30, 18))]]),
     sg.Column(MICROCODE_CENTRAL_COLUMN),
     sg.Column([[sg.Canvas(size=(320, 280))],
                [sg.Button('1 step', key=MicrocodeElements.ONE_STEP),
                 sg.Button('cont.', key=MicrocodeElements.CONT_STEP),
                 sg.Input(key=MicrocodeElements.SPEED, change_submits=True,
                          size=(10, 1))]])]
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