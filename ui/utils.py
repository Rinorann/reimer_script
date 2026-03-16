# Константы для перевода единиц и стандартные молярные массы
UNIT_TO_M = {"M": 1.0, "mM": 1e-3, "uM": 1e-6, "µM": 1e-6}

DEFAULT_MW = {
    "HCl": 36.46,              
    "NaOH": 39.997,
    "KMnO4": 158.034,
    "Ferrozine": 492.50,       
    "Ammonium acetate": 77.08,
    "Ascorbic acid": 176.12,
}

IRON_SALTS = {
    "FeSO4": 151.91,
    "FeCl3": 162.20,
    "Соль Мора": 392.14,               
    "Цитрат железа (II)": 245.95,      
    "Цитрат железа (III)": 244.94,     
    "Другое": None,
}

def safe_float(x, default=0.0):
    """Безопасный парсинг чисел (защита от запятых вместо точек)"""
    if x is None:
        return default
    try:
        return float(x)
    except Exception:
        try:
            return float(str(x).replace(",", "."))
        except Exception:
            return default

def adjust_mw_for_hydration(mw_anhydrous, n_h2o):
    """Корректировка молярной массы на количество молекул воды"""
    return mw_anhydrous + 18.01528 * max(0, int(n_h2o))