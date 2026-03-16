from .well_executor import execute_load
from copy import deepcopy

def execute_calibration(state, wells, concs, cal_name='main'):
    """
    Принимает списки wells и concs.
    Записывает их в state['calibrations'][cal_name].
    """
    # 1. Делаем глубокую копию состояния, чтобы не испортить оригинал при ошибке
    new_state = deepcopy(state)
    
    # 2. Инициализируем структуру калибровки, если её еще нет
    if cal_name not in new_state['calibrations']:
        new_state['calibrations'][cal_name] = {
            'baseline': [], 
            'standards': {}, 
            'linear_fit': None
        }
        
    added = []
    conflicts = []
    
    # 3. Проходим циклом по парам (лунка, концентрация)
    # Используем zip, чтобы связать элементы двух списков по порядку
    for well, conc in zip(wells, concs):
        
        # Проверяем, не занята ли лунка кем-то другим через глобальный индекс
        if well in new_state['_index']:
            owner = new_state['_index'][well]
            conflicts.append((well, owner))
        else:
            # Записываем данные в блок стандартов
            new_state['calibrations'][cal_name]['standards'][well] = {
                'conc': conc,
                'od': execute_load(well)  # Значение OD подтянется позже через команду load
            }
            # Обновляем индекс, чтобы пометить лунку как занятую
            new_state['_index'][well] = f"cal_{cal_name}"
            added.append(f"{well}({conc})")
            
    # 4. Формируем отчет для пользователя
    report = f"📈 Калибровка '{cal_name}':\n"
    if added:
        report += f"  ✅ Добавлено: {', '.join(added)}\n"
    if conflicts:
        report += f"  ⚠️ Пропущено (уже занято):\n"
        for well, owner in conflicts:
            report += f"     {well} → '{owner}'\n"
            
    return new_state, report

def execute_baseline(state, wells, cal_name='main'):
    """
    Принимает список wells.
    Записывает их в state['calibrations'][cal_name]['baseline'].
    """
    new_state = deepcopy(state)
    
    # Инициализируем структуру калибровки, если её еще нет
    if cal_name not in new_state['calibrations']:
        new_state['calibrations'][cal_name] = {
            'baseline': {},  # <-- ТЕПЕРЬ ЭТО СЛОВАРЬ (чтобы хранить OD)
            'standards': {}, 
            'linear_fit': None
        }
    elif isinstance(new_state['calibrations'][cal_name]['baseline'], list):
        # Если вдруг в state остался старый формат (список), превращаем его в словарь
        old_bl = new_state['calibrations'][cal_name]['baseline']
        new_state['calibrations'][cal_name]['baseline'] = {w: {'od': None} for w in old_bl}
        
    added = []
    conflicts = []
    
    # Проходим по списку лунок
    for well in wells:
        if well in new_state['_index']:
            owner = new_state['_index'][well]
            conflicts.append((well, owner))
        else:
            # Записываем лунку как словарь с ключом 'od'
            new_state['calibrations'][cal_name]['baseline'][well] = {
                'od': execute_load(well) # Сюда потом попадет результат из ридера
            }
            # Бронируем лунку в главном индексе
            new_state['_index'][well] = f"cal_{cal_name}_baseline"
            added.append(well)
            
    # Отчет
    report = f"📍 Baseline калибровки '{cal_name}':\n"
    if added:
        report += f"  ✅ Добавлено: {', '.join(added)}\n"
    if conflicts:
        report += f"  ⚠️ Пропущено (уже занято):\n"
        for well, owner in conflicts:
            report += f"     {well} → '{owner}'\n"
            
    return new_state, report
