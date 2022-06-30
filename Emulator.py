from collections import namedtuple


WatchEvent = namedtuple('WatchEvent', ('component', 'action', 'value', 'new_value'))


class Watch:
    EVENTS: list[WatchEvent] = []

    @classmethod
    def message(cls, component, action, value, new_val, *args):
        cls.EVENTS.append(WatchEvent(component, action, value, new_val))

    @classmethod
    def tick(cls):
        events_this_tick: list[str] = []
        while cls.EVENTS:
            match cls.EVENTS:
                case [get, set_, *_] if get.action == 'get' and set_.action == 'set':
                    events_this_tick.append(
                        f'{get.component}({get.value}) -> '
                        f'{set_.component}({set_.value})'
                    )

                    cls.EVENTS.remove(get)
                    cls.EVENTS.remove(set_)

                case [inc, *_] if inc.action == 'inc':
                    events_this_tick.append(f'{inc.component}++ ({inc.value+1})')
                    cls.EVENTS.remove(inc)

                case [dec, *_] if dec.action == 'dec':
                    events_this_tick.append(f'{dec.component}-- ({dec.value-1})')
                    cls.EVENTS.remove(dec)

                case [set_, *_] if set_.action == 'set':
                    events_this_tick.append(
                        f'{set_.component}({set_.value}) <- ({set_.new_value})'
                    )
                    cls.EVENTS.remove(dec)

                case [get, *_] if get.action == 'get':
                    events_this_tick.append(f'{get.component} -> {get.value}')
                    cls.EVENTS.remove(get)

                case [unknown, *_]:
                    events_this_tick.append(str(unknown))
                    cls.EVENTS.remove(unknown)

        cls.EVENTS.clear()
        print(', '.join(events_this_tick))


def watch(func):
    def inner(self, *args, **kwargs):
        if not self.is_watched():
            return func(self, *args, **kwargs)

        if args:
            Watch.message(self.name, func.__name__, self.value, args[0])
        else:
            Watch.message(self.name, func.__name__, self.value, '')

        return func(self, *args, **kwargs)

    return inner


def for_watchable_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:   # there's propably a better way to do this
            # if callable(getattr(cls, attr)) and attr != "__init__":
            if attr in ('get', 'set', 'inc', 'dec', 'reset'):
                # print(f'*adding decorator to {attr}')
                setattr(cls, attr, decorator(getattr(cls, attr)))

        return cls
    return decorate


@for_watchable_methods(watch)
class WatchableComponent:
    def __init__(self, name='', value=None):
        self._name = name
        self._value_ = value

    @property
    def name(self):
        return self._name

    def set(self, value: int) -> None:
        self._value_ = value

    def get(self) -> int:
        return self._value_

    def is_watched(self) -> bool:
        self
        return False

    @property
    def value(self) -> int:
        return self._value_

    @value.setter
    def value(self, v):
        self._value_ = v


@for_watchable_methods(watch)
class Register(WatchableComponent):
    def __init__(self, name: str, default_value=0, max_value=0xff, is_watched=False):
        super().__init__(name, default_value)
        self.on_reset = default_value
        self.max_value = max_value
        self._is_watched = is_watched

    def is_watched(self) -> bool:
        return self._is_watched

    @property
    def name(self):
        return f'{super().name}'

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, v):
        super(Register, type(self)).value.fset(self, v & self.max_value)

    def reset(self):
        self.value = self.on_reset

    def inc(self):
        self.value += 1

    def dec(self):
        self.value -= 1


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

        return self.values[idx + self.range_.start]

    def __setitem__(self, idx, value):
        if idx not in self.range_:
            raise IndexError(f'Memory Component range violation. Trying to access {idx} '
                             f'in component with range {self.range_.start}:'
                             f'{self.range_.stop}')

        self.values[idx + self.range_.start] = value

    def get(self, addr: int) -> int:
        return self[addr + self.range_.start]

    def set(self, addr: int, value: int):
        self[addr + self.range_.start] = value


@for_watchable_methods(watch)
class Memory(WatchableComponent):
    def __init__(self, components: tuple[MemoryComponent],
                 watch_ranges: tuple[range]):
        super().__init__('', None)
        self.addr = 0
        self.components = components
        self.watch_ranges = watch_ranges

    def set_addr(self, addr: int):
        self.addr = addr

    @property
    def value(self) -> int:
        return self[self.addr].get(self.addr)

    @property
    def name(self) -> str:
        return f'{self[self.addr].name}[{self.addr}]'

    def __getitem__(self, addr: int) -> MemoryComponent:
        for idx, comp in enumerate(self.components):
            if addr in comp.range_:
                return self.components[idx]
        else:
            raise IndexError(f'Address {addr} is not assigned to a memory component.')

    def set(self, v):
        self[self.addr].set(self.addr, v)

    def get(self) -> int:
        # TODO: reformat this mess
        return self[self.addr].values[self.addr]

    def is_watched(self) -> bool:
        for r in self.watch_ranges:
            if self.addr in r:
                return True

        return False


@for_watchable_methods(watch)
class ALU(WatchableComponent):
    # TODO: this ALU class
    def __init__(self, name, reg_a: Register, reg_b: Register):
        self.operand_a = reg_a
        self.operand_a_b = reg_b


if __name__ == '__main__':
    # testing
    reg_a = Register('A', is_watched=True)
    reg_b = Register('B', is_watched=True)

    reg_a.set(3)
    Watch.tick()

    reg_b.set(reg_a.get())
    reg_b.inc()
    Watch.tick()

    reg_b.inc()
    Watch.tick()

    print(f'A={reg_a.value}, B={reg_b.value}')

    rom = MemoryComponent('ROM', range(0, 0x7fff))
    ram = MemoryComponent('RAM', range(0x8000, 0xffff))

    mar = Register('MAR', max_value=0xffff)

    mem = Memory((rom, ram), (range(0, 0xffff),))

    mem.set_addr(mar.get())

    mem.set(55)
    Watch.tick()

    reg_a.set(mem.get())
    Watch.tick()
    print(reg_a.value)



