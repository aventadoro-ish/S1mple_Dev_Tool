import PySimpleGUI as sg
from queue import Queue
from Dev_Tools_Commons import *
from Dev_Tools_Commons import *


def close_main_window_event(window: sg.Window, values: dict, q: Queue) -> None:
    print(f'[View]: Closing Main Window!')
    q.put(QueueEntry(active_tab=None,
                     element=None,
                     data='Exit'))


def asm_change_event(window: sg.Window, values: dict, q: Queue) -> None:
    new_text: str = values['-asm_inp-']

    qe = QueueEntry(active_tab=Tabs.ASSEMBLER,
                    element=AsmElements.INP_MULTILINE,
                    data=new_text)

    q.put(qe)


def asm_save_file_event(window: sg.Window, values: dict, q: Queue) -> None:
    print(f'{values=}, {type(values)=}')
    print('Save press!')


def asm_file_choice_event(window: sg.Window, values: dict, q: Queue) -> None:
    filepath: str = values['-asm_fb-']
    filename: str = filepath.split('/')[-1]
    filename_text: sg.Text = window['-asm_filename-']
    filename_text.update(value=filename)


# SOFT EMULATOR TAB
def soft_emu_file_choice_event(window: sg.Window, values: dict, q: Queue) -> None:
    filepath: str = values['-s_emu_fb-']
    filename: str = filepath.split('/')[-1]
    filename_text: sg.Text = window['-s_emu_filename-']
    filename_text.update(value=filename)


def soft_emu_load_event(window: sg.Window, values: dict, q: Queue) -> None:
    window['-s_emu_filename-'].update(value='Asm')


def soft_emu_profiler_event(window: sg.Window, values: dict, q: Queue) -> None:
    window.disable()    # TODO window.disable/enable is a temp workaround
    profiler_window = sg.Window('Profiler WIP',
                                [[sg.Button('Close')]],
                                size=(400, 100))

    while True:
        event, values = profiler_window.read()

        if event in (None, 'Exit', 'Cancel', 'Close'):
            window.enable()
            break
        else:
            print(event, values)

