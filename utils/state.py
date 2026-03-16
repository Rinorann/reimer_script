def initial_state():
    """Создает пустой эксперимент"""
    return {
        'frames': {},  # имя фрейма -> {лунка: {dilution: N, od: None}}
        'calibrations' : {},  # имя калибровки(main) -> {baseline, standards, linear_fit}
        '_index': {}   # лунка -> имя фрейма/калибровки
    }