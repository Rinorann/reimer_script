from .well_executor import execute_load
from copy import deepcopy
def execute_add(state, name, specs):
    """
    specs = [
        {'dilution': 20, 'wells': ['B1','B2','B3']},
        {'dilution': 10, 'wells': ['C1','C2','C3']}
    ]
    """
    new_state = deepcopy(state)
    
    # Создаем фрейм если нет
    if name not in new_state['frames']:
        new_state['frames'][name] = {}
    
    added = []
    conflicts = []
    
    for spec in specs:
        dilution = spec['dilution']
        wells = spec['wells']
        
        for well in wells:
            if well in new_state['_index']:
                owner = new_state['_index'][well]
                conflicts.append((well, owner))
            else:
                new_state['frames'][name][well] = {
                    'dilution': dilution,
                    'od': execute_load(well)
                }
                new_state['_index'][well] = name
                added.append(well)
    
    # Отчет
    report = f"📦 Фрейм '{name}':\n"
    if added:
        report += f"  ✅ Добавлено: {', '.join(added)}\n"
    if conflicts:
        report += f"  ⚠️ Пропущено (занято):\n"
        for well, owner in conflicts:
            report += f"     {well} → '{owner}'\n"
    
    return new_state, report


def execute_edit(state, name, wells, new_dilution):
    """Изменить разведение у конкретных лунок во фрейме"""
    new_state = deepcopy(state)
    
    if name not in new_state['frames']:
        raise ValueError(f"Фрейм '{name}' не существует")
    
    edited = []
    not_found = []
    
    for well in wells:
        if well in new_state['frames'][name]:
            new_state['frames'][name][well]['dilution'] = new_dilution
            edited.append(well)
        else:
            not_found.append(well)
    
    # Отчет
    report = f"✏️ Фрейм '{name}':\n"
    if edited:
        report += f"  ✅ Изменено: {', '.join(edited)} → dil {new_dilution}\n"
    if not_found:
        report += f"  ⚠️ Не найдены: {', '.join(not_found)}\n"
    
    return new_state, report


def execute_erase(state, name, wells):
    """Удалить лунки из фрейма"""
    new_state = deepcopy(state)
    
    if name not in new_state['frames']:
        raise ValueError(f"Фрейм '{name}' не существует")
    
    erased = []
    not_found = []
    
    for well in wells:
        if well in new_state['frames'][name]:
            del new_state['frames'][name][well]
            del new_state['_index'][well]
            erased.append(well)
        else:
            not_found.append(well)
    
    # Если фрейм стал пустым - удаляем его
    if name in new_state['frames'] and not new_state['frames'][name]:
        del new_state['frames'][name]
        report = f"🗑️ Фрейм '{name}' удален (стал пустым)\n"
    else:
        report = f"🧹 Фрейм '{name}':\n"
    
    if erased:
        report += f"  ✅ Удалено: {', '.join(erased)}\n"
    if not_found:
        report += f"  ⚠️ Не найдены: {', '.join(not_found)}\n"
    
    return new_state, report


def execute_rename(state, old_name, new_name):
    """Переименовать фрейм"""
    new_state = deepcopy(state)
    
    if old_name not in new_state['frames']:
        raise ValueError(f"Фрейм '{old_name}' не существует")
    
    if new_name in new_state['frames']:
        raise ValueError(f"Фрейм '{new_name}' уже существует")
    
    # Переименовываем фрейм
    new_state['frames'][new_name] = new_state['frames'].pop(old_name)
    
    # Обновляем индекс
    for well in new_state['frames'][new_name]:
        new_state['_index'][well] = new_name
    
    report = f"📝 Фрейм '{old_name}' → '{new_name}'"
    
    return new_state, report


