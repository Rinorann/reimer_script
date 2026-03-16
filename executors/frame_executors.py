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
    """Показать информацию"""
    if target == 'all':
        if not state['frames']:
            return state, "📭 Нет фреймов"
        
        report = "📋 ФРЕЙМЫ:\n"
        for frame_name, wells in state['frames'].items():
            dilutions = set(w['dilution'] for w in wells.values())
            report += f"  • '{frame_name}': {len(wells)} лунок, dil: {sorted(dilutions)}\n"
        
        free = 96 - len(state['_index'])
        report += f"\n🟢 Свободно лунок: {free}/96"
        
    elif target == 'frame':
        if name not in state['frames']:
            raise ValueError(f"Фрейм '{name}' не существует")
        
        wells = state['frames'][name]
        report = f"🔬 Фрейм '{name}':\n"
        report += "   Лунка  Dilution  OD\n"
        for well, data in sorted(wells.items()):
            od = f"{data['od']:.3f}" if data['od'] else '--'
            report += f"   {well:<6} {data['dilution']:<8} {od}\n"
    
    return state, report



    

