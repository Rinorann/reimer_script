def parse_full_load(rest):
    """
    Парсит команду load.
    
    Вход: 'plate.xlsx Sheet1' без пробелов
    Выход: {
        'action': 'load_full',
        'file_path': 'plate.xlsx',
        'sheet_name': 'Sheet1'
    }
    """
    tokens = rest.strip().split()
    if len(tokens) !=2:
                return None, "❌Образец: load plate.xlsx Sheet1"
    file_path, sheet_name = tokens
    
    return {
        'action': 'load_full',
        'file_path': file_path,
        'sheet_name': sheet_name
    }