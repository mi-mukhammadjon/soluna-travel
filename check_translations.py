with open('/app/locale/uz/LC_MESSAGES/django.po', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('msgid '):
        msgid = line.strip().replace('msgid ', '').strip('"')
        next_line = lines[i + 1] if i + 1 < len(lines) else ''
        if next_line.strip() == 'msgstr ""':
            print(f'Line {i+1}: msgid={repr(msgid)}')
