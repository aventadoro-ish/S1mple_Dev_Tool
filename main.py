from GUI_files.Dev_Tools_GUI_Elements import Tabs, AsmElements, SEmuElements
from GUI_files.Dev_Tools_GUI import open_window, event_loop

from Models.Assembler import Assembler

from Dev_Tools_Commons import QueueEntry

import PySimpleGUI as sg
from queue import Queue
from threading import Thread


def controller(window: sg.Window, q: Queue):
    asm = Assembler()

    while True:
        qe: QueueEntry = q.get()
        print(f'[Controller]: {qe=}')

        if qe.data in (None, 'Exit', 'Cancel', 'Close'):
            print('[Controller] Exiting program!')
            break

        elif qe.active_tab == Tabs.ASSEMBLER:
            asm_actions(asm, qe, window)

        elif qe.active_tab == Tabs.MICROCODE:
            print(f'[Controller] Microcode action')

        elif qe.active_tab == Tabs.SOFT_EMU:
            soft_emu_actions(None, qe, window)

        else:
            print(f'[Controller]: Undefined Tab Event:\n'
                  f'{qe=}')


def asm_actions(asm: Assembler, qe: QueueEntry, window: sg.Window):
    if qe.element == AsmElements.INP_MULTILINE:
        asm.compare_and_update(qe.data)

        out_box: sg.Multiline = window[AsmElements.OUT_MULTILINE]
        out_box.Update('')
        out_box.print(qe.data)

        controller.text = qe.data

    elif qe.element == AsmElements.SAVE_BTN:
        print(f'[Controller]: ASM: Save {qe.data}')

    elif qe.element == AsmElements.FB:
        filepath: str = qe.data
        filename: str = filepath.split('/')[-1]
        filename_text: sg.Text = window['-asm_filename-']
        filename_text.update(value=filename)

    else:
        print(f'[Controller]: Undefined {Tabs.ASSEMBLER} action: {qe=}')


def soft_emu_actions(emu: None, qe: QueueEntry, window: sg.Window):
    if qe.element == SEmuElements.FB:
        filepath: str = qe.data
        filename: str = filepath.split('/')[-1]
        filename_text: sg.Text = window[SEmuElements.FILENAME]
        filename_text.update(value=filename)

    elif qe.element == SEmuElements.LOAD_ASM_PROG:
        window['-s_emu_filename-'].update(value='Asm')

    else:
        print(f'[Controller] Unknown {Tabs.SOFT_EMU} action: {qe=}')


def main():
    q = Queue()
    window = open_window()

    model = Thread(target=controller, args=(window, q))
    model.start()

    event_loop(window, q)


if __name__ == "__main__":
    main()


