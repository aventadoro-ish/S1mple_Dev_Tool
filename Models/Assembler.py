import difflib


class Assembler:
    def __init__(self):
        self.prog: str = ''
        self._d = difflib.Differ(linejunk=bool)

    def compare_and_update(self, new_prog: str) -> list[str]:
        changes: list[str] = []
        for line in self._d.compare(self.prog.split('\n'), new_prog.split('\n')):
            if not line.startswith('? '):  # filters out changes inside lines
                changes.append(line)
                print(line)

        self.prog = new_prog
        return line
