import difflib
import PySimpleGUI as sg
from queue import Queue


def asm_change_event(window: sg.Window, values: dict, q: Queue) -> None:
    if not hasattr(asm_change_event, 'text'):
        asm_change_event.text = ''

    if not hasattr(asm_change_event, 'dif'):
        # TODO: linejuck = method that returns if a line is ignorable
        d = difflib.Differ(linejunk=bool)

    new_text: str = values['-asm_inp-']

    for line in d.compare(asm_change_event.text.split('\n'), new_text.split('\n')):
        if not line.startswith('? '):   # filters out changes inside lines
            print(line)

    out_box: sg.Multiline = window['-asm_out-']
    out_box.Update('')
    out_box.print(new_text)

    asm_change_event.text = new_text


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

