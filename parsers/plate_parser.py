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
    tokens = rest.strip()
    file_path = tokens
    
    return {
        'action': 'load_full',
        'file_path': file_path
    }