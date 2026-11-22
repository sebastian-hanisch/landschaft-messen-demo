"""Verdikte an von Hand gesetzten Werten: jede Schwelle und jede Zahl im Text."""

import lsm_evaluation as ev
import lsm_route as R

# ------------------------------------------------------------------------------------------------------------------ Zahlformat


def test_zahlformat():
    assert ev.de(0.8750, 3) == "0,875" and ev.de(-0.0361, 3) == "−0,036" and ev.de(-0.00001, 3) == "0,000"
    assert ev.de(3859.43, 1) == "3859,4" and ev.de(25.0, 0) == "25"
    assert ev.de_exp(6.7e-16) == "6,7e−16" and ev.de_exp(0) == "0" and ev.de_exp(1.1e-28) == "1,1e−28"
    assert ev.band(0.8335, 0.8290, 4) == "0,8290 bis 0,8335" and ev.band(0.875, 0.875, 4) == "0,8750"
    assert abs(ev.sd([1.0, 3.0]) - 2 ** 0.5) < 1e-12 and ev.sd([4.0]) == 0.0


# ------------------------------------------------------------------------------------------------------------------ Experiment 1 und Kernfragen


def test_glaette_wort_schwellen():
    assert ev.glaette_wort(0.5) == "glatt" and ev.glaette_wort(0.4999) == "mittel"
    assert ev.glaette_wort(0.1) == "mittel" and ev.glaette_wort(0.0999) == "rau" and ev.glaette_wort(-0.05) == "rau"
    assert ev.glaette_wort(-0.3) == "mittel"


def test_verdict_profil_nennt_alle_zahlen():
    kind, text = ev.verdict_profil(16, 4, 0.6776, 0.716, 1000, 239)
    assert kind == "info"
    assert "N = 16, K = 4" in text and "ρ(1) = **0,678**" in text and "**glatt**" in text
    assert "mit 1000 Auswertungen schätzt 0,716" in text and "Von den 65536 Zuständen sind **239** lokale Optima" in text
    kind, text = ev.verdict_profil(16, 15, 0.0017, 0.051, 1000, 3817)
    assert kind == "info" and "**rau**" in text and "unter 0,1" in text
    assert "liegt zwischen glatt und rau" in ev.verdict_profil(16, 9, 0.3, 0.31, 100, 1200)[1]


def test_verdict_profil_einzahl_und_randfaelle():
    assert "ist **1** ein lokales Optimum" in ev.verdict_profil(4, 0, 0.5, 0.4, 100, 1)[1]
    assert ev.verdict_profil(4, 0, None, None, 100, 0)[0] == "warning"
    assert "Schätzwert ist nicht definiert" in ev.verdict_profil(4, 0, 0.5, None, 100, 1)[1]


def test_verdict_einzel():
    kind, text = ev.verdict_einzel(16, 0, 0.875, 0.9375, 0.875)
    assert kind == "success"
    assert "Familienwert 1 − (K+1)/N = 0,9375" in text and "exakt **0,8750**" in text and "Abstand zum Familienwert 0,0625" in text
    assert "1 − 2/N = 0,8750" in text and "1/N = 0,0625" in text
    kind, text = ev.verdict_einzel(16, 4, 0.6776, 0.6875, 0.6774)
    assert kind == "info" and "Abstand zum Familienwert 0,0099" in text and "zur Formel für die einzelne Landschaft 0,0002" in text
    assert ev.verdict_einzel(16, 4, None, 0.6875, 0.6774)[0] == "warning"


def test_verdict_fehler_schwelle_ein_zehntel():
    kind, text = ev.verdict_fehler(0.678, 0.464, 100)
    assert kind == "warning" and "L = 100" in text and "schätzt 0,464 statt 0,678" in text and "Fehler **−0,214**" in text
    assert ev.verdict_fehler(0.5, 0.6, 100)[0] == "info"                # genau 0,1 ist nicht „mehr als 0,1“
    assert ev.verdict_fehler(0.5, 0.61, 100)[0] == "warning"
    assert ev.verdict_fehler(0.5, 0.39, 100)[0] == "warning"
    assert ev.verdict_fehler(None, 0.4, 100)[0] == "warning" and ev.verdict_fehler(0.5, None, 100)[0] == "warning"


# ------------------------------------------------------------------------------------------------------------------ Experiment 2


