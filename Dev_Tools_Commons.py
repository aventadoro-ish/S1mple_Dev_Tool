from enum import Enum
from dataclasses import dataclass


@dataclass
class QueueEntry:
    active_tab: str
    element: str
    data: str


class EnumStr(str, Enum):   # TODO: how does adding 'str' fixes my problem?
    def __str__(self):
        return self.value


