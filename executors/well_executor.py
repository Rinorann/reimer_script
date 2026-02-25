from utils import StateManager
def execute_load(well):
    """
    Получает OD из загруженного планшета через StateManager.
    """
    if not StateManager.is_loaded():
        raise ValueError("Планшет не загружен! Сначала выполните load")
    
    return StateManager.get_well_od(well)