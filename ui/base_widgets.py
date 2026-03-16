import ipywidgets as W
from .utils import safe_float, adjust_mw_for_hydration, IRON_SALTS

class StockOrPowderWidget:
    def __init__(self, title, default_mw=None, allow_hydration=True, default_type="сток"):
        self.title = title
        self.type_dd = W.Dropdown(options=["сток", "порошок"], value=default_type,
                                  description="Тип:", layout=W.Layout(width="180px"))
        self.mw = W.FloatText(value=float(default_mw) if default_mw else 0.0,
                              description="MW (g/mol):", layout=W.Layout(width="250px"))
        self.hydr_dd = W.Dropdown(options=["сухой", "гидратированный"], value="сухой",
                                  description="Форма:", layout=W.Layout(width="250px"))
        self.hydr_n = W.IntText(value=0, description="H2O:", layout=W.Layout(width="180px"))
        self.stock_conc = W.FloatText(value=1.0, description="C стока:", layout=W.Layout(width="220px"))
        self.stock_unit = W.Dropdown(options=["M", "mM", "uM"], value="M",
                                     description="Ед.:", layout=W.Layout(width="160px"))
        self.allow_hydration = allow_hydration

        self.box = W.VBox([
            W.HTML(f"<b>{self.title}</b>"),
            W.HBox([self.type_dd]),
            W.HBox([self.stock_conc, self.stock_unit]),
            W.HBox([self.mw]),
            W.HBox([self.hydr_dd, self.hydr_n]),
        ])

        if not allow_hydration:
            self.hydr_dd.layout.display = "none"
            self.hydr_n.layout.display = "none"

        self._sync_visibility()
        self.type_dd.observe(lambda ch: self._sync_visibility(), names="value")
        self.hydr_dd.observe(lambda ch: self._sync_visibility(), names="value")

    def _sync_visibility(self):
        if self.type_dd.value == "сток":
            self.stock_conc.layout.display = ""
            self.stock_unit.layout.display = ""
            self.mw.layout.display = "none"
            if self.allow_hydration:
                self.hydr_dd.layout.display = "none"
                self.hydr_n.layout.display = "none"
        else:
            self.stock_conc.layout.display = "none"
            self.stock_unit.layout.display = "none"
            self.mw.layout.display = ""
            if self.allow_hydration:
                self.hydr_dd.layout.display = ""
                self.hydr_n.layout.display = "" if self.hydr_dd.value == "гидратированный" else "none"

    def get_config(self):
        d = {"type": self.type_dd.value}
        if self.type_dd.value == "сток":
            d["stock_conc"] = safe_float(self.stock_conc.value, 0.0)
            d["stock_unit"] = self.stock_unit.value
        else:
            mw = safe_float(self.mw.value, 0.0)
            if self.allow_hydration and self.hydr_dd.value == "гидратированный":
                mw = adjust_mw_for_hydration(mw, int(self.hydr_n.value))
            d["mw"] = mw
        return d


class IronStandardWidget:
    def __init__(self):
        self.kind = W.Dropdown(options=list(IRON_SALTS.keys()), value="FeCl3",
                               description="Стандарт:", layout=W.Layout(width="420px"))
        self.form = W.Dropdown(options=["сток", "порошок"], value="порошок",
                               description="Тип:", layout=W.Layout(width="220px"))
        self.stock_conc = W.FloatText(value=10.0, description="C стока:", layout=W.Layout(width="220px"))
        self.stock_unit = W.Dropdown(options=["M", "mM", "uM"], value="mM",
                                     description="Ед.:", layout=W.Layout(width="160px"))
        self.mw = W.FloatText(value=IRON_SALTS["FeCl3"], description="MW (g/mol):",
                              layout=W.Layout(width="260px"))
        
        self.box = W.VBox([
            W.HTML("<b>Калибровочный стандарт железа</b>"),
            self.kind,
            W.HBox([self.form]),
            W.HBox([self.stock_conc, self.stock_unit]),
            W.HBox([self.mw]),
        ])

        self._sync()
        self.kind.observe(lambda ch: self._sync(), names="value")
        self.form.observe(lambda ch: self._sync(), names="value")

    def _sync(self):
        mw = IRON_SALTS.get(self.kind.value, None)
        if self.kind.value != "Другое" and mw is not None:
            self.mw.value = float(mw)
            self.mw.disabled = True
        else:
            self.mw.disabled = False

        if self.form.value == "сток":
            self.stock_conc.layout.display = ""
            self.stock_unit.layout.display = ""
            self.mw.layout.display = "none" if self.kind.value != "Другое" else ""
        else:
            self.stock_conc.layout.display = "none"
            self.stock_unit.layout.display = "none"
            self.mw.layout.display = ""

    def get_config(self):
        d = {"kind": self.kind.value, "form": self.form.value, "mw": safe_float(self.mw.value, 0.0)}
        if self.form.value == "сток":
            d["stock_conc"] = safe_float(self.stock_conc.value, 0.0)
            d["stock_unit"] = self.stock_unit.value
        return d