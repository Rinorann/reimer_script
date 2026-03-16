from .frame_parsers import *
from .plate_parser import parse_full_load
def parse_command(text):
    """
    'add "образец 1" dil 20 B1:B3, dil 10 C1:C3'
    ↓
    {
        'action': 'add',
        'name': 'образец 1',
        'specs': [
            {'type': 'dil', 'value': 20, 'wells_str': 'B1:B3'},
            {'type': 'dil', 'value': 10, 'wells_str': 'C1:C3'}
        ]
    }
    """
    text = text.strip() #убирает пробелы слева от команды и справа от команды
    
    # 1. Откусывает первое слово-действие, деля по первому пробелу 
    parts = text.split(maxsplit=1)
    action = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else '' #остаток
    
    # 2. Отправляем в соответствующий парсер
    if action == 'add':
        return parse_add(rest)
    elif action == 'edit':
        return parse_edit(rest)
    elif action == 'erase':
        return parse_erase(rest)
    elif action == 'rename':
        return parse_rename(rest)
    elif action == 'delete':
        return parse_delete(rest)
    elif action == 'show':
        return parse_show(rest)
    elif action == 'undo':
        return {'action': 'undo'}
    elif action == 'load': 
        return parse_full_load(rest)
    else:
        raise ValueError(f'Неизвестная команда: {action}')