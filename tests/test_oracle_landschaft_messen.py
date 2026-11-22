"""Orakel-Tests landschaft-messen-demo: jede Kernroutine gegen einen anderen Rechenweg.

* exakte Autokorrelation (Operator A über gespiegelte Achsen) gegen die Matrixpotenz einer ausgeschriebenen Übergangsmatrix
* NK-Fitness (alle Zustände auf einmal) gegen die Direktberechnung je Zustand aus der gemeinsamen Basis
* Zahl der lokalen Optima gegen eine Schleife über alle Zustände; bei K = N-1 gegen die Erwartung 2^N/(N+1) (Band)
* Rundtour: Zahl der Touren, Nachbarzahlen und Nachbarmengen gegen eine Zählung über Kantenmengen; kürzeste Tour gegen Bellman-Held-Karp
* Zufallswanderungen gegen den exakten Wert (Band von 4 Standardfehlern)
Die Bruch-Orakel der Handbeispiele stehen in tests/test_handbeispiele.py."""

import itertools
import math

import numpy as np
import pytest

import lsm_basis as B
import lsm_evaluation as ev
import lsm_nk as NK
import lsm_rng as G
import lsm_route as R
import lsm_scenario as S
import lsm_walk as W
from conftest import tour_kanten

NK_FAELLE = [(n, k, seed) for n in (3, 5, 8) for k in (0, 1, n - 1) for seed in (1, 2)]


@pytest.mark.parametrize("n, k, seed", NK_FAELLE)
def test_rho_exakt_gegen_matrixpotenz_der_uebergangsmatrix(n, k, seed):
    f = NK.fitness_alle(NK.tabellen(n, k, seed))
    m = 1 << n
    p = np.zeros((m, m))
    for s in range(m):
        for b in range(n):
            p[s, s ^ (1 << b)] = 1.0 / n
    g = f - f.mean()
    soll = [float(g @ np.linalg.matrix_power(p, s) @ g) / float(g @ g) for s in range(1, 6)]
    assert NK.rho_exakt(f, n, 5) == pytest.approx(soll, abs=1e-12)


@pytest.mark.parametrize("n, k, seed", [(6, 0, 3), (7, 3, 4), (9, 8, 5), (10, 2, 6)])
def test_fitness_aller_zustaende_gegen_direktberechnung_je_zustand(n, k, seed):
    tab = NK.tabellen(n, k, seed)
    f = NK.fitness_alle(tab)
    for s in range(1 << n):
        assert f[s] == pytest.approx(B.nk_wert(tab.tolist(), NK.bits(s, n)) / n, rel=1e-12)


@pytest.mark.parametrize("n, k, seed", [(4, 0, 1), (6, 2, 2), (8, 7, 3), (10, 4, 4), (10, 9, 5)])
def test_zahl_der_optima_gegen_schleife(n, k, seed):
    f = NK.fitness_alle(NK.tabellen(n, k, seed))
    soll = sum(all(f[s] > f[s ^ (1 << b)] for b in range(n)) for s in range(1 << n))
    assert NK.zahl_optima(f, n) == soll


def test_zahl_der_optima_bei_k_gleich_n_minus_1_liegt_im_band_um_die_erwartung():
    n = 12
    zahlen = [NK.zahl_optima(NK.fitness_alle(NK.tabellen(n, n - 1, NK.nk_seed(n, n - 1, i))), n) for i in range(30)]
    erwartung = 2 ** n / (n + 1)
    assert abs(np.mean(zahlen) - erwartung) < 0.03 * erwartung


# ------------------------------------------------------------------------------------------------------------------ Rundtour


def _alle_touren_unabhaengig(n):
    return [(0,) + p for p in itertools.permutations(range(1, n)) if p[0] < p[-1]]


