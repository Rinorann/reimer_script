"""
StateManager - центральное хранилище данных приложения.
Позволяет всем модулям иметь доступ к загруженному планшету.
"""

class StateManager:
    """Менеджер состояния приложения. Все методы классовые - не нужно создавать экземпляры."""
    
    # ---------- ПРИВАТНЫЕ ПЕРЕМЕННЫЕ КЛАССА ----------
    _loaded_plate = {}      # словарь с данными из Excel: {'A1': 0.345, 'B2': 1.234, ...}
    _loaded_file = None      # имя загруженного файла (для информации)
    
    # ---------- РАБОТА С ПЛАНШЕТОМ ----------
    @classmethod
    def set_plate(cls, plate_data, file_name=None):
        """Сохраняет загруженный планшет."""
        cls._loaded_plate = plate_data.copy() if plate_data else {} 
        cls._loaded_file = file_name
    
    @classmethod
    def get_plate(cls):
        """Возвращает весь загруженный планшет."""
        return cls._loaded_plate.copy()
    
    @classmethod
    def get_well_od(cls, well):
        """Возвращает значение OD для конкретной лунки."""
        return cls._loaded_plate.get(well, "?????")
    
    @classmethod
    def has_well(cls, well):
        """Проверяет, есть ли данные для указанной лунки."""
        return well in cls._loaded_plate
    
    # ---------- ИНФОРМАЦИЯ О ЗАГРУЗКЕ ----------
    @classmethod
    def get_loaded_file(cls):
        return cls._loaded_file
    
    @classmethod
    def is_loaded(cls):
        return bool(cls._loaded_plate)
    
    @classmethod
    def get_stats(cls):
        total = len(cls._loaded_plate)
        filled = sum(1 for v in cls._loaded_plate.values() if v is not None and v != "?????")
        empty = total - filled
        return {
            'total': total,
            'filled': filled,
            'empty': empty,
            'file': cls._loaded_file
        }
    
    # ---------- ОЧИСТКА ----------
    @classmethod
    def clear(cls):
        cls._loaded_plate = {}
        cls._loaded_file = None

    # ---------- ИНТЕГРАЦИЯ С CLI И WIZARD (НОВЫЙ ФУНКЦИОНАЛ) ----------
    
    @classmethod
    def init_state(cls, config=None):
        """
        Создает начальный словарь состояния (state) для CLI.
        Если передан config из виджетов, автоматически генерирует черновики (drafts)
        для режима Wizard.
        """
        state = {
            'frames': {},
            'calibrations': {},
            '_index': {},
            'drafts': []
        }
        
        if not config:
            return state
            
        # Распаковываем глобальные настройки
        reps = config.get('global', {}).get('replicates', 3)
        blanks = config.get('global', {}).get('blanks_count', 3)
        
        # 1. Создаем черновик для Калибровки
        cal_points = config.get('calibration', {}).get('points', [])
        unit = config.get('calibration', {}).get('unit', 'uM')
        if cal_points:
            cal_draft = {
                'id': 'cal_main',
                'name': 'Калибровка (main)',
                'type': 'cal',
                'tasks': []
            }
            for pt in cal_points:
                cal_draft['tasks'].append({
                    'label': f"Стандарт {pt} {unit}",
                    'needed': reps,
                    'done': False,
                    'wells': [],
                    'meta': {'conc': pt} # сохраняем концентрацию для экзекьютора
                })
            state['drafts'].append(cal_draft)
            
        # 2. Создаем черновик для Бейзлайна
        if blanks > 0:
            bl_draft = {
                'id': 'bl_main',
                'name': 'Фон (Baseline)',
                'type': 'bl',
                'tasks': [{
                    'label': 'Буфер (пустые лунки)',
                    'needed': blanks,
                    'done': False,
                    'wells': []
                }]
            }
            state['drafts'].append(bl_draft)
            
        # 3. Создаем черновики для Образцов
        dilutions = config.get('dilutions', [1.0])
        for i, sample in enumerate(config.get('samples', [])):
            s_draft = {
                'id': f"sample_{i}",
                'name': sample.get('name', f"Sample {i+1}"),
                'type': 'sample',
                'tasks': []
            }
            for dil in dilutions:
                s_draft['tasks'].append({
                    'label': f"Разведение x{dil}",
                    'needed': reps,
                    'done': False,
                    'wells': [],
                    'meta': {'dilution': dil} # сохраняем разведение
                })
            state['drafts'].append(s_draft)
            
        return state

    @classmethod
    def sync_ods_to_state(cls, state):
        """
        Пробегается по размеченному state и подтягивает значения OD 
        из загруженного Excel-планшета (_loaded_plate).
        Вызывай эту функцию в экзекьюторе команды 'load'.
        """
        if not cls.is_loaded():
            return state, "⚠️ Планшет не загружен. Данные OD не обновлены."
            
        updated_count = 0
        
        # Обновляем образцы
        for f_name, f_data in state.get('frames', {}).items():
            for well, well_info in f_data.items():
                if cls.has_well(well):
                    well_info['od'] = cls.get_well_od(well)
                    updated_count += 1
                    
        # Обновляем калибровки
        for c_name, c_data in state.get('calibrations', {}).items():
            # Стандарты
            for well, well_info in c_data.get('standards', {}).items():
                if cls.has_well(well):
                    well_info['od'] = cls.get_well_od(well)
                    updated_count += 1
            # Бейзлайны
            for well, well_info in c_data.get('baseline', {}).items():
                if cls.has_well(well):
                    well_info['od'] = cls.get_well_od(well)
                    updated_count += 1
                    
        return state, f"✅ Значения OD успешно подтянуты для {updated_count} лунок."

    # ---------- ДЛЯ ОТЛАДКИ ----------
    @classmethod
    def __repr__(cls):
        stats = cls.get_stats()
        return f"StateManager(plate={stats['filled']}/{stats['total']} wells, file={cls._loaded_file})"