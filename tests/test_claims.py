"""Claims: jede Zahl der README gegen die eingefrorene Messung (`lsm_messung.json`) bzw. gegen eine Rechnung.

Die Messung selbst wird in tests/test_messung.py in Teilen neu gerechnet. Hier steht je Aussage der README ein Test mit ihrer Voraussetzung
(N, K, L, Zahl der Instanzen, Messreihe). `kennzahlen` leitet die Zahlen des Fließtexts aus der Messung ab; die README wurde aus denselben
Werten gefüllt, der Test hält beide zusammen."""

import math
import re
import subprocess
import sys
from pathlib import Path

import pytest

import lsm_evaluation as ev
import lsm_nk as NK
import lsm_route as R
import lsm_texts as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
M = ev.lade_messung()
REIHEN = ("A", "B")


def _exakt(k):
    return [z for r in REIHEN for z in M["nk_exakt"]["reihen"][r] if z["k"] == k]


def _schaetzer(k, laenge):
    return [z for r in REIHEN for z in M["nk_schaetzer"]["reihen"][r] if z["k"] == k and z["L"] == laenge]


def _route(nb=None):
    return [z for r in REIHEN for z in M["route_exakt"]["reihen"][r] if nb is None or z["nachbarschaft"] == nb]


def kennzahlen() -> dict:
    """Textbausteine der README, abgeleitet aus der Messung."""
    bias100 = [z["bias"] for k in (0, 1, 2, 4, 8) for z in _schaetzer(k, 100)]
    bias100_k15 = [z["bias"] for z in _schaetzer(15, 100)]
    verh = [z["sd_innen"] / z["sd_zwischen"] for k in (1, 2, 4, 8, 15) for z in _schaetzer(k, 1000)]
    verh_k1 = [z["sd_innen"] / z["sd_zwischen"] for z in _schaetzer(1, 1000)]
    z_fam = [abs(z["mittel"] - z["familie"]) / z["se"] for k in (1, 2, 4) for z in _exakt(k)]
    z_fam_k8 = [abs(z["mittel"] - z["familie"]) / z["se"] for z in _exakt(8)]
    z_end = [abs(z["mittel"] - z["endlich"]) / z["se"] for k in (1, 2, 4, 8, 15) for z in _exakt(k)]
    oropt = [z["rho2"] - z["rho1"] ** 2 for z in _route("Or-opt") if z["n"] >= 6]
    quad = [M["route_exakt"]["gegenprobe_quadrat"][r]["spanne1"] for r in REIHEN]
    walk_z = [abs(z["mittel"] - z["exakt"]) / z["se"] for r in REIHEN for z in M["route_wanderung"]["lang"][r]]
    tau100 = [z["tau_median"] for r in REIHEN for z in M["route_wanderung"]["guete"][r] if z["n"] == 100 and z["L"] == 1000]

    def opt(k):
        a, b = (z["optima_mittel"] for z in _exakt(k))
        return ev.band(a, b, 1)

    return {
        "BIAS100": f"{ev.de(min(bias100), 3)} bis {ev.de(max(bias100), 3)}",
        "BIAS100_K15": ev.band(*bias100_k15, 3),
        "VERH_MIN": ev.de(min(verh), 1), "VERH_MAX": ev.de(max(verh), 1), "VERH_K1": ev.band(*verh_k1, 1),
        "SPANNE_2OPT": ev.de_exp(max(z["spanne1"] for z in _route("2-opt"))),
        "SPANNE_ALLE": ev.de_exp(max(z["spanne1"] for z in _route())),
        "OPT2": opt(2), "OPT4": opt(4), "OPT8": opt(8), "OPT15": opt(15),
        "OPT1_MIN": str(min(z["optima_min"] for z in _exakt(1))), "OPT1_MAX": str(max(z["optima_max"] for z in _exakt(1))),
        "QUAD_SPANNE": ev.band(*quad, 4),
        "K0_ABW": ev.de_exp(max(max(abs(z["min"] - 0.875), abs(z["max"] - 0.875)) for z in _exakt(0))),
        "Z_FAM_MIN": ev.de(min(z_fam), 1), "Z_FAM_MAX": ev.de(max(z_fam), 1), "Z_FAM_K8": ev.band(*z_fam_k8, 1), "Z_END_MAX": ev.de(max(z_end), 1),
        "OROPT_DIFF_MIN": ev.de(min(oropt), 4), "OROPT_DIFF_MAX": ev.de(max(oropt), 4),
        "WALK_Z_MAX": ev.de(max(walk_z), 1), "TAU_N100": ev.band(*tau100, 2),
    }


KZ = kennzahlen()


