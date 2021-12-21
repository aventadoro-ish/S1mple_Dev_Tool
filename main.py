import PySimpleGUI as sg
from Dev_Tools_Commons import *
from GUI_files.Dev_Tools_GUI import open_window, event_loop
from Models.Assembler import Assembler

from queue import Queue
from threading import Thread


def controller(window: sg.Window, q: Queue):
    asm = Assembler()

    while True:
        qe: QueueEntry = q.get()

        if qe.data in (None, 'Exit', 'Cancel', 'Close'):
            print('[Controller] Exiting program!')
            break

        elif qe.active_tab == Tabs.ASSEMBLER:
            if qe.element == AsmElements.INP_MULTILINE:
                asm.compare_and_update(qe.data)

                out_box: sg.Multiline = window['-asm_out-']
                out_box.Update('')
                out_box.print(qe.data)

                controller.text = qe.data


def main():
    q = Queue()
    window = open_window()

    model = Thread(target=controller, args=(window, q))
    model.start()

    event_loop(window, q)


if __name__ == "__main__":
    main()


