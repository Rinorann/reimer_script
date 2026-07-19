from openpyxl import load_workbook
class State:
    def __init__(self):
        self.wells = {} # dict well:OD
        self.samples = {} #dict sample:qualities(dil, wells)
    def load_plate(self, file_path, sheet_name='Sheet1'):
        #TODO: изучить выход синерджи и придумать наиболее стабильный парсер
        '''
        принимает на вход путь к файлу с синерджи и название листа в нём.
        выдаёт словарь типа 'A1': od для всего планшета 8x12. 
        '''
        wb = load_workbook(file_path, data_only=True)
        ws = wb[sheet_name]
        
        # 1. Ищем "Результаты" в колонке A
        results_row = None
        for row in range(1, 150):
            if ws.cell(row=row, column=1).value == "Результаты":
                results_row = row
                break
        
        if results_row is None:
            raise ValueError("Не найдено слово 'Результаты' в колонке A")
        
        # 2. A1 планшета = строка results_row + 4, колонка 3 (C)
        a1_row = results_row + 4
        a1_col = 3  # C = 3
        
        plate_data = {}
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        for i, row_letter in zip(range(0, 32, 5), rows): # целится по read 2:550 по каждой букве в планшете
            for col in range(12):  # 12 колонок планшета
                well = f"{row_letter}{col+1}"
                od_value = ws.cell(
                    row=a1_row + i,           # A -> +0, B -> +1, C -> +2...
                    column=a1_col + col       # 1я колонка -> +0, 2я -> +1...
                ).value
                plate_data[well] = od_value
        
        wb.close()
        self.wells = plate_data
    def _get_od_of_well(self, wells:list):
        """
        Превращает массив названий ячеек в массив их OD
        """
        ods = []
        for well in wells:
            if well in self.wells:
                val = self.wells[well]
                if isinstance(val, (float, int)):
                    ods.append(val)
        return ods


    def calculate_samples(self):
        """
        Обрабатывает dict self.samples, извлекая сырые OD из self.wells,
        рассчитывает среднее значение с учетом разведения и сохраняет 
        результаты расчета прямо внутрь структуры образцов.
        """
        for sample_name in self.samples.keys():
            wells = self.samples[sample_name]['wells']
            ods = self._get_od_of_well(wells)
            dil = self.samples[sample_name]['dil']
            self.samples[sample_name]['final_od'] = sum(ods)/len(ods) *dil
    
        