def _satz(teil: str) -> str:
    assert teil in README, f"README nennt nicht: {teil}"
    return teil


# ------------------------------------------------------------------------------------------------------------------ Tabellen und Texte


def test_readme_hat_keine_offenen_platzhalter():
    assert "@@" not in README
    assert "TODO" not in README.replace("<!-- TODO nach dem Deploy", "")


def test_tabellen_der_readme_stammen_aus_der_messung():
    for tabelle in (ev.tabelle_nk_exakt(M), ev.tabelle_nk_schaetzer(M), ev.tabelle_streuung(M), ev.tabelle_route_exakt(M),
                    ev.tabelle_route_wanderung(M), ev.tabelle_route_guete(M)):
        assert tabelle in README


def test_grenzen_stehen_wortgleich_in_app_und_readme():
    assert T.GRENZEN.strip() in README


def test_messung_nennt_quelle_und_stand_je_teil():
    for teil in ("nk_exakt", "nk_schaetzer", "route_exakt", "route_wanderung"):
        assert M[teil]["quelle"].startswith("tools/lsm_make_messung.py") and M[teil]["stand"] == "2026-11-21"
    _satz("Stand 2026-11-21")


# ------------------------------------------------------------------------------------------------------------------ NK exakt


def test_k0_jede_der_60_landschaften_hat_exakt_0875_und_ein_optimum():
    for z in _exakt(0):
        assert abs(z["min"] - 0.875) < 1e-9 and abs(z["max"] - 0.875) < 1e-9 and z["optima_min"] == z["optima_max"] == 1
        assert abs(z["diff2_mittel"]) < 1e-12 and abs(z["diff5_min"]) < 1e-12 and abs(z["diff5_max"]) < 1e-12
        assert z["familie"] == 0.9375
    assert sum(M["nk_exakt"]["instanzen"] for _ in REIHEN) == 60
    _satz("K = 0: 0,9375 gegen exakt 0,8750 in jeder der 60 Landschaften")
    _satz(f"jede der 60 Landschaften hat ρ(1) = 1 − 2/N = 0,8750 (größte Abweichung {KZ['K0_ABW']})")


def test_familienwert_liegt_bei_k_1_2_4_in_6_von_6_zellen_ueber_4_standardfehler_ueber_dem_mittel():
    zellen = [z for k in (1, 2, 4) for z in _exakt(k)]
    assert len(zellen) == 6 and all((z["familie"] - z["mittel"]) / z["se"] > 4 for z in zellen)
    assert all(abs(z["familie"] - z["mittel"]) / z["se"] < 3 for z in _exakt(8))
    _satz(f"in 6 von 6 Zellen (3 K × 2 Messreihen) mehr als 4 Standardfehler über dem Mittel der exakten Werte ({KZ['Z_FAM_MIN']} bis {KZ['Z_FAM_MAX']} Standardfehler)")
    _satz(f"bei K = 8 sind es {KZ['Z_FAM_K8']} Standardfehler")


def test_formel_fuer_die_einzelne_landschaft_in_10_von_10_zellen_nah_am_mittel():
    zellen = [z for k in (1, 2, 4, 8, 15) for z in _exakt(k)]
    assert len(zellen) == 10 and all(abs(z["mittel"] - z["endlich"]) / z["se"] < 3 for z in zellen)
    for z in zellen:
        assert z["endlich"] == pytest.approx(NK.einzelwert_erwartung(16, z["k"])) and z["familie"] == pytest.approx(NK.familienwert(16, z["k"]))
    _satz(f"in 10 von 10 Zellen (K = 1, 2, 4, 8, 15) höchstens {KZ['Z_END_MAX']} Standardfehler vom Mittel entfernt")


def test_rho5_liegt_bei_k_1_2_4_8_in_jeder_der_240_landschaften_ueber_der_potenz():
    zellen = [z for k in (1, 2, 4, 8) for z in _exakt(k)]
    assert len(zellen) == 8 and all(z["diff5_positiv"] == 30 and z["diff5_min"] > 0.01 for z in zellen)
    _satz("in jeder der 240 Landschaften positiv (8 Zellen zu je 30)")


