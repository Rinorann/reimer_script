import numpy as np
from sklearn.linear_model import LinearRegression
from copy import deepcopy

def execute_fit(state, linear_min, linear_max, cal_name='main'):
    new_state = deepcopy(state)
    
    if cal_name not in new_state.get('calibrations', {}):
        return state, f"❌ Калибровка '{cal_name}' не найдена."
    
    cal_data = new_state['calibrations'][cal_name]
    
    # 1. Расчет бейзлайна (фона)
    baseline_ods = [d['od'] for d in cal_data.get('baseline', {}).values() if isinstance(d['od'], (int, float))]
    if not baseline_ods:
        return state, "❌ Нет числовых данных OD для бейзлайна! Вы сделали load?"
    
    baseline_value = np.mean(baseline_ods)
    
    # 2. Подготовка точек калибровки
    X_list = []
    y_list = []
    
    for well, data in cal_data.get('standards', {}).items():
        if isinstance(data.get('od'), (int, float)):
            X_list.append(data['conc'])
            y_list.append(data['od'])
            
    if len(X_list) < 2:
        return state, "❌ Нужно как минимум 2 стандарта с загруженными OD для построения прямой."
        
    X = np.array(X_list).reshape(-1, 1)
    # Вычитаем фон из сырых OD стандартов
    y = np.array(y_list) - baseline_value
    
    # 3. Обучаем регрессию
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, y)
    
    # Сохраняем формулу
    formula = f"OD = {slope:.6f}*C + {intercept:.6f}"
    new_state['calibrations'][cal_name]['linear_fit'] = formula
    
    # 4. Формируем начало отчета
    report = f"\n{'='*75}\n"
    report += f"📈 РЕЗУЛЬТАТЫ РАСЧЕТА (Калибровка: '{cal_name}')\n"
    report += f"{'='*75}\n"
    report += f"🔹 Уравнение:   {formula}\n"
    report += f"🔹 R²:          {r2:.4f} " + ("(⚠️ Низкий!)" if r2 < 0.95 else "(✅ Отлично)") + "\n"
    report += f"🔹 Фон (Blank): {baseline_value:.4f}\n"
    report += f"🔹 Диапазон:    [{linear_min} ... {linear_max}]\n"
    report += f"{'-'*75}\n"
    report += f"{'Образец':<15} {'Разведение':<12} {'Сред. OD':<10} {'С(лунки)':<12} {'С(исходная)':<15}\n"
    report += f"{'-'*75}\n"
    
    # 5. Расчет концентраций образцов
    midpoint = (linear_max + linear_min) / 2

    for f_name, f_wells in new_state.get('frames', {}).items():
        # Группируем OD по разведениям
        dil_groups = {}
        for well, data in f_wells.items():
            if isinstance(data.get('od'), (int, float)):
                dil_groups.setdefault(data['dilution'], []).append(data['od'])
        
        if not dil_groups:
            report += f"{f_name:<15} {'(нет данных OD)':<58}\n"
            continue
            
        sample_results = []
        
        for dil, ods in dil_groups.items():
            mean_od = np.mean(ods)
            # x = (y - intercept) / slope (y уже скорректировано на бейзлайн)
            predicted_x = (mean_od - baseline_value - intercept) / slope
            final_conc = predicted_x * dil
            
            in_range = linear_min <= predicted_x <= linear_max
            sample_results.append({
                'dil': dil, 'mean_od': mean_od, 'pred_x': predicted_x, 
                'final_c': final_conc, 'in_range': in_range
            })
            
        # Выбираем лучшее разведение
        valid_results = [r for r in sample_results if r['in_range']]
        
        if valid_results:
            # Ищем то, предсказанная концентрация которого ближе всего к середине диапазона
            best = min(valid_results, key=lambda r: abs(r['pred_x'] - midpoint))
            report += f"{f_name:<15} x{best['dil']:<11} {best['mean_od']:<10.4f} {best['pred_x']:<12.4f} {best['final_c']:<15.4f} ✅\n"
            
            # Сохраняем итоговую концентрацию в стейт фрейма
            for well in f_wells:
                new_state['frames'][f_name]['_result_conc'] = best['final_c']
        else:
            # Если все разведения пролетели мимо линейного диапазона
            best = sample_results[0] # Берем первое для показа
            report += f"{f_name:<15} x{best['dil']:<11} {best['mean_od']:<10.4f} {best['pred_x']:<12.4f} {'ВНЕ ДИАПАЗОНА':<15} ❌\n"

    report += f"{'='*75}\n"
    return new_state, report