import re
from .args_parser import parse_specs
from .wells_parser import parse_wells
def parse_add(rest):
    # rest = 'образец_1 dil 20 range B1:B3, dil 10 range C1:C3'
    
    # 1. Имя
    tokens = rest.split(' ', 1)
    name, specs_part = tokens    
    
    # 3. Парсим спецификации
    specs = parse_specs(specs_part)  # ← ЗДЕСЬ ВЫЗЫВАЕМ
    
    return {
        'action': 'add',
        'name': name,
        'specs': specs
    }

def parse_edit(rest):
    """
    Парсит команду edit.
    
    Вход: '"образец 1" B1:B3 dil 40'
    Выход: {
        'action': 'edit',
        'name': 'образец 1',
        'wells': ['B1','B2','B3'],
        'new_dilution': 40
    }
    """
    # 1. Имя в кавычках
    name_match = re.search(r'"([^"]+)"', rest)
    name = name_match.group(1)
    
    # 2. Всё что после имени
    after_name = rest.split('"')[2].strip()
    
    # 3. Разбиваем по пробелам
    tokens = after_name.split()
    
    # Ищем где стоит 'dil'
    dil_index = tokens.index('dil')
    
    # Всё до dil_index - лунки
    wells_str = ' '.join(tokens[:dil_index])
    # Всё после dil_index - число
    new_dilution = int(tokens[dil_index + 1])
    
    wells = parse_wells(wells_str)
    
    return {
        'action': 'edit',
        'name': name,
        'wells': wells,
        'new_dilution': new_dilution
    }

def parse_rename(rest):
    """
    Парсит команду rename.
    
    Вход: '"образец 1" "образец 2"'
    Выход: {
        'action': 'rename',
        'old_name': 'образец 1',
        'new_name': 'образец 2'
    }
    """
    # Находим все имена в кавычках
    matches = re.findall(r'"([^"]+)"', rest)
    
    if len(matches) != 2:
        raise ValueError(
            "rename требует два имени в кавычках: rename \"старое\" \"новое\"\n"
            f"Получено: {rest}"
        )
    
    return {
        'action': 'rename',
        'old_name': matches[0],
        'new_name': matches[1]
    }

def parse_delete(rest):
    """
    Парсит команду delete.
    
    Вход: '"образец 1"'
    Выход: {
        'action': 'delete',
        'name': 'образец 1'
    }
    """
    name_match = re.search(r'"([^"]+)"', rest)
    if not name_match:
        raise ValueError(
            "delete требует имя фрейма в кавычках: delete \"название\"\n"
            f"Получено: {rest}"
        )
    
    return {
        'action': 'delete',
        'name': name_match.group(1)
    }

def parse_show(rest):
    """
    Парсит команду show.
    
    Вход: 'all', 'cal', или имя фрейма
    Выход: {
        'action': 'show',
        'target': 'all' | 'cal' | 'frame',
        'name': 'имя' 
    }
    """
    # Очищаем от пробелов
    rest = rest.strip()
    
    if not rest:
        raise ValueError("Команда show не может быть пустой. Введите 'all', 'cal' или имя фрейма.")

    rest_lower = rest.lower()

    # 1. Показать всё
    if rest_lower == 'all':
        return {
            'action': 'show',
            'target': 'all'
        }
    
    # 2. Показать калибровку (основную)
    if rest_lower == 'cal' or rest_lower == 'calibration':
        return {
            'action': 'show',
            'target': 'cal',
            'name': 'main'  # Задаем имя по умолчанию
        }
        
    # 2.1. Если в будущем будет несколько калибровок (например, show cal my_cal)
    if rest_lower.startswith('cal ') or rest_lower.startswith('calibration '):
        parts = rest.split(maxsplit=1)
        return {
            'action': 'show',
            'target': 'cal',
            'name': parts[1].strip()
        }

    # 3. Всё остальное считаем именем фрейма
    return {
        'action': 'show',
        'target': 'frame',
        'name': rest
    }
def parse_erase(rest):
    pass
