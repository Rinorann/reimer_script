from copy import deepcopy
from ..parsers import parse_wells 
from .well_executor import execute_load
def execute_wizard(state):
    """
    Интерактивный мастер разметки (Режим долбоёба).
    Итерируется по drafts, запрашивает лунки и сразу подтягивает OD через execute_load.
    """
    new_state = deepcopy(state)
    drafts = new_state.get('drafts', [])
    
    if not drafts:
        return state, "⚠️ Черновики не найдены. Сначала настрой эксперимент в виджетах (UI)."

    print("\n" + "="*55)
    print("🧙 МАСТЕР РАЗМЕТКИ ПЛАНШЕТА (Wizard)")
    print("Команды: 'undo' - шаг назад, 'exit' - пауза/выход, 'skip' - пропустить")
    print("="*55)

    for draft in drafts:
        # Проверяем, есть ли в этом драфте незавершенные задачи
        tasks_to_do = [t for t in draft['tasks'] if not t['done']]
        if not tasks_to_do:
            continue

        print(f"\n📂 РАБОТАЕМ С БЛОКОМ: {draft['name']}")

        for task in draft['tasks']:
            if task['done']:
                continue

            # Бесконечный цикл для конкретной задачи, пока не введем правильно
            while True:
                print(f"\n📍 Задача: {task['label']}")
                print(f"   Нужно выделить лунок: {task['needed']}")
                
                user_input = input("   Введите диапазон (напр. A1:A3) > ").strip().lower()

                # --- ОБРАБОТКА СПЕЦ-КОМАНД ---
                if user_input == 'exit':
                    return new_state, "🚪 Выход из мастера. Прогресс сохранен. Напиши 'wizard', чтобы продолжить."

                if user_input == 'skip':
                    print("⏭️ Пропущено.")
                    break

                if user_input == 'undo':
                    print("🔄 Отмена шага внутри визарда пока в разработке. Если ошибся - выйди (exit) и поправь через CLI.")
                    continue

                # --- ОСНОВНАЯ ЛОГИКА ---
                try:
                    # 1. Парсим лунки (используем твой парсер)
                    wells = parse_wells(user_input) 
                    
                    # 2. Проверка количества
                    if len(wells) != task['needed']:
                        print(f"❌ Ошибка: Вы ввели {len(wells)} лунок, а нужно {task['needed']}.")
                        continue

                    # 3. Проверка на занятость (нет ли пересечений с уже размеченным)
                    overlap = [w for w in wells if w in new_state.get('_index', {})]
                    if overlap:
                        print(f"❌ Ошибка: Лунки {overlap} уже заняты!")
                        continue

                    # 4. ПОДТЯГИВАЕМ OD ЧЕРЕЗ ТВОЙ execute_load
                    data_to_fill = {}
                    for w in wells:
                        try:
                            # Пытаемся достать реальную цифру из StateManager
                            data_to_fill[w] = execute_load(w)
                        except ValueError:
                            # Если вылетела твоя ошибка (планшет не загружен), ставим заглушку
                            data_to_fill[w] = "?????"

                    # 5. ФИКСИРУЕМ РЕЗУЛЬТАТ В STATE
                    task['wells'] = wells
                    task['done'] = True
                    
                    # Обновляем глобальный индекс лунок
                    owner_name = f"{draft['name']} ({task['label']})"
                    if '_index' not in new_state:
                        new_state['_index'] = {}
                    for w in wells:
                        new_state['_index'][w] = owner_name

                    # Раскладываем данные по нужным словарям в зависимости от типа драфта
                    if draft['type'] == 'sample':
                        f_name = draft['name']
                        new_state.setdefault('frames', {}).setdefault(f_name, {})
                        dil = task['meta']['dilution']
                        for w in wells:
                            new_state['frames'][f_name][w] = {
                                'dilution': dil, 
                                'od': data_to_fill[w] # <--- OD легли на место
                            }
                    
                    elif draft['type'] == 'cal':
                        c_name = 'main'
                        cal_node = new_state.setdefault('calibrations', {}).setdefault(c_name, {'standards': {}, 'baseline': {}})
                        conc = task['meta']['conc']
                        for w in wells:
                            cal_node['standards'][w] = {
                                'conc': conc, 
                                'od': data_to_fill[w] # <--- OD легли на место
                            }

                    elif draft['type'] == 'bl':
                        c_name = 'main'
                        cal_node = new_state.setdefault('calibrations', {}).setdefault(c_name, {'standards': {}, 'baseline': {}})
                        for w in wells:
                            cal_node['baseline'][w] = {
                                'od': data_to_fill[w] # <--- OD легли на место
                            }

                    # Даем красивый фидбек
                    print(f"✅ Готово: {user_input} закреплены за {task['label']}")
                    if any(val != "?????" for val in data_to_fill.values()):
                        print("   (OD успешно подтянуты из планшета 📊)")
                    else:
                        print("   (OD пока пустые, сделайте load позже ⏳)")
                        
                    break # Выходим из while True и идем к следующей задаче в цикле for

                except Exception as e:
                    print(f"⚠️ Ошибка ввода или парсинга: {e}. Попробуйте еще раз.")

    return new_state, "✨ Разметка планшета полностью завершена! Вызови 'show', чтобы полюбоваться."