def _oropt_nachbarn_knotensprache(tour):
    """Or-opt in Knotensprache: einen Abschnitt von 1 bis 3 aufeinanderfolgenden Städten herausnehmen und zwischen zwei aufeinanderfolgende
    Städte des Rests setzen, vorwärts oder rückwärts. Rückgabe: Menge der Kantenmengen der verschiedenen Nachbartouren."""
    n = len(tour)
    selbst = tour_kanten(tour)
    out = set()
    for laenge in (1, 2, 3):
        if n - laenge < 2:
            continue
        for start in range(n):
            abschnitt = [tour[(start + i) % n] for i in range(laenge)]
            rest = [tour[(start + laenge + i) % n] for i in range(n - laenge)]
            for luecke in range(len(rest)):
                for richtung in (abschnitt, abschnitt[::-1]):
                    neu = rest[: luecke + 1] + richtung + rest[luecke + 1:]
                    kanten = tour_kanten(neu)
                    if kanten != selbst:
                        out.add(kanten)
    return out


@pytest.mark.parametrize("n", [4, 5, 6, 7, 8, 9])
def test_zahl_der_touren_und_der_2opt_nachbarn(n):
    touren = R.alle_touren(n)
    assert len(touren) == math.factorial(n - 1) // 2
    assert [tuple(t) for t in touren.tolist()] == _alle_touren_unabhaengig(n)        # dieselbe lexikographische Reihenfolge
    assert R.nachbar_tabelle(n, "2-opt").shape[1] == n * (n - 3) // 2


@pytest.mark.parametrize("n", [5, 6, 7])
def test_2opt_nachbarn_sind_genau_die_touren_mit_zwei_anderen_kanten(n):
    touren = [tuple(t) for t in R.alle_touren(n).tolist()]
    kanten = [tour_kanten(t) for t in touren]
    tab = R.nachbar_tabelle(n, "2-opt")
    for i in range(len(touren)):
        soll = {j for j in range(len(touren)) if len(kanten[i] - kanten[j]) == 2}
        assert set(tab[i].tolist()) == soll and len(soll) == tab.shape[1]


