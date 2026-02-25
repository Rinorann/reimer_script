import re
def parse_wells(parts):
    """'B1:B3, C5, E6:F6' -> ['B1','B2','B3','C5','E6','F6']"""
    wells = []
    COLUMNS = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I':9, 'J':10, 'K':11, 'L':12}
    COLUMNS_REVERSED = {i: k for k, i in COLUMNS.items()}
    for part in parts:
        part = part.strip()
        if ':' in part:
            # Колонка или строчка
            start, end = part.split(':')
            start_letter = re.match(r'([A-Z]+)', start).group(1)
            start_num = int(re.match(r'[A-Z]+(\d+)', start).group(1))
            end_letter = re.match(r'([A-Z]+)', end).group(1)
            end_num = int(re.match(r'[A-Z]+(\d+)', end).group(1))
            
            if start_letter == end_letter:
                # Одна колонка
                for num in range(start_num, end_num + 1):
                    wells.append(f"{start_letter}{num}")
            elif start_num == end_num:
                #Cтрочка
                for i in range(COLUMNS[start_letter], COLUMNS[end_letter]+1):
                    wells.append(f"{COLUMNS_REVERSED[i]}{start_num}")
        else:
            # Одиночная ячейка
            wells.append(part)
    
    return wells