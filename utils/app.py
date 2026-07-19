# utils/app.py
import sys
import os
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QFileDialog, QTextEdit, 
                             QLineEdit, QTableWidget, QAbstractItemView, QTableWidgetItem,
                             QDialog, QRadioButton, QButtonGroup, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QShortcut, QKeySequence

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from state import State

class CalibrationDialog(QDialog):
    """Всплывающее окно для удобного задания концентраций стандартов"""
    def __init__(self, selected_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка калибровочных стандартов")
        self.resize(380, 220)
        layout = QVBoxLayout(self)
        
        self.lbl_info = QLabel(f"Выделено лунок под стандарты: <b>{selected_count}</b>")
        layout.addWidget(self.lbl_info)
        
        self.radio_same = QRadioButton("Одинаковая концентрация для всех лунок", self)
        self.radio_series = QRadioButton("Автоматический ряд разведений", self)
        self.radio_same.setChecked(True)
        
        self.bg = QButtonGroup(self)
        self.bg.addButton(self.radio_same)
        self.bg.addButton(self.radio_series)
        layout.addWidget(self.radio_same)
        layout.addWidget(self.radio_series)
        
        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.input_base = QLineEdit(self)
        self.input_base.setPlaceholderText("Например: 1.0")
        self.form_layout.addRow("Начальная конц. Fe:", self.input_base)
        
        self.input_step = QLineEdit(self)
        self.input_step.setText("2")
        self.input_step.setEnabled(False)
        self.form_layout.addRow("Шаг / Делитель разведения:", self.input_step)
        layout.addWidget(self.form_widget)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.radio_same.toggled.connect(lambda: self.input_step.setEnabled(False))
        self.radio_series.toggled.connect(lambda: self.input_step.setEnabled(True))

    def get_values(self):
        return {
            "is_series": self.radio_series.isChecked(),
            "base": float(self.input_base.text().strip() or 0),
            "step": float(self.input_step.text().strip() or 1)
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = State()
        self.setWindowTitle("Ferritin Fe Analyzer v4.5 (Individual Mass)")
        self.resize(1200, 850)
        
        self.current_sample_name = None
        self.current_sample_color = None
        self.current_ferritin_mass = 0.0
        
        # --- ШАГ 1: ФОРМА ОБРАЗЦОВ ---
        self.input_name = QLineEdit(self)
        self.input_name.setPlaceholderText("Например: sp1")
        
        self.input_mass = QLineEdit(self)
        self.input_mass.setPlaceholderText("Масса белка (мкг)")
        self.input_mass.setText("100")
        
        self.btn_lock_name = QPushButton("Разметить образец", self)
        self.btn_lock_name.clicked.connect(self.action_lock_sample_name)
        
        self.input_dil = QLineEdit(self)
        self.input_dil.setText("1")
        self.input_dil.setEnabled(False)
        self.btn_add_dilution = QPushButton("Добавить разведение", self)
        self.btn_add_dilution.clicked.connect(self.action_add_dilution_to_state)
        self.btn_add_dilution.setEnabled(False)
        
        self.btn_finish_sample = QPushButton("🔒Зафиксировать образец", self)
        self.btn_finish_sample.clicked.connect(self.action_finish_sample)
        self.btn_finish_sample.setEnabled(False)

        # --- ШАГ 2: ФОРМА КАЛИБРОВКИ ---
        self.btn_add_calib = QPushButton("Разметить калибровку", self)
        self.btn_add_calib.clicked.connect(self.action_add_calibration_point)
        self.btn_lock_calib = QPushButton("🔒 Зафиксировать калибровку", self)
        self.btn_lock_calib.clicked.connect(self.action_lock_calibration)

        # --- ЦЕНТРАЛЬНЫЙ ПЛАНШЕТ ---
        self.plate_table = QTableWidget(8, 12, self)
        self.setup_plate_ui()

        # --- ШАГ 3: ЗАГРУЗКА И РАСЧЕТ ---
        self.btn_load = QPushButton("Загрузить xlsx-файл с Synergy", self)
        self.file_label = QLabel("Файл не выбран", self)
        self.btn_calc = QPushButton("Выполнить расчёт(газик)", self)
        self.btn_export = QPushButton("Сохранить отчет (HTML + График)", self)
        
        self.btn_load.clicked.connect(self.action_choose_file)
        self.btn_calc.clicked.connect(self.action_calculate)
        self.btn_export.clicked.connect(self.action_export_report)
        
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)

        # Холст для графика Matplotlib
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)

        # --- ЛАЙАУТЫ (КОМПОНОВКА) ---
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Левая колонка (Ввод параметров и планшет)
        left_layout.addWidget(QLabel("<b>Шаг 1: Укажи имя образца и массу белка в нём</b>"))
        row_s1_name = QHBoxLayout()
        row_s1_name.addWidget(QLabel("Имя образца:"))
        row_s1_name.addWidget(self.input_name)
        row_s1_name.addWidget(QLabel("Масса белка (мкг):"))
        row_s1_name.addWidget(self.input_mass)
        row_s1_name.addWidget(self.btn_lock_name)
        left_layout.addLayout(row_s1_name)
        
        row_s1_dil = QHBoxLayout()
        row_s1_dil.addWidget(QLabel("Коэф. разведения для выделенных лунок:"))
        row_s1_dil.addWidget(self.input_dil)
        row_s1_dil.addWidget(self.btn_add_dilution)
        left_layout.addLayout(row_s1_dil)
        left_layout.addWidget(self.btn_finish_sample)
        
        left_layout.addWidget(QLabel("<hr>"))
        left_layout.addWidget(QLabel("<b>Шаг 2: Разметка калибровочной кривой</b>"))
        row_s2 = QHBoxLayout()
        row_s2.addWidget(self.btn_add_calib)
        row_s2.addWidget(self.btn_lock_calib)
        left_layout.addLayout(row_s2)
        
        left_layout.addWidget(QLabel("<hr>"))
        left_layout.addWidget(self.plate_table)
        left_layout.addWidget(QLabel("<hr>"))
        
        left_layout.addWidget(QLabel("<b>Шаг 3: Расчёт</b>"))
        left_layout.addWidget(self.btn_load)
        left_layout.addWidget(self.file_label)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(self.btn_export)
        left_layout.addWidget(self.result_output)

        # Правая колонка (Визуализация графика с верхней симметрией)
        right_layout.addWidget(QLabel("<h3>Калибровочная прямая</h3>"))
        right_layout.addWidget(self.canvas)
        right_layout.addStretch()  # Распорка выталкивает график наверх на уровень Шага 1
        
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        buttons_list = [self.btn_load, self.btn_calc, self.btn_export, self.btn_lock_name, 
                        self.btn_add_dilution, self.btn_finish_sample, self.btn_add_calib, self.btn_lock_calib]
        for btn in buttons_list:
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        QShortcut(QKeySequence(Qt.Key.Key_Return), self).activated.connect(self.shortcut_enter_pressed)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self).activated.connect(self.shortcut_enter_pressed)

    def setup_plate_ui(self):
        rows_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.plate_table.setVerticalHeaderLabels(rows_letters)
        self.plate_table.setHorizontalHeaderLabels([str(i) for i in range(1, 13)])
        
        # Настройка высоты строк
        for i in range(8): 
            self.plate_table.setRowHeight(i, 45)
            
        self.plate_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.plate_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # 🔑 ИСПРАВЛЕННЫЙ РЕЖИМ РАСТЯЖЕНИЯ КОЛОНОК
        # В PyQt6 правильный путь лежит через импорт QHeaderView
        from PyQt6.QtWidgets import QHeaderView
        self.plate_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Инициализируем пустые ячейки
        for row in range(8):
            for col in range(12): 
                self.plate_table.setItem(row, col, QTableWidgetItem(""))

    def shortcut_enter_pressed(self):
        if self.btn_lock_name.isEnabled() and self.input_name.text().strip():
            self.action_lock_sample_name()
        elif self.btn_add_dilution.isEnabled():
            self.action_add_dilution_to_state()

    def action_lock_sample_name(self):
        name = self.input_name.text().strip()
        if not name: return
        try:
            mass = float(self.input_mass.text().strip())
        except ValueError:
            self.result_output.append("⚠️ Масса ферритина должна быть числом!")
            return

        self.current_sample_name = name
        self.current_ferritin_mass = mass
        self.current_sample_color = QColor(random.randint(160, 255), random.randint(160, 255), random.randint(160, 255))
        
        self.state.samples[name] = {
            "ferritin_mass": mass,
            "dilutions": {}
        }
        
        self.input_name.setEnabled(False)
        self.input_mass.setEnabled(False)
        self.btn_lock_name.setEnabled(False)
        self.input_dil.setEnabled(True)
        self.btn_add_dilution.setEnabled(True)
        self.btn_finish_sample.setEnabled(True)
        self.input_dil.setFocus()
        self.result_output.append(f"🔒 Образец: <b>{name}</b> (Внесено белка: {mass} мкг). Задайте разведения.")

    def action_add_dilution_to_state(self):
        dil_text = self.input_dil.text().strip()
        if not dil_text or not self.current_sample_name: return
        selected_items = self.plate_table.selectedItems()
        if not selected_items: return

        wells_list = []
        rows_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for item in selected_items:
            well_name = f"{rows_letters[item.row()]}{item.column() + 1}"
            wells_list.append(well_name)
            item.setText(f"{self.current_sample_name}\n(1:{dil_text})")
            item.setBackground(QBrush(self.current_sample_color))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        self.state.samples[self.current_sample_name]["dilutions"][dil_text] = wells_list
        self.result_output.append(f"  ↳ Добавлено разведение 1:{dil_text} для лунок {sorted(wells_list)}")
        self.plate_table.clearSelection()
        self.input_dil.setText("1")
        self.input_dil.setFocus()

    def action_finish_sample(self):
        self.result_output.append(f"✅ Образец <b>{self.current_sample_name}</b> полностью сохранен в разметку.\n")
        self.current_sample_name = None
        self.current_sample_color = None
        
        self.input_name.setEnabled(True)
        self.input_mass.setEnabled(True)
        self.btn_lock_name.setEnabled(True)
        self.input_dil.setEnabled(False)
        self.btn_add_dilution.setEnabled(False)
        self.btn_finish_sample.setEnabled(False)
        self.input_name.clear()
        self.input_mass.setText("100")
        self.input_name.setFocus()

    def action_add_calibration_point(self):
        selected_items = self.plate_table.selectedItems()
        if not selected_items: return
        dialog = CalibrationDialog(len(selected_items), self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        try: data = dialog.get_values()
        except ValueError: return

        calib_color = QColor(255, 223, 128)
        rows_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        current_conc = data["base"]
        sorted_items = sorted(selected_items, key=lambda x: (x.row(), x.column()))

        for item in sorted_items:
            well_name = f"{rows_letters[item.row()]}{item.column() + 1}"
            item.setText(f"Std: {round(current_conc, 2)}")
            item.setBackground(QBrush(calib_color))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            self.state.calibration_points.append({"concentration": current_conc, "wells": [well_name]})
            if data["is_series"]:
                if data["step"] > 1: current_conc /= data["step"]
                else: current_conc += data["step"]
        self.plate_table.clearSelection()

    def action_lock_calibration(self):
        if not self.state.calibration_points: return
        self.btn_add_calib.setEnabled(False)
        self.btn_lock_calib.setEnabled(False)
        self.result_output.append("🔒 Матрица стандартов Fe зафиксирована.")

    def action_choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть Excel Synergy", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                self.state.load_plate(file_path)
                self.file_label.setText(f"✅ Загружен: {os.path.basename(file_path)}")
            except Exception as e:
                self.result_output.append(f"Ошибка: {str(e)}")

    def draw_graph(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        x_pts, y_pts = [], []
        for pt in self.state.calibration_points:
            ods = self.state._get_od_of_well(pt["wells"])
            if ods:
                x_pts.append(pt["concentration"])
                y_pts.append(sum(ods) / len(ods))

        if x_pts and self.state.regression_coef:
            ax.scatter(x_pts, y_pts, color='orange', label='Стандарты', zorder=5)
            k = self.state.regression_coef["k"]
            b = self.state.regression_coef["b"]
            x_line = [min(x_pts), max(x_pts)]
            y_line = [k * x + b for x in x_line]
            ax.plot(x_line, y_line, color='blue', linestyle='--', label=f'OD = {k:.3f}*x + {b:.3f}')
            ax.set_title(f"Калибровка Fe (R² = {self.state.regression_coef['R2']:.4f})")
            ax.set_xlabel("Концентрация Fe")
            ax.set_ylabel("OD")
            ax.legend()
            ax.grid(True, linestyle=':', alpha=0.6)
        self.canvas.draw()

    def action_calculate(self):
        if not self.state.wells or not self.state.samples: return
        calculated_data = self.state.calculate_samples()
        self.draw_graph()

        self.result_output.append("\n========================================")
        self.result_output.append("📈 <b>РЕЗУЛЬТАТЫ С ИНДИВИДУАЛЬНОЙ МАССОЙ БЕЛКА</b>")
        self.result_output.append("========================================")
        
        for sample_name, info in calculated_data.items():
            wells_str = ", ".join(info['wells'])
            self.result_output.append(
                f"• <b>{sample_name}</b> (Внесено белка: {info['ferritin_mass']} мкг)<br>"
                f"  ↳ Лучшее разведение: <b>1:{info['chosen_dil']}</b> (Лунки: [{wells_str}])<br>"
                f"  ↳ Сырой OD лучшей лунки: <b>{info['chosen_raw_od']:.3f}</b><br>"
                f"  ↳ Итоговая конц. Fe в исходнике: <b>{info['fe_conc']:.3f}</b> мкг/мл<br>"
                f"  ↳ 💎 <b>Атомов Fe на молекулу ферритина: <span style='color: red;'><b>{info['atoms_fe']}</b></span></b><br>"
            )

    def action_export_report(self):
        if not self.state.wells or not self.state.samples: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "Ферритин_Отчет.html", "HTML Files (*.html)")
        if not file_path: return

        try:
            import io, base64
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            graph_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            calculated_data = self.state.calculate_samples()
            coef = self.state.regression_coef or {"k": 0.0, "b": 0.0, "R2": 0.0, "center_od": 0.0}

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Отчет биохимического анализа ферритина</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f9f9f9; }}
                    .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #2c3e50; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    .highlight {{ font-weight: bold; color: #c0392b; }}
                    .graph-container {{ text-align: center; margin: 30px 0; }}
                    .info-block {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Отчет: Анализ количества атомов Fe в Ферритине</h1>
                    <div class="info-block">
                        <p><b>Уравнение прямой:</b> OD = {coef['k']:.4f} * Концентрация + ({coef['b']:.4f})</p>
                        <p><b>Качество аппроксимации (R²):</b> {coef['R2']:.4f}</p>
                        <p><b>Центр детекции прибора (OD):</b> {coef['center_od']:.3f}</p>
                    </div>
                    <div class="graph-container">
                        <img src="data:image/png;base64,{graph_base64}" alt="Калибровочный график">
                    </div>
                    <h2>🧪 Таблица результатов</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Имя семпла</th>
                                <th>Внесено ферритина (мкг)</th>
                                <th>Выбранное разведение</th>
                                <th>Лунки</th>
                                <th>Сырой OD</th>
                                <th>Fe в исходнике (мкг/мл)</th>
                                <th>Атомов Fe на ферритин</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for name, info in calculated_data.items():
                html_content += f"""
                            <tr>
                                <td><b>{name}</b></td>
                                <td>{info['ferritin_mass']}</td>
                                <td>1:{info['chosen_dil']}</td>
                                <td>[{", ".join(info['wells'])}]</td>
                                <td>{info['chosen_raw_od']:.4f}</td>
                                <td>{info['fe_conc']:.4f}</td>
                                <td class="highlight">{info['atoms_fe']}</td>
                            </tr>
                """
            html_content += "</tbody></table></div></body></html>"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.result_output.append(f"💾 Отчет сохранен: {file_path}")
        except Exception as e:
            self.result_output.append(f"❌ Ошибка экспорта: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())