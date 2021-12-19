import difflib


def asm_change_event(new_text: str):
    if not hasattr(asm_change_event, 'text'):
        asm_change_event.text = ''

    # TODO: linejuck = method that returns if a line is ignorable
    d = difflib.Differ(linejunk=None)
    for line in d.compare(asm_change_event.text, new_text):
        if not line.startswith('? '):
            print(line)

    print('')
    asm_change_event.text = new_text


