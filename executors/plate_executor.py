from utils import load_full_plate
from utils import StateManager
def execute_load_full(state, file_path):
    """
    Загружает данные планшета из Excel и сохраняет в глобальную переменную.
    Не изменяет state, только загружает данные в память.
    """

    try:
        
        # Загружаем данные планшета
        plate_data = load_full_plate(file_path)
        
        # 👇 СОХРАНЯЕМ В STATEMANAGER (вместо глобальной переменной)
        StateManager.set_plate(plate_data, file_path)
        # Статистика через StateManager
        stats = StateManager.get_stats()
        
        
        # Формируем отчет
        report = f"📥 Загружен планшет: {file_path}\n"
        report += f"   ✅ Всего лунок: {stats['total']}\n"
        report += f"   📊 Значений OD: {stats['filled']}\n"
        report += f"   ⚠️ Пустых/нет данных: {stats['empty']}\n"
        
        if stats['filled'] == 0:
            report += "   ⚠️ ВНИМАНИЕ: Не найдено ни одного значения OD!\n"
        
        return state, report  # state не меняется
        
    except Exception as e:
        raise ValueError(f"Ошибка при загрузке планшета: {e}")