def _f(werte, familie, endlich):
    import math

    import numpy as np
    return {"werte": werte, "familie": familie, "endlich": endlich, "mittel": float(np.mean(werte)) if werte else None, "sd": ev.sd(werte),
            "se": ev.sd(werte) / math.sqrt(len(werte)) if werte else None}


def test_verdict_formeln_k0():
    kind, text = ev.verdict_formeln(16, 0, _f([0.875] * 30, 0.9375, 0.875))
    assert kind == "success" and "jede der 30 Landschaften" in text and "**0,8750**" in text
    assert "Familienwert 0,9375 liegt um 0,0625 darüber" in text and "größte Abweichung 0" in text


def test_verdict_formeln_familie_unterscheidbar():
    # Mittel 0,68; Abweichungen ±0,01 und ±0,00707: Quadratsumme 3e-4, Varianz 1e-4, SD 0,01, SE 0,005 bei 4 Werten; Familienwert 0,70: 4 SE entfernt; Formel 0,678: 0,4 SE
    werte = [0.67, 0.69, 0.68 - 0.0070710678, 0.68 + 0.0070710678]
    kind, text = ev.verdict_formeln(16, 4, _f(werte, 0.70, 0.678))
    assert kind == "success"
    assert "4 Landschaften" in text and "**0,6800**" in text and "Standardfehler 0,0050" in text and "Instanzen 0,0100" in text
    assert "Familienwert 0,7000: 4,0 Standardfehler" in text and "0,6780: 0,4 Standardfehler" in text and "unterscheidbar (über 3 Standardfehler)" in text


def test_verdict_formeln_schwelle_drei_standardfehler():
    werte = [0.67, 0.69, 0.68 - 0.0070710678, 0.68 + 0.0070710678]        # SE 0,005
    assert ev.verdict_formeln(16, 4, _f(werte, 0.6949, 0.68))[0] == "info"       # 2,98 SE: nicht unterscheidbar
    assert "nicht zu unterscheiden" in ev.verdict_formeln(16, 4, _f(werte, 0.6949, 0.68))[1]
    assert ev.verdict_formeln(16, 4, _f(werte, 0.6951, 0.68))[0] == "success"    # 3,02 SE
    assert ev.verdict_formeln(16, 4, _f(werte, 0.70, 0.66))[0] == "warning"      # beide über 3 SE entfernt


def test_verdict_formeln_randfaelle():
    assert ev.verdict_formeln(16, 4, _f([], 0.7, 0.68))[0] == "warning"
    kind, text = ev.verdict_formeln(16, 4, _f([0.68], 0.7, 0.68))
    assert kind == "info" and "eine Landschaft mit ρ(1) = 0,6800" in text


# ------------------------------------------------------------------------------------------------------------------ Experiment 3


def _s(sd_innen_1000, sd_zwischen):
    zeilen = [
        {"L": 100, "bias": -0.036, "sd_innen": 0.084, "anteil_01": 0.25},
        {"L": 1000, "bias": -0.0050, "sd_innen": sd_innen_1000, "anteil_01": 0.0},
        {"L": 10000, "bias": -0.0004, "sd_innen": 0.0075, "anteil_01": 0.0},
    ]
    return {"zeilen": zeilen, "sd_zwischen": sd_zwischen, "instanzen": 30, "wanderungen": 10}


def test_verdict_schaetzung_streut_staerker_als_die_instanzen():
    kind, text = ev.verdict_schaetzung(16, 4, _s(0.0244, 0.0110))
    assert kind == "warning"
    assert "30 Instanzen × 10 Wanderungen" in text and "bei L = 100" in text and "um −0,036 verschoben" in text and "25 % der Schätzungen" in text
    assert "bei L = 1000 beträgt die Verschiebung −0,0050" in text and "innerhalb einer Instanz 0,0244" in text
    assert "(0,0244 gegen 0,0110)" in text and "nicht zuverlässig zu unterscheiden (Verhältnis 2,2;" in text


def test_verdict_schaetzung_instanzen_unterscheiden_sich_staerker():
    kind, text = ev.verdict_schaetzung(16, 1, _s(0.010, 0.016))
    assert kind == "info" and "(0,0160 gegen 0,0100)" in text and "nicht zu unterscheiden" not in text
    assert ev.verdict_schaetzung(16, 1, _s(0.016, 0.016))[0] == "info"           # Gleichstand: „stärker“ gilt nicht


