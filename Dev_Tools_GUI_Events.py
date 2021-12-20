import difflib
import PySimpleGUI as sg


def asm_change_event(window: sg.Window, values: dict) -> None:
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


def asm_save_file_event(window: sg.Window, values: dict) -> None:
    print(f'{values=}, {type(values)=}')
    print('Save press!')


def asm_file_choice_event(window, values):
    filepath: str = values['-asm_fb-']
    filename: str = filepath.split('/')[-1]
    filename_text: sg.Text = window['-asm_filename-']
    filename_text.update(value=filename)