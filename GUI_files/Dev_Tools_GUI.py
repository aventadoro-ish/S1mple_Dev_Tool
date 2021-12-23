from GUI_files.Dev_Tools_GUI_Elements import *
from Dev_Tools_Commons import *
import PySimpleGUI as sg
from queue import Queue


def open_window() -> sg.Window:
    window = sg.Window('S1mple Dev Tools', LAYOUT_TAB_GROUP, finalize=True)
    window[AsmElements.INP_MULTILINE].bind("<Return>", "_Enter")

    return window


def event_loop(window: sg.Window, q: Queue) -> None:
    # TODO: asyncio investigation
    while True:
        event, values = window.read()

        if event in (None, 'Exit', 'Cancel'):
            close_main_window_event(window, values, q)
            break

        tab = values['-tab_grp-']
        if tab == Tabs.ASSEMBLER:
            event_loop_tab_asm(window, values, event, q)

        elif tab == Tabs.SOFT_EMU:
            event_loop_tab_soft_emu(window, values, event, q)

        elif tab == Tabs.MICROCODE:
            event_loop_tab_microcode(window, values, event, q)

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


def event_loop_tab_microcode(window: sg.Window, values, event, q: Queue):
    print(f'MICROCODE EVENT: {event}')


def close_main_window_event(window: sg.Window, values: dict, q: Queue) -> None:
    print(f'[View]: Closing Main Window!')
    q.put(QueueEntry(active_tab=None,
                     element=None,
                     data='Exit'))


def asm_change_event(window: sg.Window, values: dict, q: Queue) -> None:
    new_text: str = values[AsmElements.INP_MULTILINE]

    q.put(QueueEntry(active_tab=Tabs.ASSEMBLER,
                     element=AsmElements.INP_MULTILINE,
                     data=new_text))


def asm_save_file_event(window: sg.Window, values: dict, q: Queue) -> None:
    q.put(QueueEntry(active_tab=Tabs.ASSEMBLER,
                     element=AsmElements.SAVE_BTN,
                     data=values[AsmElements.FB]))


def asm_file_choice_event(window: sg.Window, values: dict, q: Queue) -> None:
    q.put((QueueEntry(active_tab=Tabs.ASSEMBLER,
                      element=AsmElements.FB,
                      data=values[AsmElements.FB])))


# SOFT EMULATOR TAB
def soft_emu_file_choice_event(window: sg.Window, values: dict, q: Queue) -> None:
    q.put((QueueEntry(active_tab=Tabs.SOFT_EMU,
                      element=SEmuElements.FB,
                      data=values[SEmuElements.FB])))


def soft_emu_load_event(window: sg.Window, values: dict, q: Queue) -> None:
    q.put(QueueEntry(active_tab=Tabs.SOFT_EMU,
                     element=SEmuElements.LOAD_ASM_PROG,
                     data='Asm'))


def soft_emu_profiler_event(window: sg.Window, values: dict, q: Queue) -> None:
    sg.PopupOK('Profiler WIP')


