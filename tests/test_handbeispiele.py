"""Die Handbeispiele als exakte Tests: jeder Sollwert ist ein Bruch, gerechnet mit `fractions` auf einem eigenen Rechenweg (conftest.bruch_rho),
und die Routinen der Demo (Gleitkomma) müssen ihn auf 1e-12 treffen."""

import itertools
import math
from fractions import Fraction as Fr

import numpy as np
import pytest

import lsm_nk as NK
import lsm_route as R
import lsm_walk as W
from conftest import alle_bits, bit_nachbarn, bruch_rho, tour_kanten


def _nk_bruch(n, k, tab):
    """Fitness in Brüchen, Index wie in der Basis: Bits (x_i, …, x_{i+k}) mit x_i als höchstwertigem Bit."""
    out = {}
    for x in alle_bits(n):
        s = Fr(0)
        for i in range(n):
            index = 0
            for j in range(k + 1):
                index = (index << 1) | x[(i + j) % n]
            s += Fr(tab[i][index])
        out[x] = s / n
    return out


def _demo_rho(tab, smax):
    f = NK.fitness_alle(np.array(tab, dtype=float))
    return NK.rho_exakt(f, len(tab), smax)


# ---------------------------------------------------------------------------------------------- 1. K = 0, N = 4


@pytest.mark.parametrize("tab", [[(0, 1)] * 4, [(0, 3), (1, 2), (5, 0), (2, 2)], [(7, 7), (0, 1), (4, 9), (3, 8)]])
def test_k0_n4_rho1_ist_ein_halb_und_rho2_ein_viertel(tab):
    bruch = bruch_rho(_nk_bruch(4, 0, tab), bit_nachbarn, 2)
    assert bruch == [Fr(1, 2), Fr(1, 4)]
    assert _demo_rho(tab, 2) == pytest.approx([0.5, 0.25], abs=1e-12)


def test_k0_n4_rho_s_ist_die_potenz_bis_s5():
    tab = [(0, 3), (1, 2), (5, 0), (2, 2)]
    assert bruch_rho(_nk_bruch(4, 0, tab), bit_nachbarn, 5) == [Fr(1, 2) ** s for s in range(1, 6)]
    assert _demo_rho(tab, 5) == pytest.approx([0.5 ** s for s in range(1, 6)], abs=1e-12)
    assert _demo_rho(tab, 5)[4] == pytest.approx(1 / 32, abs=1e-12)
    assert Fr(3, 4) ** 5 == Fr(243, 1024)                      # der Familienwert hoch 5 wäre etwas anderes
    assert NK.familienwert(4, 0) == 0.75 and NK.einzelwert_erwartung(4, 0) == 0.5


# ---------------------------------------------------------------------------------------------- 2. N = 3, K = 0, alle 64 Tabellen


def test_n3_k0_alle_64_tabellen_familienmittel_zwei_drittel_einzelwert_ein_drittel():
    zaehler = nenner = Fr(0)
    mu = Fr(1, 2)
    einzel, konstant = [], 0
    for bits in itertools.product((0, 1), repeat=6):
        tab = [(bits[2 * i], bits[2 * i + 1]) for i in range(3)]
        f = _nk_bruch(3, 0, tab)
        for x in f:
            nenner += (f[x] - mu) ** 2
            for y in bit_nachbarn(x):
                zaehler += (f[x] - mu) * (f[y] - mu) / 3
        demo = _demo_rho(tab, 1)
        if len(set(f.values())) > 1:
            einzel.append(bruch_rho(f, bit_nachbarn, 1)[0])
            assert demo[0] == pytest.approx(1 / 3, abs=1e-12)
        else:
            konstant += 1
            assert demo is None                                 # konstante Landschaft: nicht definiert
    assert zaehler / nenner == Fr(2, 3) and NK.familienwert(3, 0) == pytest.approx(2 / 3)
    assert len(einzel) == 56 and all(r == Fr(1, 3) for r in einzel) and konstant == 8
    assert NK.einzelwert_erwartung(3, 0) == pytest.approx(1 / 3)


# ---------------------------------------------------------------------------------------------- 3. N = 3, K = 1


