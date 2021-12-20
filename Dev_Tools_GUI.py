import PySimpleGUI as sg
from Dev_Tools_GUI_Events import *
import time


LAYOUT_TAB_MICROCODE = [
    [sg.Text('Microcode'), sg.FileBrowse()]
]

LAYOUT_TAB_SOFT_EMULATOR = [
    [sg.Text('Software Emulator')]
]

LAYOUT_TAB_HARD_EMULATOR = [
    [sg.Text('Hardware Arduino-serial emulator')]
]

LAYOUT_TAB_ASSEMBLER = [
    [sg.Text('New file', key='-asm_filename-'),
     sg.FileBrowse('Open', key='-asm_fb-', target='-asm_fb-', change_submits=True),
     sg.Button('Save', key='-asm_save_file_event-')],
    [sg.Multiline(size=(44, 20), autoscroll=True, enable_events=True,
                  key='-asm_inp-', enter_submits=True),
     sg.Multiline(size=(44, 20), key='-asm_out-', disabled=True, no_scrollbar=True)
     ]
]

LAYOUT_TAB_GROUP = [
    [sg.TabGroup(
        [
            [sg.Tab('Assembler', LAYOUT_TAB_ASSEMBLER, title_color='Red', border_width=10,
                    background_color='Lightgray', tooltip='Assembler for S1mple'),
             sg.Tab('Soft Emulator', LAYOUT_TAB_SOFT_EMULATOR, title_color='Blue',
                    background_color='Lightgray'),
             sg.Tab('Hard Emulator', LAYOUT_TAB_HARD_EMULATOR, title_color='Black',
                    background_color='Lightgray', tooltip='Enter  your Lsst job experience'),
             sg.Tab('Microcode', LAYOUT_TAB_MICROCODE, title_color='Black',
                    background_color='Lightgray', tooltip='Enter  your Lsst job experience')
             ]
        ], tab_location='centertop', title_color='Black', tab_background_color='White',
        selected_title_color='Black', selected_background_color='Gray',
        border_width=5)
    ]
]


def open_window():
    window = sg.Window('S1mple Dev Tools', LAYOUT_TAB_GROUP, finalize=True)
    window['-asm_inp-'].bind("<Return>", "_Enter")

    event_loop(window)


def event_loop(window: sg.Window):
    # TODO: asyncio investigation
    while True:
        event, values = window.read()

        if event in (None, 'Exit', 'Cancel'):
            break

        elif event == '-asm_inp-' + "_Enter":
            asm_change_event(window, values)

        elif event == '-asm_fb-':
            asm_file_choice_event(window, values)

        elif event == '-asm_save_file_event-':
            asm_save_file_event(window, values)

        elif event != '-asm_inp-':
            print(f'{event=}, {values=}')
