from .wells_parser import parse_wells
import re
import re

import re

def parse_calibration(rest):
    """
    Вход: 'B1:B4 5, 10, 20, 30'
    Выход: {
        'action': 'calibration',
        'specs': [
            {'conc': 5.0, 'well': 'B1'},
            {'conc': 10.0, 'well': 'B2'},
            ...
        ]
    }
    """
    parts = rest.strip().split(maxsplit=1)
    if len(parts) < 2:
        raise ValueError("Формат: cal [ЛУНКИ] [КОНЦЕНТРАЦИИ] (напр. cal B1:B4 5, 10, 20, 30)")

    wells_part = parts[0].upper() # 'B1:B4'
    concs_part = parts[1]         # '5, 10, 20, 30'

    # 1. Надежный парсинг лунок (чтобы избежать AttributeError)
    wells = []
    if ':' in wells_part:
        start, end = wells_part.split(':')
        start_match = re.match(r'([A-H])(\d+)', start)
        end_match = re.match(r'([A-H])(\d+)', end)
        
        if not start_match or not end_match:
            raise ValueError(f"Неверный формат лунок: {wells_part}")
            
        r1, c1 = start_match.groups()
        r2, c2 = end_match.groups()
        
        # Разворачиваем диапазон B1:B4
        for r in range(ord(r1), ord(r2) + 1):
            for c in range(int(c1), int(c2) + 1):
                wells.append(f"{chr(r)}{c}")
    else:
        wells = wells_part.split(',')

    # 2. Парсинг концентраций (с защитой от пробелов)
    concs = []
    if ':' in concs_part and ',' not in concs_part:
        start, step = map(float, concs_part.split(':'))
        concs = [start + i * step for i in range(len(wells))]
    else:
        concs = [float(c) for c in re.split(r'[,\s]+', concs_part) if c.strip()]

    if len(wells) != len(concs):
        raise ValueError(f"ОШИБКА: Лунок {len(wells)}, а концентраций {len(concs)}!")


    return {
        'action': 'calibration',
        'wells': wells,
        'concs': concs
    }

def parse_baseline(rest):
    """
    Парсит остаток команды: 'bl B1:B3' или 'baseline A1, A2'
    """
    wells_part = rest.strip().upper()
    
    if not wells_part:
        raise ValueError("Укажите диапазон лунок для бейзлайна: bl B1:B3")

    # Встраиваем надежный парсинг лунок напрямую
    wells = []
    if ':' in wells_part:
        start, end = wells_part.split(':')
        start_match = re.match(r'([A-H])(\d+)', start)
        end_match = re.match(r'([A-H])(\d+)', end)
        
        if not start_match or not end_match:
            raise ValueError(f"Неверный формат лунок: {wells_part}")
            
        r1, c1 = start_match.groups()
        r2, c2 = end_match.groups()
        
        # Разворачиваем диапазон (от B1 до B3)
        for r in range(ord(r1), ord(r2) + 1):
            for c in range(int(c1), int(c2) + 1):
                wells.append(f"{chr(r)}{c}")
    else:
        # Если ввели через запятую или пробел (A1, A2, A3)
        wells = [w.strip() for w in re.split(r'[,\s]+', wells_part) if w.strip()]

    return {
        'action': 'baseline',
        'wells': wells
    }