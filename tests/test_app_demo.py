"""App-Tests mit Inhalt: je Preset die erwartete Verdikt-Zeile (kein Preset ohne Wirkung meldet eine Wirkung), Expander per Titel, Schalter."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import lsm_constants as C
import lsm_evaluation as ev

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(preset=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    if preset is not None:
        at.sidebar.button(key=f"preset_{preset}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at) -> dict:
    return {kind: [e.value for e in getattr(at, kind)] for kind in ("success", "info", "warning", "error")}


def _einer(texte: dict, kind: str, teil: str) -> str:
    treffer = [t for t in texte[kind] if teil in t]
    assert len(treffer) == 1, (kind, teil, texte)
    return treffer[0]


# je Preset: (Art, Textteil) der Verdikte, die genau einmal vorkommen müssen
ERWARTET = {
    "NK, K = 4 (Voreinstellung)": [
        ("info", "N = 16, K = 4: exakt ist ρ(1) ="), ("success", "N = 16, K = 4, 30 Landschaften"), ("warning", "nicht zuverlässig zu unterscheiden"),
        ("success", "n = 7, 2-opt, 50 Instanzen aus 5 Familien, alle 360 Touren aufgezählt: ρ(1) = **0,571429** in jeder Instanz"),
        ("success", "n = 30, 2-opt, eine Instanz"),
    ],
    "Von Hand: K = 0, N = 4": [
        ("info", "N = 4, K = 0: exakt ist ρ(1) = **0,500**"), ("success", "diese Landschaft exakt **0,5000**"),
        ("success", "jede der 30 Landschaften hat ρ(1) = 1 − 2/N = **0,5000**"), ("info", "Zwischen den Instanzen gibt es hier keinen Unterschied"),
    ],
    "NK, K = 0": [
        ("info", "N = 16, K = 0: exakt ist ρ(1) = **0,875**"), ("info", "ist **1** ein lokales Optimum"),
        ("success", "jede der 30 Landschaften hat ρ(1) = 1 − 2/N = **0,8750**"), ("success", "Der Familienwert 0,9375 liegt um 0,0625 darüber"),
        ("info", "Zwischen den Instanzen gibt es hier keinen Unterschied"),
    ],
    "NK, K = 15": [
        ("info", "nennt die Demo das **rau**"), ("info", "ist der Familienwert vom Mittel nicht zu unterscheiden"), ("warning", "nicht zuverlässig zu unterscheiden"),
    ],
    "Wanderung L = 100": [("info", "Die eine Wanderung mit 100 Auswertungen schätzt"), ("success", "N = 16, K = 4, 30 Landschaften")],
    "Rundtour n = 8": [
        ("success", "n = 8, 2-opt, 50 Instanzen aus 5 Familien, alle 2520 Touren aufgezählt: ρ(1) = **0,650000** in jeder Instanz"),
        ("success", "Die Formel 1 − 2(n−1)/(n(n−3)) gibt 0,650000"),
    ],
    "Rundtour n = 100": [("success", "n = 100, 2-opt, eine Instanz (gleichverteilt), 5 Wanderungen mit je 20000 Auswertungen"), ("success", "τ = 48,5 Schritte")],
}


def test_erwartungen_decken_jedes_preset():
    assert set(ERWARTET) == set(C.PRESETS)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_zeigt_die_erwarteten_verdikte_und_keinen_fehler(name):
    texte = _texte(_app(name))
    assert not texte["error"]
    for kind, teil in ERWARTET[name]:
        _einer(texte, kind, teil)
    # die Rundtour meldet in keinem Preset einen Unterschied zwischen Instanzen (alle Presets lassen die Gegenprobe aus)
    assert not any("die Instanzen unterscheiden sich" in t for t in texte["warning"])
    assert sum("Schätzrauschen: die Zahl misst hier n" in t for t in texte["success"]) == 1


def test_preset_k0_meldet_bei_den_instanzen_keinen_unterschied_und_keine_warnung_zur_streuung():
    texte = _texte(_app("NK, K = 0"))
    assert not any("streut damit stärker" in t for t in texte["warning"])


def test_gegenprobe_meldet_instanzunterschied_nur_mit_dem_quadrat():
    at = _app()
    at.sidebar.toggle(key="quad_toggle").set_value(True).run()
    assert not at.exception
    texte = _texte(at)
    _einer(texte, "info", "mit dem **Quadrat der Tourlänge** als Landschaft unterscheiden sich die Instanzen")
    assert not any("in jeder Instanz" in t for t in texte["success"])


def test_oropt_hat_mehr_nachbarn_und_kleineres_rho():
    at = _app()
    at.sidebar.radio(key="nb_radio").set_value("Or-opt").run()
    assert not at.exception
    text = _einer(_texte(at), "success", "n = 7, Or-opt")
    assert "**0,404762**" in text and "Formel" not in text
    werte = {m.label: m.value for m in at.metric}
    assert werte["Nachbarn je Tour"] == "63" and werte["Touren = Auswertungen der Aufzählung"] == "360"


def test_kennzahlen_der_primaeransicht():
    at = _app("Von Hand: K = 0, N = 4")
    werte = {m.label: m.value for m in at.metric}
    assert werte["ρ(1) exakt"] == "0,500" and werte["Familienwert 1 − (K+1)/N"] == "0,750" and werte["Lokale Optima"] == "1"


def test_expander_per_titel_und_eingefrorene_tabellen():
    at = _app()
    titel = [e.label for e in at.expander]
    for t in ("So funktioniert die Messung der Rauigkeit", "📐 Mathematische Formulierung", "Erklärung: Nachbarschaften und Familien"):
        assert t in titel
    assert titel[-1] == "📐 Mathematische Formulierung"
    assert sum(t.startswith("Eingefrorene Messung") for t in titel) == 3
    alles = " ".join(m.value for m in at.markdown)
    m = ev.lade_messung()
    for tabelle in (ev.tabelle_nk_exakt(m), ev.tabelle_nk_schaetzer(m), ev.tabelle_route_exakt(m)):
        assert tabelle in alles
    assert "🚧 Wo die Annahmen enden" in [s.value for s in at.subheader]
    assert sum(s.value.startswith("🔬 Experiment") for s in at.subheader) == 3          # Experiment 1 ist die Primäransicht
    assert len([s for s in at.subheader if "Experiment" in s.value]) + 1 <= 5           # höchstens fünf Experimente je Seite


def test_k_groesser_null_am_kleinsten_n_und_raender_laufen():
    at = _app()
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN).run()
    assert not at.exception
    assert at.sidebar.slider(key="k_slider").value == C.N_MIN - 1
    at.sidebar.slider(key="rn_slider").set_value(5).run()
    at.sidebar.radio(key="nb_radio").set_value("Or-opt").run()                          # n = 5, Or-opt: 10 von 11 anderen Touren sind Nachbarn
    assert not at.exception and not _texte(at)["error"]