def test_n3_k1_verhaeltnis_der_erwartungen_ist_ein_neuntel():
    """Alle 4096 Tabellen mit Werten 0 oder 1: Summe der Zähler durch Summe der Nenner, mit den Routinen der Demo gerechnet, gegen den Bruch 1/9."""
    zaehler = nenner = 0.0
    for bits in itertools.product((0, 1), repeat=12):
        f = NK.fitness_alle(np.array(bits, dtype=float).reshape(3, 4))
        g = f - f.mean()
        zaehler += float(g @ NK.nachbar_mittel(g, 3))
        nenner += float(g @ g)
    assert zaehler / nenner == pytest.approx(1 / 9, abs=1e-12)
    assert 1 - Fr(2, 3) / (1 - Fr(1, 4)) == Fr(1, 9)
    assert NK.einzelwert_erwartung(3, 1) == pytest.approx(1 / 9, abs=1e-15)
    assert NK.familienwert(3, 1) == pytest.approx(1 / 3)        # die Familienformel gäbe 1/3


def test_n3_k1_beispiel_landschaft_fuenf_neunzehntel_und_ein_neuntel():
    # Handbeispiel: Tabellen 0|3|1|2, 2|0|3|1, 1|2|0|3 mit Index x_i + 2·x_{i+1}; in der Bitfolge der Basis (x_i höchstwertig) sind die mittleren Einträge vertauscht
    hand = [(0, 3, 1, 2), (2, 0, 3, 1), (1, 2, 0, 3)]
    tab = [(t[0], t[2], t[1], t[3]) for t in hand]
    f = _nk_bruch(3, 1, tab)
    assert [f[x] for x in sorted(f)] == [Fr(1), Fr(5, 3), Fr(2, 3), Fr(4, 3), Fr(5, 3), Fr(3), Fr(2, 3), Fr(2)]
    assert sum(f.values()) / 8 == Fr(3, 2)
    r1, r2 = bruch_rho(f, bit_nachbarn, 2)
    assert r1 == Fr(5, 19) and r2 == Fr(1, 9) and r1 ** 2 == Fr(25, 361) and r2 > r1 ** 2
    assert _demo_rho(tab, 2) == pytest.approx([5 / 19, 1 / 9], abs=1e-12)


# ---------------------------------------------------------------------------------------------- 4. Verzerrung des Schätzers


def _bruch_dach(reihe):
    laenge = len(reihe)
    mittel = sum(reihe) / laenge
    c = [v - mittel for v in reihe]
    return (sum(c[t] * c[t + 1] for t in range(laenge - 1)) / (laenge - 1)) / (sum(v * v for v in c) / laenge)


def _erwartung(n, laenge):
    """Exakte Erwartung des Schätzers über alle Wanderungen: die Zahl der Einsen ist eine Markow-Kette, Start binomialverteilt.
    Rückgabe: (Bruch aus der Bruchrechnung, Gleitkommawert mit `lsm_walk.rho_dach` für jede Reihe)."""
    bruch, gleit = Fr(0), 0.0

    def rec(reihe, p):
        nonlocal bruch, gleit
        if len(reihe) == laenge:
            if len(set(reihe)) > 1:
                bruch += p * _bruch_dach(reihe)
                gleit += float(p) * W.rho_dach([float(v) for v in reihe])
            return
        k = reihe[-1]
        if k < n:
            rec(reihe + [k + 1], p * Fr(n - k, n))
        if k > 0:
            rec(reihe + [k - 1], p * Fr(k, n))

    for k0 in range(n + 1):
        rec([Fr(k0)], Fr(math.comb(n, k0), 2 ** n))
    return bruch, gleit


def test_schaetzer_von_hand_l3():
    assert W.rho_dach([1, 2, 1]) == pytest.approx(-1.0, abs=1e-12)     # Mittel 4/3, Zähler -2/9, Nenner 2/9
    assert W.rho_dach([1, 2, 3]) == pytest.approx(0.0, abs=1e-12)      # Zähler 0
    assert _bruch_dach([Fr(1), Fr(2), Fr(1)]) == -1 and _bruch_dach([Fr(1), Fr(2), Fr(3)]) == 0


def test_erwartung_des_schaetzers_ist_minus_fuenf_achtel_und_minus_fuenf_sechzehntel():
    for laenge, soll in ((3, Fr(-5, 8)), (4, Fr(-5, 16))):
        bruch, gleit = _erwartung(4, laenge)
        assert bruch == soll
        assert gleit == pytest.approx(float(soll), abs=1e-12)


