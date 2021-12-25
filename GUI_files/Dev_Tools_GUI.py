from GUI_files.Dev_Tools_GUI_Elements import *
from Dev_Tools_Commons import *
import PySimpleGUI as sg
from queue import Queue


def open_window() -> sg.Window:
    window = sg.Window('S1mple Dev Tools', LAYOUT_TAB_GROUP, finalize=True)
    window[AsmElements.INP_MULTILINE].bind("<Return>", "")

    return window


def event_loop(window: sg.Window, q: Queue) -> None:
    # TODO: asyncio investigation
    while True:
        event, values = window.read()

        if event in (None, 'Exit', 'Cancel'):
            close_main_window_event(window, values, q)
            break

        elif event not in values:
            # element that has been interacted with has no value, hence data is empty
            data = ''

        else:
            data = values[event]

        tab = values['-tab_grp-']

        q.put(QueueEntry(tab, event, data))


def close_main_window_event(window: sg.Window, values: dict, q: Queue) -> None:
    print(f'[View]: Closing Main Window!')
    q.put(QueueEntry(active_tab=None,
                     element=None,
                     data='Exit'))
