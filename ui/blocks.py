import ipywidgets as W
from .utils import safe_float

class SampleBlock:
    def __init__(self, idx, saved_name=None):
        name_val = saved_name if saved_name else f"Sample_{idx+1}"
        self.name = W.Text(value=name_val, description="Название:", layout=W.Layout(width="420px"))
        self.box = W.VBox([self.name])

    def get_config(self):
        return {"name": self.name.value}


class DilutionBlock:
    def __init__(self, preset_dilutions=None):
        presets = preset_dilutions if preset_dilutions else [1, 2, 5]
        self.n_dil = W.IntText(value=len(presets), description="Разведений:", layout=W.Layout(width="220px"))
        self.dil_box = W.VBox()
        self.box = W.VBox([
            W.HTML("<b>Разведения (общие для всех образцов)</b>"),
            self.n_dil,
            self.dil_box
        ])

        self.dil_widgets = []
        self._build(presets)
        self.n_dil.observe(lambda ch: self._build(), names="value")

    def _build(self, preset=None):
        n = max(1, int(self.n_dil.value))
        old_vals = [w.value for w in self.dil_widgets]
        
        if preset is None:
            vals = old_vals + [1.0] * max(0, n - len(old_vals))
        else:
            vals = list(preset) + [1.0] * max(0, n - len(preset))

        self.dil_widgets = []
        children = []
        for i in range(n):
            ft = W.FloatText(value=float(vals[i]), description=f"D{i+1} (x):", layout=W.Layout(width="260px"))
            self.dil_widgets.append(ft)
            children.append(ft)
        self.dil_box.children = children

    def get_config(self):
        return [safe_float(w.value, 1.0) for w in self.dil_widgets]


class CalibrationBlock:
    def __init__(self, preset_points=None):
        presets = preset_points if preset_points else [0, 25, 50, 100, 200, 300]
        self.unit = W.Dropdown(options=["uM", "mM", "M"], value="uM", description="Ед.:", layout=W.Layout(width="200px"))
        self.n_pts = W.IntText(value=len(presets), description="Точек:", layout=W.Layout(width="200px"))
        self.pts_box = W.VBox()
        self.box = W.VBox([W.HBox([self.n_pts, self.unit]), self.pts_box])

        self.pt_widgets = []
        self._build_points(presets)
        self.n_pts.observe(lambda ch: self._build_points(), names="value")

    def _build_points(self, preset=None):
        n = max(2, int(self.n_pts.value))
        old_vals = [w.value for w in self.pt_widgets]

        if preset is None:
            vals = old_vals + [0.0] * max(0, n - len(old_vals))
        else:
            vals = list(preset) + [0.0] * max(0, n - len(preset))

        self.pt_widgets = []
        children = []
        for i in range(n):
            ft = W.FloatText(value=float(vals[i]), description=f"C{i+1}:", layout=W.Layout(width="240px"))
            self.pt_widgets.append(ft)
            children.append(ft)
        self.pts_box.children = children

    def get_config(self):
        return {
            "unit": self.unit.value, 
            "points": [safe_float(w.value, 0.0) for w in self.pt_widgets]
        }