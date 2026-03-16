import ipywidgets as W
from IPython.display import display
from .utils import DEFAULT_MW
from .base_widgets import StockOrPowderWidget, IronStandardWidget
from .blocks import SampleBlock, DilutionBlock, CalibrationBlock

class ReimerApp:
    def __init__(self):
        # 1. Глобальные настройки
        self.n_samples = W.IntText(value=1, description="Образцов:", layout=W.Layout(width="220px"))
        self.replicates = W.IntText(value=3, description="Повторов:", layout=W.Layout(width="220px"))
        self.blanks = W.IntText(value=3, description="Бейзлайнов:", layout=W.Layout(width="220px"))
        self.V_sample = W.FloatText(value=100.0, description="V aliquot (µL):", layout=W.Layout(width="240px"))

        # 2. Динамические блоки
        self.samples_box = W.VBox()
        self.sample_blocks = []
        self._rebuild_samples()
        self.n_samples.observe(lambda ch: self._rebuild_samples(), names="value")

        self.dilution_block = DilutionBlock()
        self.cal_block = CalibrationBlock()

        # 3. Реактивы
        self.reag_hcl = StockOrPowderWidget("HCl (источник для 10mM и 1.4M)", default_mw=DEFAULT_MW["HCl"], allow_hydration=False, default_type="сток")
        self.reag_naoh = StockOrPowderWidget("NaOH (для 50 mM)", default_mw=DEFAULT_MW["NaOH"], allow_hydration=True, default_type="порошок")
        self.reag_kmno4 = StockOrPowderWidget("KMnO4 (для 4.5% w/v)", default_mw=DEFAULT_MW["KMnO4"], allow_hydration=False, default_type="порошок")
        self.reag_ferrozine = StockOrPowderWidget("Ferrozine (6.5 mM, без неокупорина)", default_mw=DEFAULT_MW["Ferrozine"], allow_hydration=True, default_type="порошок")
        self.reag_nh4oac = StockOrPowderWidget("Аммоний ацетат (2.5 M)", default_mw=DEFAULT_MW["Ammonium acetate"], allow_hydration=True, default_type="порошок")
        self.reag_asc = StockOrPowderWidget("Аскорбиновая кислота (1 M)", default_mw=DEFAULT_MW["Ascorbic acid"], allow_hydration=True, default_type="порошок")
        self.iron_widget = IronStandardWidget()

        self._build_ui()

    def _rebuild_samples(self):
        n = max(1, int(self.n_samples.value))
        # Сохраняем введенные имена, если они были
        saved_names = [b.name.value for b in self.sample_blocks]
        
        self.sample_blocks = []
        for i in range(n):
            name = saved_names[i] if i < len(saved_names) else None
            self.sample_blocks.append(SampleBlock(i, saved_name=name))
        
        self.samples_box.children = [b.box for b in self.sample_blocks]

    def _build_ui(self):
        global_box = W.VBox([
            W.HTML("<h3>Параметры эксперимента (Riemer et al., 2004)</h3>"),
            W.HBox([self.n_samples, self.replicates, self.blanks]),
            W.HBox([self.V_sample]),
            self.dilution_block.box
        ])

        samples_accordion = W.Accordion(children=[self.samples_box])
        samples_accordion.set_title(0, "Образцы")

        cal_accordion = W.Accordion(children=[self.cal_block.box])
        cal_accordion.set_title(0, "Калибровка")

        reag_accordion = W.Accordion(children=[
            W.VBox([self.reag_hcl.box, self.reag_naoh.box, self.reag_kmno4.box, 
                    self.reag_ferrozine.box, self.reag_nh4oac.box, self.reag_asc.box]),
            self.iron_widget.box
        ])
        reag_accordion.set_title(0, "Реактивы подготовки")
        reag_accordion.set_title(1, "Реактивы калибровки (Fe стандарт)")

        self.ui_container = W.VBox([global_box, samples_accordion, cal_accordion, reag_accordion])

    def display(self):
        """Выводит интерфейс в ячейке Jupyter"""
        display(self.ui_container)

    def get_config(self):
        """Формирует итоговый словарь для передачи в CLI и генерации drafts"""
        return {
            'global': {
                'replicates': max(1, int(self.replicates.value)),
                'blanks_count': max(0, int(self.blanks.value)),
                'v_aliquot_ul': float(self.V_sample.value)
            },
            'calibration': self.cal_block.get_config(),
            'dilutions': self.dilution_block.get_config(),
            'samples': [s.get_config() for s in self.sample_blocks],
            'reagents': {
                'hcl': self.reag_hcl.get_config(),
                'naoh': self.reag_naoh.get_config(),
                'kmno4': self.reag_kmno4.get_config(),
                'ferrozine': self.reag_ferrozine.get_config(),
                'nh4oac': self.reag_nh4oac.get_config(),
                'asc': self.reag_asc.get_config(),
                'iron_std': self.iron_widget.get_config()
            }
        }