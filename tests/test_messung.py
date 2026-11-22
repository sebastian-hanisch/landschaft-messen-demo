"""Die eingefrorene Messung in Teilen neu gerechnet: exakte Größen mit relativer Toleranz 1e-9, Zufallsgrößen als Band.

Der volle Vergleich läuft mit `python tools/lsm_make_messung.py --check` (etwa zwei Minuten, nicht in der Suite)."""

import importlib.util
import math
from pathlib import Path

import pytest

import lsm_evaluation as ev

ROOT = Path(__file__).resolve().parent.parent
M = ev.lade_messung()


def _werkzeug():
    spec = importlib.util.spec_from_file_location("lsm_make_messung", ROOT / "tools" / "lsm_make_messung.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_aufbau_der_messung():
    assert set(M) >= {"hinweis", "skript", "nk_exakt", "nk_schaetzer", "route_exakt", "route_wanderung"}
    for reihe in ("A", "B"):
        assert [z["k"] for z in M["nk_exakt"]["reihen"][reihe]] == [0, 1, 2, 4, 8, 15]
        assert [(z["k"], z["L"]) for z in M["nk_schaetzer"]["reihen"][reihe]] == [(k, laenge) for k in (0, 1, 2, 4, 8, 15) for laenge in (100, 1000, 10000)]
        assert [(z["n"], z["nachbarschaft"]) for z in M["route_exakt"]["reihen"][reihe]] == [(n, nb) for n in range(5, 10) for nb in ("2-opt", "Or-opt")]
        assert len(M["route_wanderung"]["lang"][reihe]) == 4 and len(M["route_wanderung"]["guete"][reihe]) == 6
    assert M["nk_exakt"]["n"] == M["nk_schaetzer"]["n"] == 16
    assert M["nk_exakt"]["instanzen"] == M["nk_schaetzer"]["instanzen"] == M["nk_schaetzer"]["wanderungen"] == 30
    assert M["route_exakt"]["je_familie"] == 30


def test_die_zwei_messreihen_sind_verschiedene_instanzen():
    a, b = (M["nk_exakt"]["reihen"][r][3] for r in ("A", "B"))        # K = 4
    assert a["mittel"] != b["mittel"] and a["optima_mittel"] != b["optima_mittel"]


@pytest.mark.parametrize("reihe, start", [("A", 0), ("B", 1000)])
@pytest.mark.parametrize("k", [0, 4])
def test_nk_exakt_neu_gerechnet(reihe, start, k):
    alt = next(z for z in M["nk_exakt"]["reihen"][reihe] if z["k"] == k)
    f = ev.formeln(16, k, start, 30, smax=5, mit_optima=True)
    assert f["mittel"] == pytest.approx(alt["mittel"], rel=1e-9) and f["sd"] == pytest.approx(alt["sd"], rel=1e-6, abs=1e-12)
    assert min(f["werte"]) == pytest.approx(alt["min"], rel=1e-9) and max(f["werte"]) == pytest.approx(alt["max"], rel=1e-9)
    diff5 = [r[4] - r[0] ** 5 for r in f["rho"]]
    assert sum(diff5) / 30 == pytest.approx(alt["diff5_mittel"], rel=1e-6, abs=1e-12)
    assert sum(f["optima"]) / 30 == alt["optima_mittel"] and min(f["optima"]) == alt["optima_min"] and max(f["optima"]) == alt["optima_max"]


@pytest.mark.parametrize("n", [5, 6, 7])
@pytest.mark.parametrize("nachbarschaft", ["2-opt", "Or-opt"])
def test_route_exakt_neu_gerechnet(n, nachbarschaft):
    alt = next(z for z in M["route_exakt"]["reihen"]["B"] if z["n"] == n and z["nachbarschaft"] == nachbarschaft)
    r = ev.route_exakt(n, nachbarschaft, 30, 1000)
    assert (r["touren"], r["nachbarn"], r["instanzen"], r["familien"]) == (alt["touren"], alt["nachbarn"], alt["instanzen"], alt["familien"])
    assert r["rho1"] == pytest.approx(alt["rho1"], rel=1e-9, abs=1e-12) and r["rho2"] == pytest.approx(alt["rho2"], rel=1e-9, abs=1e-12)
    assert r["spanne1"] < 1e-13 and alt["spanne1"] < 1e-13             # die Spanne ist Rundungsfehler: nur die Größenordnung zählt


def test_gegenprobe_quadrat_neu_gerechnet():
    alt = M["route_exakt"]["gegenprobe_quadrat"]["A"]
    r = ev.route_exakt(8, "2-opt", 30, 0, quadrat=True)
    assert r["min1"] == pytest.approx(alt["min1"], rel=1e-9) and r["max1"] == pytest.approx(alt["max1"], rel=1e-9)
    assert r["spanne1"] == pytest.approx(alt["spanne1"], rel=1e-6)


def test_schaetzer_zelle_neu_gerechnet_als_band():
    """K = 4, Messreihe A, alle drei Längen: dieselben Zufalls-Seeds, verglichen als Band (die letzte Binärstelle der Summen darf je Plattform abweichen)."""
    s = ev.schaetzung(16, 4, 0, 30, 30)
    for z in s["zeilen"]:
        alt = next(a for a in M["nk_schaetzer"]["reihen"]["A"] if a["k"] == 4 and a["L"] == z["L"])
        assert z["bias"] == pytest.approx(alt["bias"], abs=1e-6)
        assert z["sd_innen"] == pytest.approx(alt["sd_innen"], rel=1e-4)
        assert z["anteil_01"] == pytest.approx(alt["anteil_01"], abs=2 / 900)
        assert z["tau_median"] == pytest.approx(alt["tau_median"], rel=1e-4)


def test_schaetzer_mit_fremden_seeds_liegt_im_band_der_messung():
    """Gegenprobe mit einer dritten Menge von Landschaften und Wanderungen (ab laufender Nummer 5000): Bias und Streuung liegen im Band um A und B."""
    s = ev.schaetzung(16, 4, 5000, 20, 20)
    alt = {z["L"]: z for z in M["nk_schaetzer"]["reihen"]["A"] if z["k"] == 4}
    for z in s["zeilen"]:
        assert z["sd_innen"] == pytest.approx(alt[z["L"]]["sd_innen"], rel=0.2)
    kurz = s["zeilen"][0]
    se = kurz["sd_innen"] / math.sqrt(400)
    assert abs(kurz["bias"] - alt[100]["bias"]) < 4 * se * math.sqrt(2)
    assert kurz["bias"] < 0


def test_lange_wanderung_neu_gerechnet_als_band():
    alt = M["route_wanderung"]["lang"]["A"][0]                          # n = 9, 10 Wanderungen mit je 20000 Auswertungen
    w = ev.route_wanderung(9, "gleich", 0, 10, 20000)
    assert w["mittel"] == pytest.approx(alt["mittel"], abs=1e-6) and w["se"] == pytest.approx(alt["se"], rel=1e-3)
    assert w["exakt"] == pytest.approx(alt["exakt"], rel=1e-12)


def test_vergleich_des_werkzeugs_erkennt_abweichungen():
    w = _werkzeug()
    a = {"x": [1.0, {"y": 2}], "z": "t"}
    assert w.gleich(a, {"x": [1.0 + 1e-12, {"y": 2}], "z": "t"}) == []
    assert len(w.gleich(a, {"x": [1.001, {"y": 2}], "z": "t"})) == 1
    assert len(w.gleich(a, {"x": [1.0, {"y": 3}], "z": "t"})) == 1
    assert len(w.gleich(a, {"x": [1.0], "z": "t"})) == 1 and len(w.gleich(a, {"x": [1.0, {"y": 2}]})) == 1
    assert w.STAND == M["nk_exakt"]["stand"] and set(w.TEILE) <= set(M)
