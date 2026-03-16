def parse_fit(rest):
    """
    Парсит команду fit.
    Примеры:
      'fit' -> min: 0, max: 1000, cal: main
      'fit 10 100' -> min: 10, max: 100, cal: main
    """
    rest = rest.strip()
    
    # Дефолтные значения
    linear_min = 0.0
    linear_max = 1000.0
    cal_name = 'main'
    
    if rest:
        parts = rest.split()
        try:
            if len(parts) >= 1:
                linear_min = float(parts[0])
            if len(parts) >= 2:
                linear_max = float(parts[1])
            if len(parts) >= 3:
                cal_name = parts[2]
        except ValueError:
            raise ValueError("❌ ОШИБКА: Диапазон должен быть числами. Пример: fit 10 100")
            
        if linear_min >= linear_max:
            raise ValueError("❌ ОШИБКА: Минимум не может быть больше или равен максимуму!")

    return {
        'action': 'fit',
        'min': linear_min,
        'max': linear_max,
        'cal_name': cal_name
    }