def test_verdict_schaetzung_ohne_unterschied_zwischen_instanzen():
    kind, text = ev.verdict_schaetzung(16, 0, _s(0.0149, 0.0))
    assert kind == "info" and "keinen Unterschied" in text and "Schätzrauschen" in text
    assert ev.verdict_schaetzung(16, 0, _s(0.0149, 5e-16))[0] == "info"          # Rundungsreste gelten als kein Unterschied


# ------------------------------------------------------------------------------------------------------------------ Experiment 4


def _r(n=8, nb="2-opt", quadrat=False, lo=0.65, hi=0.65):
    return {"n": n, "nachbarschaft": nb, "quadrat": quadrat, "touren": 2520, "nachbarn": 20, "instanzen": 50, "familien": 5,
            "rho1": (lo + hi) / 2, "rho2": 0.4225, "min1": lo, "max1": hi, "spanne1": hi - lo, "spanne2": 0.0}


def test_verdict_route_gleich_in_allen_instanzen():
    kind, text = ev.verdict_route(_r(hi=0.65 + 7e-16))
    assert kind == "success"
    assert "n = 8, 2-opt, 50 Instanzen aus 5 Familien, alle 2520 Touren aufgezählt" in text and "ρ(1) = **0,650000** in jeder Instanz" in text
    assert "Die Formel 1 − 2(n−1)/(n(n−3)) gibt 0,650000" in text and "Schätzrauschen" in text and "nicht die Instanz" in text
    assert R.formel_2opt(8) == 0.65


def test_verdict_route_oropt_nennt_keine_formel():
    kind, text = ev.verdict_route(_r(nb="Or-opt", lo=0.507407, hi=0.507407))
    assert kind == "success" and "Formel" not in text and "**0,507407**" in text


def test_verdict_route_meldet_keinen_instanzunterschied_bei_rundungsresten_und_einen_ab_der_schwelle():
    assert ev.verdict_route(_r(hi=0.65 + 9e-10))[0] == "success"
    kind, text = ev.verdict_route(_r(hi=0.65 + 2e-9))
    assert kind == "warning" and "unterscheiden sich" in text


def test_verdict_route_gegenprobe():
    kind, text = ev.verdict_route(_r(quadrat=True, lo=0.6430, hi=0.6499))
    assert kind == "info" and "Quadrat der Tourlänge" in text and "von 0,6430 bis 0,6499" in text and "Spanne 0,0069" in text
    kind, text = ev.verdict_route(_r(quadrat=True))
    assert kind == "info" and "auch mit dem Quadrat" in text


def _w(mittel, se):
    return {"n": 100, "familie": "gleich", "L": 20000, "wanderungen": 5, "mittel": mittel, "se": se, "exakt": 0.9796, "tau": 48.5}


def test_verdict_route_wanderung_band_vier_standardfehler():
    kind, text = ev.verdict_route_wanderung(_w(0.9799, 0.0002))
    assert kind == "success"
    assert "n = 100, 2-opt, eine Instanz (gleichverteilt), 5 Wanderungen mit je 20000 Auswertungen" in text
    assert "**0,9799**" in text and "Formel 0,9796" in text and "τ = 48,5 Schritte" in text and "Abstand 0,0003 sind 1,5 Standardfehler" in text
    assert ev.verdict_route_wanderung(_w(0.9796 + 0.00079, 0.0002))[0] == "success"       # 3,95 SE
    assert ev.verdict_route_wanderung(_w(0.9796 + 0.00081, 0.0002))[0] == "warning"       # 4,05 SE
    assert ev.verdict_route_wanderung(_w(0.9796, 0.0))[0] == "info"


def test_tau_text():
    assert ev.tau_text({"tau_median": 0.9844, "tau_gueltig": 1.0}) == "0,98"
    assert ev.tau_text({"tau_median": 2.58, "tau_gueltig": 0.23}) == ev.TAU_OHNE_SINN
    assert ev.tau_text({"tau_median": None, "tau_gueltig": 0.0}) == ev.TAU_OHNE_SINN
    assert ev.tau_sinnvoll({"tau_median": 1.0, "tau_gueltig": 0.5})