@pytest.mark.parametrize("n, zahl", [(5, 10), (6, 29), (7, 63), (8, 108)])
def test_oropt_nachbarn_gegen_zaehlung_in_knotensprache(n, zahl):
    touren = [tuple(t) for t in R.alle_touren(n).tolist()]
    nummer = {tour_kanten(t): i for i, t in enumerate(touren)}
    tab = R.nachbar_tabelle(n, "Or-opt")
    assert tab.shape[1] == zahl
    for i in range(0, len(touren), max(1, len(touren) // 60)):                         # jede Tour bei kleinen n, sonst etwa 60 Stichproben
        soll = {nummer[k] for k in _oropt_nachbarn_knotensprache(touren[i])}
        assert set(tab[i].tolist()) == soll and len(soll) == zahl


def test_oropt_hat_bei_neun_staedten_165_nachbarn():
    assert len(R.zugliste(9, "Or-opt")) == 165 and len(R.zugliste(9, "2-opt")) == 27


def _held_karp(d):
    """Bellman-Held-Karp (dynamische Programmierung über Teilmengen), die kürzeste Rundtour; nicht die 1-Baum-Schranke gleichen Namens."""
    n = len(d)
    beste = {(1 << j, j): d[0][j] for j in range(1, n)}
    for groesse in range(2, n):
        for teil in itertools.combinations(range(1, n), groesse):
            maske = sum(1 << j for j in teil)
            for j in teil:
                vor = maske ^ (1 << j)
                beste[(maske, j)] = min(beste[(vor, i)] + d[i][j] for i in teil if i != j)
    voll = sum(1 << j for j in range(1, n))
    return min(beste[(voll, j)] + d[j][0] for j in range(1, n))


@pytest.mark.parametrize("familie, n, idx", [("gleich", 6, 0), ("cluster", 7, 1), ("gitter", 8, 2), ("netz", 9, 3), ("zufall", 9, 4)])
def test_kuerzeste_tour_der_aufzaehlung_gegen_held_karp(familie, n, idx):
    d = S.route_abstaende(familie, n, idx)
    laengen = R.tourlaengen(d, R.alle_touren(n))
    assert float(laengen.min()) == pytest.approx(_held_karp(d), rel=1e-9)


@pytest.mark.parametrize("familie, n, idx", [("gleich", 6, 0), ("netz", 7, 5), ("zufall", 8, 2)])
def test_tourlaengen_gegen_die_basis(familie, n, idx):
    d = S.route_abstaende(familie, n, idx)
    touren = R.alle_touren(n)
    laengen = R.tourlaengen(d, touren)
    for i in range(0, len(touren), 7):
        assert laengen[i] == pytest.approx(B.tourlaenge(d, touren[i].tolist()), rel=1e-12)


@pytest.mark.parametrize("n, nachbarschaft", [(6, "2-opt"), (6, "Or-opt"), (7, "Or-opt")])
def test_rho_der_rundtour_gegen_matrixpotenz(n, nachbarschaft):
    d = S.route_abstaende("gleich", n, 0)
    w = R.tourlaengen(d, R.alle_touren(n))
    tab = R.nachbar_tabelle(n, nachbarschaft)
    p = np.zeros((len(w), len(w)))
    for i in range(len(w)):
        p[i, tab[i]] = 1.0 / tab.shape[1]
    g = w - w.mean()
    soll = [float(g @ np.linalg.matrix_power(p, s) @ g) / float(g @ g) for s in (1, 2)]
    assert R.rho_exakt(w, tab, 2) == pytest.approx(soll, abs=1e-12)


# ------------------------------------------------------------------------------------------------------------------ Wanderung gegen exakt


def _im_band(werte, exakt, faktor=4.0):
    se = ev.sd(werte) / math.sqrt(len(werte))
    return abs(float(np.mean(werte)) - exakt) <= faktor * se


def test_nk_wanderung_laeuft_gegen_den_exakten_wert():
    n, k = 10, 3
    f = NK.fitness_alle(NK.tabellen(n, k, 21))
    exakt = NK.rho_exakt(f, n, 1)[0]
    werte = W.rho_dach_zeilen(f[W.nk_wanderungen(n, 20000, list(range(100, 140)))])
    assert _im_band(werte, exakt)
    assert abs(float(np.mean(werte)) - exakt) < 0.01


@pytest.mark.parametrize("n, laenge, wanderungen", [(9, 20000, 10), (30, 30000, 8)])
def test_route_wanderung_laeuft_gegen_die_formel(n, laenge, wanderungen):
    d = S.route_abstaende("gleich", n, 0)
    werte = [W.rho_dach(W.route_wanderung_2opt(d, laenge, G.SplitMix64(500 + w))) for w in range(wanderungen)]
    assert _im_band(werte, R.formel_2opt(n))
    assert abs(float(np.mean(werte)) - R.formel_2opt(n)) < 0.01


def test_route_wanderung_schreibt_die_laenge_richtig_fort():
    """Nachsimulation mit demselben Zufallsstrom: jede fortgeschriebene Länge gegen die volle Neuberechnung der Tour."""
    n, laenge = 12, 300
    d = S.route_abstaende("cluster", n, 0)
    reihe = W.route_wanderung_2opt(d, laenge, G.SplitMix64(9))
    rng = G.SplitMix64(9)
    tour = list(range(n))
    rng.shuffle(tour)
    assert reihe[0] == pytest.approx(B.tourlaenge(d, tour), rel=1e-12)
    for t in range(1, laenge):
        while True:
            i, j = 1 + rng.below(n - 1), 1 + rng.below(n - 1)
            if i > j:
                i, j = j, i
            if i != j and not (i == 1 and j == n - 1):
                break
        vorher = tour_kanten(tour)
        tour[i:j + 1] = tour[i:j + 1][::-1]
        assert len(vorher - tour_kanten(tour)) == 2                 # jeder Schritt führt zu einem echten 2-opt-Nachbarn
        assert reihe[t] == pytest.approx(B.tourlaenge(d, tour), rel=1e-9)


def test_schaetzer_gegen_numpy_korrelation_der_definition():
    reihe = np.array([0.3, 0.9, 0.1, 0.5, 0.7, 0.2, 0.8, 0.4])
    for s in (1, 2, 3):
        c = reihe - reihe.mean()
        soll = (sum(c[t] * c[t + s] for t in range(len(c) - s)) / (len(c) - s)) / (sum(v * v for v in c) / len(c))
        assert W.rho_dach(reihe, s) == pytest.approx(soll, abs=1e-14)
        assert W.rho_dach_zeilen(reihe[None, :], s)[0] == pytest.approx(soll, abs=1e-14)
