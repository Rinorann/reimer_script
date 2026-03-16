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
        """
        Сохраняет загруженный планшет.
        
        Args:
            plate_data (dict): Словарь с данными из Excel {лунка: OD}
            file_name (str, optional): Имя загруженного файла
        """
        cls._loaded_plate = plate_data.copy() if plate_data else {}  # копируем для безопасности
        cls._loaded_file = file_name
    
    @classmethod
    def get_plate(cls):
        """
        Возвращает весь загруженный планшет.
        
        Returns:
            dict: {лунка: OD}
        """
        return cls._loaded_plate.copy()  # возвращаем копию, чтобы не испортили оригинал
    
    @classmethod
    def get_well_od(cls, well):
        """
        Возвращает значение OD для конкретной лунки.
        
        Args:
            well (str): Идентификатор лунки ('A1', 'B3' и т.д.)
            
        Returns:
            float or str: Значение OD или "?????" если лунка не найдена
        """
        return cls._loaded_plate.get(well, "?????")
    
    @classmethod
    def has_well(cls, well):
        """
        Проверяет, есть ли данные для указанной лунки.
        
        Args:
            well (str): Идентификатор лунки
            
        Returns:
            bool: True если лунка существует в загруженных данных
        """
        return well in cls._loaded_plate
    
    # ---------- ИНФОРМАЦИЯ О ЗАГРУЗКЕ ----------
    @classmethod
    def get_loaded_file(cls):
        """Возвращает имя загруженного файла."""
        return cls._loaded_file
    
    @classmethod
    def is_loaded(cls):
        """
        Проверяет, загружен ли планшет.
        
        Returns:
            bool: True если есть данные
        """
        return bool(cls._loaded_plate)
    
    @classmethod
    def get_stats(cls):
        """
        Возвращает статистику по загруженному планшету.
        
        Returns:
            dict: {'total': общее кол-во, 'filled': заполненные, 'empty': пустые}
        """
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
        """Полностью очищает все данные."""
        cls._loaded_plate = {}
        cls._loaded_file = None
    
    # ---------- ДЛЯ ОТЛАДКИ ----------
    @classmethod
    def __repr__(cls):
        """Красивый вывод для отладки."""
        stats = cls.get_stats()
        return f"StateManager(plate={stats['filled']}/{stats['total']} wells, file={cls._loaded_file})"