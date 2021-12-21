from Dev_Tools_GUI import open_window, event_loop
from queue import Queue
from threading import Thread


def controller(q: Queue):
    while True:
        data = q.get()
        if data == 'Exit':
            print('*Exiting')
            break


def main():
    q = Queue()
    window = open_window()

    model = Thread(target=controller, args=(q, ))
    model.start()

    event_loop(window, q)


if __name__ == "__main__":
    main()