def test_lokale_optima():
    _satz(f"zwischen {KZ['OPT1_MIN']} und {KZ['OPT1_MAX']} Optima")
    assert (KZ["OPT1_MIN"], KZ["OPT1_MAX"]) == ("1", "24")
    _satz(f"bei K = 15 liegt das Mittel bei {KZ['OPT15']}, die Erwartung 2^N/(N+1) ist 3855,1")
    assert ev.de(2 ** 16 / 17, 1) == "3855,1"
    for z in _exakt(15):
        assert abs(z["optima_mittel"] - 2 ** 16 / 17) < 0.01 * 2 ** 16 / 17
    _satz(f"| Zahl der lokalen Optima, N = 16 | K = 2 / 4 / 8: 25,6 / 132,0 / 767,9 (Mittel von 30) | {KZ['OPT2']} / {KZ['OPT4']} / {KZ['OPT8']} |")
    # die Verschiebung gegen die Vormessung ist echt: beide Messreihen liegen über den Werten der Vormessung
    for k, alt in ((2, 25.6), (4, 132.0), (8, 767.9)):
        assert all(z["optima_mittel"] > alt for z in _exakt(k))


# ------------------------------------------------------------------------------------------------------------------ NK Schätzer


def test_bias_bei_l_100():
    werte = [z["bias"] for k in (0, 1, 2, 4, 8) for z in _schaetzer(k, 100)]
    assert len(werte) == 10 and all(-0.045 < w < -0.025 for w in werte)
    assert _satz(f"bei L = 100 um {KZ['BIAS100']} für K = 0 bis 8") and KZ["BIAS100"] == "−0,041 bis −0,027"
    _satz(f"{KZ['BIAS100']} für K = 0 bis 8; K = 15: {KZ['BIAS100_K15']}")
    assert all(z["bias"] < 0 for k in (0, 1, 2, 4, 8, 15) for z in _schaetzer(k, 100))                # nach unten, in 12 von 12 Zellen
    # der Betrag schrumpft mit L in jeder Zelle mit K <= 8 (bei K = 15 liegt er bei L = 10000 im Rauschen)
    for k in (0, 1, 2, 4, 8):
        for a, b in zip(_schaetzer(k, 100), _schaetzer(k, 1000)):
            assert abs(b["bias"]) < abs(a["bias"]) / 5


def test_schaetzung_streut_bei_l_1000_in_10_von_10_zellen_staerker_als_die_instanzen():
    zellen = [z for k in (1, 2, 4, 8, 15) for z in _schaetzer(k, 1000)]
    assert len(zellen) == 10 and all(z["sd_innen"] > z["sd_zwischen"] > 0 for z in zellen)
    assert all(z["sd_zwischen"] < 1e-9 for z in _schaetzer(0, 1000))                                   # K = 0: nur Rundungsreste
    _satz(f"Verhältnis {KZ['VERH_MIN']} bis {KZ['VERH_MAX']} in 10 von 10 Zellen; am knappsten bei K = 1")
    _satz(f"bei K = 1 ist der Abstand klein (Verhältnis {KZ['VERH_K1']})")
    verh = {k: min(z["sd_innen"] / z["sd_zwischen"] for z in _schaetzer(k, 1000)) for k in (1, 2, 4, 8, 15)}
    assert min(verh, key=verh.get) == 1
    # sd_zwischen im Schätzer-Teil ist dieselbe Größe wie die SD im exakten Teil
    for k in (1, 2, 4, 8, 15):
        for a, b in zip(_exakt(k), _schaetzer(k, 1000)):
            assert a["sd"] == pytest.approx(b["sd_zwischen"], rel=1e-9)


# ------------------------------------------------------------------------------------------------------------------ Rundtour


def test_2opt_formel_und_gleichheit_in_300_instanzen_je_n():
    zeilen = _route("2-opt")
    assert len(zeilen) == 10 and all(z["instanzen"] == 150 and z["familien"] == 5 for z in zeilen)
    for z in zeilen:
        n = z["n"]
        assert z["touren"] == math.factorial(n - 1) // 2 and z["nachbarn"] == n * (n - 3) // 2
        assert z["rho1"] == pytest.approx(R.formel_2opt(n), abs=1e-12) and z["rho2"] == pytest.approx(z["rho1"] ** 2, abs=1e-12)
        assert z["spanne1"] < 1e-14 and z["spanne2"] < 1e-14
    _satz(f"in jeder von 300 aufgezählten Instanzen je n derselbe Wert 1 − 2(n−1)/(n(n−3)) (größte Spanne {KZ['SPANNE_2OPT']}, Rundungsfehler)")
    _satz(f"| Größte Spanne von ρ(1) über die Rundtour-Instanzen | höchstens 8e−16 | {KZ['SPANNE_ALLE']} |")
    _satz("also 1/5, 4/9, 4/7, 13/20, 19/27")
    assert [R.formel_2opt(n) for n in range(5, 10)] == pytest.approx([1 / 5, 4 / 9, 4 / 7, 13 / 20, 19 / 27])


