def parse_wizard(rest):
    """
    Парсит команду wizard.
    Обычно вызывается без аргументов, но мы оставляем 'rest' на вырост
    (например, если потом захотим сделать команду 'wizard reset').
    """
    rest = rest.strip()
    
    # Разбиваем на аргументы, если они вдруг есть
    args = rest.split() if rest else []
    
    return {
        'action': 'wizard',
        'args': args
    }