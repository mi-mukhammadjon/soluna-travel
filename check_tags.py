with open('/app/templates/bookings/booking_list.html', 'r') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if '{% if ' in stripped and '{% endif %}' not in stripped and '{% else %}' not in stripped and '{% elif ' not in stripped:
        stack.append(('if', i, stripped[:80]))
    elif '{% for ' in stripped and '{% endfor %}' not in stripped:
        stack.append(('for', i, stripped[:80]))
    elif '{% with ' in stripped and '{% endwith %}' not in stripped:
        stack.append(('with', i, stripped[:80]))
    elif '{% endif %}' in stripped:
        if stack:
            tag, line_no, text = stack.pop()
            if tag != 'if':
                print(f'MISMATCH: endif at line {i} closes {tag} at line {line_no}: {text}')
        else:
            print(f'EXTRA endif at line {i}')
    elif '{% endfor %}' in stripped:
        if stack:
            tag, line_no, text = stack.pop()
            if tag != 'for':
                print(f'MISMATCH: endfor at line {i} closes {tag} at line {line_no}: {text}')
        else:
            print(f'EXTRA endfor at line {i}')

if stack:
    for tag, line_no, text in stack:
        print(f'UNCLOSED {tag} at line {line_no}: {text}')
else:
    print('All tags balanced!')