def test_oropt_gleich_in_jeder_instanz_aber_keine_potenz():
    zeilen = _route("Or-opt")
    assert [z["nachbarn"] for z in zeilen[:5]] == [10, 29, 63, 108, 165]
    _satz("10 / 29 / 63 / 108 / 165 verschiedene Nachbarn für n = 5 bis 9")
    assert all(z["spanne1"] < 1e-14 for z in zeilen)
    diff = [z["rho2"] - z["rho1"] ** 2 for z in zeilen if z["n"] >= 6]
    assert len(diff) == 8 and all(0.001 < d < 0.003 for d in diff)
    _satz(f"für n = 6 bis 9 um {KZ['OROPT_DIFF_MIN']} bis {KZ['OROPT_DIFF_MAX']} über ρ(1)²")
    assert all(abs(z["rho1"]) < 1e-12 for z in zeilen if z["n"] == 5)                               # n = 5: 0 bis auf Rundung
    _satz("10 Nachbarn je Tour, ρ(1) = 0 bis auf Rundung")
    neun = {z["nachbarschaft"]: z for z in M["route_exakt"]["reihen"]["A"] if z["n"] == 9}
    _satz(f"n = 9: {ev.de(neun['2-opt']['rho1'], 4)} bei 27 Nachbarn (2-opt), {ev.de(neun['Or-opt']['rho1'], 4)} bei 165 (Or-opt)")


def test_gegenprobe_quadrat_unterscheidet_instanzen():
    for r in REIHEN:
        q = M["route_exakt"]["gegenprobe_quadrat"][r]
        assert q["n"] == 8 and q["instanzen"] == 150 and q["spanne1"] > 0.005
    assert README.count(f"Spanne {KZ['QUAD_SPANNE']}") == 2


def test_wanderungen_laufen_gegen_die_formel():
    zeilen = [z for r in REIHEN for z in M["route_wanderung"]["lang"][r]]
    assert len(zeilen) == 8 and all(z["wanderungen"] == 10 and abs(z["mittel"] - z["exakt"]) <= 4 * z["se"] for z in zeilen)
    assert all(z["exakt"] == pytest.approx(R.formel_2opt(z["n"])) for z in zeilen)
    _satz(f"Alle 8 Zeilen liegen höchstens {KZ['WALK_Z_MAX']} Standardfehler vom Wert der Formel")
    tau = " / ".join(ev.de(NK.tau(R.formel_2opt(n)), 1) for n in (9, 30, 100, 200))
    assert tau == "2,8 / 13,5 / 48,5 / 98,5"
    _satz(f"Die Korrelationslänge der Formel ist {tau} Schritte für n = 9 / 30 / 100 / 200")
    _satz(f"Bei n = 100 und L = 1000 ist der Median von τ̂/τ {KZ['TAU_N100']}")


def test_guete_auf_der_rundtour_zeigt_keinen_unterschied_zwischen_instanzen():
    """Streuung der Instanz-Mittel gegen SD innen / Wurzel(Wanderungen): bei gleichem exaktem Wert sind beide von gleicher Größe (Faktor unter 2)."""
    for r in REIHEN:
        for z in M["route_wanderung"]["guete"][r]:
            if z["L"] >= 1000:
                assert z["sd_instanzmittel"] < 2 * z["sd_innen"] / math.sqrt(M["route_wanderung"]["guete_wanderungen"])


# ------------------------------------------------------------------------------------------------------------------ Testzahl, Struktur


def test_testzahl_der_readme_stimmt_mit_der_suite():
    m = re.search(r"\*\*(\d+) Tests\*\*", README)
    assert m, "README nennt keine Testzahl"
    aus = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests"], cwd=ROOT, capture_output=True, text=True, timeout=300)
    gesammelt = re.search(r"(\d+) tests? collected", aus.stdout)
    assert gesammelt and int(gesammelt.group(1)) == int(m.group(1)), aus.stdout[-300:]


def test_readme_pflichtabschnitte_in_reihenfolge():
    abschnitte = ["## Kernfrage", "## Befunde und Korrekturen", "## Modell", "## Methodik", "## Befunde (gemessen, keine Behauptungen)", "### Zahl → Test",
                  "## Ehrliche Grenzen", "## 🚧 Bewusst nicht enthalten / nicht gemessen", "## Tests", "## Dateistruktur", "## Lokal ausführen"]
    stellen = [README.index(a) for a in abschnitte]
    assert stellen == sorted(stellen)


def test_dateien_der_dateistruktur_existieren():
    for name in re.findall(r"`((?:lsm_|tools/lsm_)[a-z_]+\.(?:py|json))`", README):
        assert (ROOT / name).exists(), name
    for pfad in ROOT.glob("lsm_*.py"):
        assert f"`{pfad.name}`" in README, pfad.name