def execute_delete(state, name):
    """Удалить фрейм целиком"""
    new_state = deepcopy(state)
    
    if name not in new_state['frames']:
        raise ValueError(f"Фрейм '{name}' не существует")
    
    # Собираем лунки для отчета
    wells = list(new_state['frames'][name].keys())
    
    # Удаляем из индекса
    for well in wells:
        del new_state['_index'][well]
    
    # Удаляем фрейм
    del new_state['frames'][name]
    
    report = f"🗑️ Фрейм '{name}' удален\n"
    if wells:
        report += f"   Освобождено: {', '.join(wells[:5])}"
        if len(wells) > 5:
            report += f" и еще {len(wells)-5}"
    
    return new_state, report


def execute_show(state, target, name=None):
    """Показать информацию подробно"""
    
    # Вспомогательная функция для отрисовки таблицы одного фрейма
    def format_frame_report(f_name, f_wells):
        res = f"🔬 Фрейм '{f_name}':\n"
        res += "   Лунка   Dilution   OD\n"
        # Сортируем лунки (например, A1, A2, B1...)
        for well, data in sorted(f_wells.items()):
            od = f"{data['od']:.3f}" if data['od'] else '--'
            res += f"   {well:<7} {data['dilution']:<10} {od}\n"
        return res

    if target == 'all':
        if not state['frames']:
            return state, "📭 Нет загруженных фреймов"
        
        # Собираем отчеты по всем фреймам через разделитель
        reports = []
        for f_name, f_wells in state['frames'].items():
            reports.append(format_frame_report(f_name, f_wells))
        
        full_report = "\n" + "\n---\n".join(reports)
        
        # Добавим общую статистику в конец
        free = 96 - len(state['_index'])
        full_report += f"\n\n🟢 Свободно лунок: {free}/96"
        return state, full_report

    elif target == 'frame':
        if name not in state['frames']:
            raise ValueError(f"Фрейм '{name}' не существует")
        
        report = format_frame_report(name, state['frames'][name])
        return state, report
    
    elif target == 'cal':
        cal_name = name if name else 'main'
        if cal_name not in state['calibrations']:
            return state, f"❌ Калибровка '{cal_name}' не найдена."
        
        cal_data = state['calibrations'][cal_name]
        
        # Шапка
        report = f"\n{'='*45}\n"
        report += f"📊 ОТЧЕТ ПО КАЛИБРОВКЕ: '{cal_name}'\n"
        report += f"{'='*45}\n"
        
        # 1. Блок Бейзлайнов (Холостые пробы)
        report += "📍 Baseline (Blanks):\n"
        if not cal_data['baseline']:
            report += "   (не заданы)\n"
        else:
            bl_entries = []
            for b_well, data in sorted(cal_data['baseline'].items()):
                val = data.get('od')
                od_str = f"{val:.3f}" if isinstance(val, (int, float)) else "--"
                bl_entries.append(f"{b_well}[{od_str}]")
            
            # Выводим бейзлайны списком по 4 в ряд, чтобы не растягивать вертикаль
            for i in range(0, len(bl_entries), 4):
                report += "   " + " | ".join(bl_entries[i:i+4]) + "\n"
        
        report += f"{'-'*45}\n"
        
        # 2. Блок Стандартов
        report += "🧪 Стандарты концентрации:\n"
        report += f"   {'Лунка':<10} {'Конц. (nM)':<15} {'OD':<10}\n"
        report += f"   {'·'*38}\n"
        
        standards = cal_data['standards']
        if not standards:
            report += "   (не заданы)\n"
        else:
            for well, data in sorted(standards.items()):
                # Берем OD из данных стандарта
                val = data.get('od')
                od_str = f"{val:.3f}" if isinstance(val, (int, float)) else "  --  "
                conc_str = f"{data['conc']:.2f}"
                report += f"   {well:<10} {conc_str:<15} {od_str:<10}\n"
            
        report += f"{'='*45}\n"
        
        # 3. Инфа по аппроксимации
        if cal_data.get('linear_fit'):
            report += f"📈 Результат аппроксимации:\n"
            report += f"   {cal_data['linear_fit']}\n"
            report += f"{'='*45}\n"
            
        return state, report

    return state, "Неизвестная цель для show"



    

