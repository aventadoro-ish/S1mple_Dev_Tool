import sys
from collections import namedtuple
from dataclasses import dataclass


WatchEvent = namedtuple('WatchEvent', ('component', 'action', 'value', 'other'))


class Watch:
    EVENTS: list[WatchEvent] = []

    @classmethod
    def message(cls, component, action, value, **kwargs):
        cls.EVENTS.append(WatchEvent(component, action, value, str(**kwargs)))
        # print(f'Watch: {component=}, {action=}, {value=}', end='')
        # print(kwargs) if kwargs else print()

    @classmethod
    def tick(cls):
        while cls.EVENTS:
            match cls.EVENTS:
                case [get, set_, *_] if get.action == 'get' and set_.action == 'set':
                    print(f'{get.component} ({get.value}) -> '
                          f'{set_.component} ({set_.value})')
                    cls.EVENTS.remove(get)
                    cls.EVENTS.remove(set_)

                case [inc, *_] if inc.action == 'inc':
                    print(f'{inc.component}++ ({inc.value})')
                    cls.EVENTS.remove(inc)

                case [dec, *_] if dec.action == 'dec':
                    print(f'{dec.component}-- ({dec.value})')
                    cls.EVENTS.remove(dec)

                case [set_, *_] if set_.action == 'set':
                    print(f'{set_.component} <- ({set_.value})')
                    cls.EVENTS.remove(dec)

                case [unknown, *_]:
                    print(unknown)
                    cls.EVENTS.remove(unknown)

        cls.EVENTS.clear()
        print()


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:   # there's propably a better way to do this
            if callable(getattr(cls, attr)) and attr != "__init__":
                # print(f'*adding decorator to {attr}')
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def register_watch(func):
    def inner(self, *args, **kwargs):
        if not self.is_watched:
            return func(self, *args, **kwargs)

        Watch.message(self.name, func.__name__, self.value)
        # match func.__name__:
        #     case "get":
        #         print(f'Register {self.name} -> {self.value}')
        #     case "set":
        #         print(f'Register {self.name} <- {args[0]}')
        #     case "inc":
        #         print(f'Register {self.name}++')
        #     case "dec":
        #         print(f'Register {self.name}--')
        #     case _:
        #         print(f'Register {self.name} {func.__name__}')

        return func(self, *args, **kwargs)

    return inner


@for_all_methods(register_watch)
class Register:
    def __init__(self, name: str, default_value=0, max_value=0xff, is_watched=False):
        self.name = name
        self._value_ = default_value
        self.on_reset = default_value
        self.max_value = max_value
        self.is_watched = is_watched

    @property
    def value(self):
        return self._value_

    @value.setter
    def value(self, v):
        self._value_ = v & self.max_value

    def get(self) -> int:
        return self._value_

    def set(self, v):
        self._value_ = v & self.max_value

    def reset(self):
        self.value = self.on_reset

    def inc(self):
        self.value += 1

    def dec(self):
        self.value -= 1


def memory_comp_watch(func):
    def inner(self, *args, **kwargs):
        func(self, *args, **kwargs)

    return inner


class MemoryComponent:
    def __init__(self, name: str, range_: range):
        self.name = name
        self.range_ = range_
        self.values = bytearray(len(self.range_))

    def __getitem__(self, idx) -> int:
        if idx not in self.range_:
            raise IndexError(f'Memory Component range violation. Trying to access {idx} '
                             f'in component with range {self.range_.start}:'
                             f'{self.range_.stop}')

        return self.values[idx]

    def __setitem__(self, idx, value):
        if idx not in self.range_:
            raise IndexError(f'Memory Component range violation. Trying to access {idx} '
                             f'in component with range {self.range_.start}:'
                             f'{self.range_.stop}')

        self.values[idx] = value


class Memory:
    def __init__(self, watch_addresses: tuple(int)):
        self.watch_addresses = watch_addresses
        self.components: list[MemoryComponent]

    def add_component(self, comp: MemoryComponent):
        # TODO: I stopped here
        pass



if __name__ == '__main__':
    # testing
    reg_a = Register("A", max_value=255, is_watched=True)
    reg_b = Register("B", max_value=255, is_watched=True)

    reg_a.set(13)
    reg_b.set(55)
    Watch.tick()

    reg_a.set(reg_b.get())
    Watch.tick()

    mem = MemoryComponent('ram', range(0, 0x7fff))
    mem[0x23ff] = 3
    mem[0x22ff] = 4
    mem[0x21ff] = 5

    print(f'{mem[0x23ff]}')