def test_verzerrung_ist_negativ_und_schrumpft_mit_l():
    exakt = Fr(1, 2)
    werte = {laenge: _erwartung(4, laenge)[0] for laenge in (3, 6, 8, 10)}
    assert all(v < exakt for v in werte.values())
    assert abs(werte[10] - exakt) < abs(werte[8] - exakt) < abs(werte[6] - exakt) < abs(werte[3] - exakt)
    assert float(werte[8]) == pytest.approx(0.1124, abs=5e-5) and float(werte[10]) == pytest.approx(0.1979, abs=5e-5)


# ---------------------------------------------------------------------------------------------- 5. Rundtour

D5A = [[0, 3, 5, 7, 4], [3, 0, 2, 6, 5], [5, 2, 0, 3, 8], [7, 6, 3, 0, 2], [4, 5, 8, 2, 0]]
D5B = [[0, 9, 1, 1, 9], [9, 0, 9, 9, 1], [1, 9, 0, 1, 9], [1, 9, 1, 0, 9], [9, 1, 9, 9, 0]]
D5C = [[0, 1, 2, 3, 4], [1, 0, 1, 2, 3], [2, 1, 0, 1, 2], [3, 2, 1, 0, 1], [4, 3, 2, 1, 0]]
D6 = [[0, 4, 6, 3, 8, 2], [4, 0, 5, 7, 1, 9], [6, 5, 0, 2, 4, 6], [3, 7, 2, 0, 9, 5], [8, 1, 4, 9, 0, 3], [2, 9, 6, 5, 3, 0]]


def _route_bruch(d, quadrat=False):
    """Unabhängiger Rechenweg: Touren als Kantenmengen; 2-opt-Nachbarn sind die Touren, die sich in genau zwei Kanten unterscheiden."""
    n = len(d)
    touren = [(0,) + p for p in itertools.permutations(range(1, n)) if p[0] < p[-1]]
    kanten = {t: tour_kanten(t) for t in touren}
    werte = {t: sum(d[t[i]][t[(i + 1) % n]] for i in range(n)) ** (2 if quadrat else 1) for t in touren}
    nachbarn = {t: [u for u in touren if len(kanten[t] - kanten[u]) == 2] for t in touren}
    return bruch_rho(werte, lambda t: nachbarn[t], 2), len(touren), len(nachbarn[touren[0]])


@pytest.mark.parametrize("d", [D5A, D5B, D5C])
def test_fuenf_staedte_rho1_ein_fuenftel(d):
    (r1, r2), touren, nachbarn = _route_bruch(d)
    assert (touren, nachbarn) == (12, 5) and r1 == Fr(1, 5) and r2 == Fr(1, 25)
    demo = R.rho_exakt(R.tourlaengen(d, R.alle_touren(5)), R.nachbar_tabelle(5, "2-opt"), 2)
    assert demo == pytest.approx([0.2, 0.04], abs=1e-12)


def test_sechs_staedte_rho1_vier_neuntel():
    (r1, r2), touren, nachbarn = _route_bruch(D6)
    assert (touren, nachbarn) == (60, 9) and r1 == Fr(4, 9) and r2 == Fr(16, 81)
    demo = R.rho_exakt(R.tourlaengen(D6, R.alle_touren(6)), R.nachbar_tabelle(6, "2-opt"), 2)
    assert demo == pytest.approx([4 / 9, 16 / 81], abs=1e-12)


def test_formel_gibt_die_brueche_der_aufzaehlung():
    soll = {5: Fr(1, 5), 6: Fr(4, 9), 7: Fr(4, 7), 8: Fr(13, 20), 9: Fr(19, 27)}
    for n, bruch in soll.items():
        assert 1 - Fr(2 * (n - 1), n * (n - 3)) == bruch
        assert R.formel_2opt(n) == pytest.approx(float(bruch), abs=1e-15)
    assert 48 < NK.tau(R.formel_2opt(100)) < 49                 # Korrelationslänge etwa n/2


def test_gegenprobe_quadrat_der_laenge_gibt_drei_verschiedene_werte():
    soll = [Fr(145297, 751765), Fr(1, 5), Fr(299, 1505)]
    for d, bruch in zip((D5A, D5B, D5C), soll):
        (r1, _), _, _ = _route_bruch(d, quadrat=True)
        assert r1 == bruch
        laengen = R.tourlaengen(d, R.alle_touren(5))
        assert R.rho_exakt(laengen * laengen, R.nachbar_tabelle(5, "2-opt"), 1)[0] == pytest.approx(float(bruch), abs=1e-12)
    assert len(set(soll)) == 3
