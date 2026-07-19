# utils/app.py
import sys
import os
import random  # Для генерации случайных цветов
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QFileDialog, QTextEdit, 
                             QLineEdit, QTableWidget, QAbstractItemView, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

# Импортируем твой класс State из соседнего файла utils/state.py
from state import State

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = State()  # Твой класс

        self.setWindowTitle("Yeast Analyzer v1.5 (Strict Protected Plate)")
        self.resize(750, 700)
        
        self.sample_colors = {}
        self.occupied_wells = set()
        
        # --- ФОРМА ДОБАВЛЕНИЯ ОБРАЗЦА ---
        self.input_name = QLineEdit(self)
        self.input_name.setPlaceholderText("Например: Штамм_А")
        
        self.input_dil = QLineEdit(self)
        self.input_dil.setPlaceholderText("1")
        self.input_dil.setText("1")
        
        # Интерактивный планшет 8х12
        self.plate_table = QTableWidget(8, 12, self)
        self.setup_plate_ui()

        self.btn_add_sample = QPushButton("➕ Добавить образец и закрасить лунки", self)
        self.btn_add_sample.clicked.connect(self.action_add_sample_to_state)

        # --- КНОПКИ УПРАВЛЕНИЯ ФАЙЛОМ И РАСЧЕТОМ ---
        self.btn_load = QPushButton("📂 1. Загрузить Excel с прибора", self)
        self.file_label = QLabel("Файл не выбран", self)
        self.btn_calc = QPushButton("🧮 2. Рассчитать OD образцов", self)
        
        self.btn_load.clicked.connect(self.action_choose_file)
        self.btn_calc.clicked.connect(self.action_calculate)
        
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)

        # --- КОМПОНОВКА (LAYOUTS) ---
        main_layout = QVBoxLayout()
        form_layout = QVBoxLayout()
        
        form_layout.addWidget(QLabel("<b>Шаг 1: Задайте имя и разведение</b>"))
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Имя образца:"))
        row1.addWidget(self.input_name)
        row1.addWidget(QLabel("Разведение:"))
        row1.addWidget(self.input_dil)
        form_layout.addLayout(row1)
        
        form_layout.addWidget(QLabel("<b>Шаг 2: Выделите лунки на планшете мышкой:</b>"))
        form_layout.addWidget(self.plate_table)
        form_layout.addWidget(self.btn_add_sample)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(QLabel("<hr>"))
        main_layout.addWidget(self.btn_load)
        main_layout.addWidget(self.file_label)
        main_layout.addWidget(self.btn_calc)
        main_layout.addWidget(self.result_output)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setup_plate_ui(self):
        """Настраивает QTableWidget под внешний вид лабораторного планшета"""
        rows_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.plate_table.setVerticalHeaderLabels(rows_letters)
        self.plate_table.setHorizontalHeaderLabels([str(i) for i in range(1, 13)])
        
        for i in range(12):
            self.plate_table.setColumnWidth(i, 55)
        for i in range(8):
            self.plate_table.setRowHeight(i, 40)
            
        self.plate_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.plate_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Инициализируем пустые ячейки, чтобы у них изначально был флаг "можно выделить"
        for row in range(8):
            for col in range(12):
                item = QTableWidgetItem("")
                self.plate_table.setItem(row, col, item)

    def generate_pastel_color(self):
        return QColor(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

    def action_add_sample_to_state(self):
        """Слот: собирает выделенные лунки, красит их и блокирует от повторного выбора"""
        name = self.input_name.text().strip()
        if not name:
            self.result_output.append("⚠️ Введите имя образца!")
            return
            
        try:
            dil = float(self.input_dil.text().strip())
        except ValueError:
            self.result_output.append("⚠️ Разведение должно быть числом!")
            return

        selected_items = self.plate_table.selectedItems()
        if not selected_items:
            self.result_output.append("⚠️ Выделите хотя бы одну лунку на планшете мышкой!")
            return

        if name not in self.sample_colors:
            self.sample_colors[name] = self.generate_pastel_color()
        color = self.sample_colors[name]

        wells_list = []
        rows_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for item in selected_items:
            row = item.row()
            col = item.column()
            well_name = f"{rows_letters[row]}{col + 1}"
            
            wells_list.append(well_name)
            
            # Меняем текст и цвет
            item.setText(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QBrush(QColor("black")))
            item.setBackground(QBrush(color))
            
            # ЖЕСТКАЯ БЛОКИРОВКА: Забираем у ячейки флаг "Selectable" (выделяемая)
            # Теперь мышка будет просто игнорировать эту ячейку при выделении прямоугольником
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        # Пишем в бэкенд (класс State)
        self.state.samples[name] = {
            "dil": dil,
            "wells": wells_list
        }
        
        self.result_output.append(f"✅ Добавлен образец: <b>{name}</b> (dil={dil}, лунки={sorted(wells_list)})")
        
        self.plate_table.clearSelection()
        self.input_name.clear()
        self.input_dil.setText("1")

    def action_choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть Excel Synergy", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                self.file_label.setText(f"✅ Загружен: {os.path.basename(file_path)}")
                self.result_output.append(f" Спектрофотометр прочитан.")
            except Exception as e:
                self.file_label.setText("❌ Ошибка загрузки!")
                self.result_output.append(f"Ошибка парсинга: {str(e)}")

    def action_calculate(self):
        if not self.state.wells:
            self.result_output.append("⚠️ Сначала загрузите файл с данными прибора!")
            return
        if not self.state.samples:
            self.result_output.append("⚠️ Сначала разметьте планшет!")
            return
            
        calculated_data = self.state.calculate_samples()
        
        self.result_output.append("\n=== РЕЗУЛЬТАТЫ РАСЧЕТА ===")
        for name, info in calculated_data.items():
            wells_str = ", ".join(info['wells'])
            final_od = info.get('final_od', 'Нет данных')
            self.result_output.append(
                f"• <b>{name}</b> (Разведение: {info['dil']}, Лунки: {wells_str})<br>"
                f"  Финальный OD: <span style='color: green;'><b>{final_od}</b></span><br>"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())