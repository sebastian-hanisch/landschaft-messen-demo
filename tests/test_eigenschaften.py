"""Eigenschaften und Randfälle der Kernroutinen (feste Zufalls-Seeds)."""

import numpy as np
import pytest

import lsm_basis as B
import lsm_evaluation as ev
import lsm_nk as NK
import lsm_rng as G
import lsm_route as R
import lsm_scenario as S
import lsm_walk as W

# ------------------------------------------------------------------------------------------------------------------ Eigenschaften


@pytest.mark.parametrize("seed", range(20))
def test_skalieren_und_verschieben_aendert_rho_nicht(seed):
    n, k = 8, seed % 8
    f = NK.fitness_alle(NK.tabellen(n, k, seed))
    assert NK.rho_exakt(3.5 * f - 7.0, n, 3) == pytest.approx(NK.rho_exakt(f, n, 3), abs=1e-10)


@pytest.mark.parametrize("seed", range(20))
def test_spiegeln_des_bitraums_aendert_rho_und_die_zahl_der_optima_nicht(seed):
    n, k = 9, seed % 9
    f = NK.fitness_alle(NK.tabellen(n, k, seed))
    gespiegelt = f[::-1].copy()                                   # Zustand s wird zu 2^n - 1 - s: alle Bits gewechselt
    assert NK.rho_exakt(gespiegelt, n, 2) == pytest.approx(NK.rho_exakt(f, n, 2), abs=1e-10)
    assert NK.zahl_optima(gespiegelt, n) == NK.zahl_optima(f, n)


@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 12, 16])
def test_k0_gibt_exakt_eins_minus_zwei_durch_n(n):
    for seed in range(5):
        f = NK.fitness_alle(NK.tabellen(n, 0, 40 + seed))
        assert NK.rho_exakt(f, n, 1)[0] == pytest.approx(1 - 2 / n, abs=1e-10)
        assert NK.zahl_optima(f, n) == 1


@pytest.mark.parametrize("seed", range(10))
def test_k0_rho_s_ist_die_potenz(seed):
    n = 10
    rho = NK.rho_exakt(NK.fitness_alle(NK.tabellen(n, 0, seed)), n, 5)
    assert rho == pytest.approx([(1 - 2 / n) ** s for s in range(1, 6)], abs=1e-10)


@pytest.mark.parametrize("familie", S.FAMILIEN)
def test_umbenennen_der_staedte_aendert_rho_nicht(familie):
    n = 7
    d = np.array(S.route_abstaende(familie, n, 3))
    perm = [3, 0, 6, 1, 5, 2, 4]
    d2 = d[np.ix_(perm, perm)]
    for nb in R.NACHBARSCHAFTEN:
        tab = R.nachbar_tabelle(n, nb)
        a = R.rho_exakt(R.tourlaengen(d, R.alle_touren(n)), tab, 2)
        b = R.rho_exakt(R.tourlaengen(d2, R.alle_touren(n)), tab, 2)
        assert a == pytest.approx(b, abs=1e-10)


@pytest.mark.parametrize("n", [5, 6, 7, 8])
def test_2opt_rho_haengt_nicht_an_der_instanz_und_rho2_ist_das_quadrat(n):
    """40 Instanzen je n (fünf Familien zu je acht, auch nicht-euklidisch): Spanne unter 1e-10, Formel, rho(2) = rho(1)²."""
    r = ev.route_exakt(n, "2-opt", 8, 50)
    assert r["instanzen"] == 40 and r["spanne1"] < 1e-10 and r["spanne2"] < 1e-10
    for z in r["zeilen"]:
        assert z["rho1"] == pytest.approx(R.formel_2opt(n), abs=1e-10)
        assert z["rho2"] == pytest.approx(z["rho1"] ** 2, abs=1e-10)


@pytest.mark.parametrize("n", [6, 7, 8])
def test_oropt_rho_haengt_nicht_an_der_instanz_aber_rho2_liegt_ueber_dem_quadrat(n):
    r = ev.route_exakt(n, "Or-opt", 4, 50)
    assert r["instanzen"] == 20 and r["spanne1"] < 1e-10 and r["spanne2"] < 1e-10
    assert 0.001 < r["rho2"] - r["rho1"] ** 2 < 0.003
    assert r["rho1"] < R.formel_2opt(n)                             # mehr Nachbarn, kleineres rho(1)


def test_quadrat_der_laenge_haengt_an_der_instanz():
    r = ev.route_exakt(7, "2-opt", 4, 50, quadrat=True)
    assert r["spanne1"] > 1e-4


def test_jede_tour_hat_gleich_viele_verschiedene_nachbarn_und_nie_sich_selbst():
    for n in (5, 6, 7):
        for nb in R.NACHBARSCHAFTEN:
            tab = R.nachbar_tabelle(n, nb)
            for i, zeile in enumerate(tab.tolist()):
                assert len(set(zeile)) == len(zeile) and i not in zeile
            # die Nachbarschaft ist symmetrisch: i Nachbar von j genau dann, wenn j Nachbar von i
            paare = {(i, j) for i, zeile in enumerate(tab.tolist()) for j in zeile}
            assert all((j, i) in paare for i, j in paare)


def test_normalform_stellt_null_nach_vorn_und_richtet_die_tour():
    z = R.normalform(np.array([[2, 0, 1, 3], [3, 1, 0, 2], [0, 3, 2, 1]]))
    # (2,0,1,3) gedreht: (0,1,3,2), 1 < 2 bleibt. (3,1,0,2) gedreht: (0,2,3,1), 2 > 1, also umgekehrt gelesen: (0,1,3,2).
    # (0,3,2,1): 3 > 1, umgekehrt gelesen: (0,1,2,3).
    assert z.tolist() == [[0, 1, 3, 2], [0, 1, 3, 2], [0, 1, 2, 3]]


def test_wanderung_wechselt_je_schritt_genau_ein_bit_und_bleibt_im_raum():
    n = 7
    zustaende = W.nk_wanderungen(n, 500, [1, 2, 3])
    assert zustaende.min() >= 0 and zustaende.max() < (1 << n)
    wechsel = zustaende[:, 1:] ^ zustaende[:, :-1]
    assert all(bin(int(w)).count("1") == 1 for w in wechsel.reshape(-1))
    gewaehlt = {int(w).bit_length() - 1 for w in wechsel.reshape(-1)}
    assert gewaehlt == set(range(n))                                 # jedes Bit kommt vor


def test_familie_zufall_ist_symmetrisch_ganzzahlig_und_nicht_euklidisch():
    d = S.route_abstaende("zufall", 9, 0)
    assert all(d[i][j] == d[j][i] and d[i][i] == 0 for i in range(9) for j in range(9))
    assert all(float(d[i][j]).is_integer() and 1 <= d[i][j] <= S.ZUFALL_MAX for i in range(9) for j in range(9) if i != j)
    verletzt = sum(d[i][j] > d[i][m] + d[m][j] for i in range(9) for j in range(9) for m in range(9) if len({i, j, m}) == 3)
    assert verletzt > 0                                              # die Dreiecksungleichung gilt nicht
    assert S.route_abstaende("zufall", 9, 0) == d and S.route_abstaende("zufall", 9, 1) != d


def test_instanzen_der_basisfamilien_kommen_aus_der_basis():
    d = S.route_abstaende("netz", 8, 2)
    assert d == B.abstaende(B.rundtour_punkte(G.SplitMix64(B.instanz_seed("netz", 8, 2)), "netz", 8))
    assert set(S.FAMILIEN) == set(S.FAMILIEN_TEXT) and "zufall" in S.FAMILIEN


# ------------------------------------------------------------------------------------------------------------------ Randfälle


def test_konstante_landschaft_ist_nicht_definiert():
    assert NK.rho_exakt(np.full(16, 0.25), 4, 2) is None
    assert NK.zahl_optima(np.full(16, 0.25), 4) == 0                 # kein Zustand ist echt besser als alle Nachbarn
    tab = np.full((4, 2), 0.5)
    assert NK.rho_exakt(NK.fitness_alle(tab), 4, 1) is None
    assert R.rho_exakt(np.ones(12), R.nachbar_tabelle(5, "2-opt"), 2) is None


def test_ein_gen_zwei_zustaende():
    """N = 1: zwei Zustände, jeder Schritt wechselt zum anderen; rho(1) = 1 - 2/N = -1, rho(2) = +1, ein Optimum."""
    f = NK.fitness_alle(np.array([[0.2, 0.9]]))
    assert f.tolist() == [0.2, 0.9]
    assert NK.rho_exakt(f, 1, 2) == pytest.approx([-1.0, 1.0], abs=1e-12)
    assert NK.zahl_optima(f, 1) == 1


def test_zwei_gene_mit_voller_wechselwirkung():
    """N = 2, K = 1: vier unabhängige Werte je Beitrag. Von Hand: f = (b0[00] + b1[00], …)/2; hier nur die Übereinstimmung der Größen und der Formelwerte."""
    tab = np.array([[0.0, 1.0, 2.0, 3.0], [3.0, 1.0, 0.0, 2.0]])
    # Zustand s: x0 = Bit 0, x1 = Bit 1. Beitrag 0: Index 2·x0 + x1, Beitrag 1: Index 2·x1 + x0.
    # s=0 (0,0): 0 + 3 = 3; s=1 (x0=1,x1=0): 2 + 1 = 3; s=2 (x0=0,x1=1): 1 + 0 = 1; s=3 (1,1): 3 + 2 = 5; geteilt durch 2
    assert NK.fitness_alle(tab).tolist() == [1.5, 1.5, 0.5, 2.5]
    assert NK.zahl_optima(NK.fitness_alle(tab), 2) == 1               # nur s = 3 ist echt besser als beide Nachbarn (s = 0 und s = 1 sind gleich)
    assert NK.familienwert(2, 1) == 0.0
    assert NK.einzelwert_erwartung(2, 1) == pytest.approx(1 - 2 / (2 * 0.75))


def test_einzelwert_formel_bei_k_gleich_n_minus_1():
    for n in (4, 8, 16):
        assert NK.einzelwert_erwartung(n, n - 1) == pytest.approx(-(2.0 ** -n) / (1 - 2.0 ** -n), abs=1e-15)
    assert abs(NK.einzelwert_erwartung(16, 15)) < 2e-5


def test_vier_staedte_drei_touren_zwei_nachbarn():
    assert len(R.alle_touren(4)) == 3 and R.nachbar_tabelle(4, "2-opt").shape == (3, 2)
    d = [[0, 1, 5, 2], [1, 0, 3, 7], [5, 3, 0, 4], [2, 7, 4, 0]]
    # drei Touren, jede hat die beiden anderen als Nachbarn: A g = -g/2, also rho(1) = -1/2 = 1 - 2·3/(4·1)
    assert R.rho_exakt(R.tourlaengen(d, R.alle_touren(4)), R.nachbar_tabelle(4, "2-opt"), 2) == pytest.approx([-0.5, 0.25], abs=1e-12)
    assert R.formel_2opt(4) == -0.5
    with pytest.raises(ValueError):
        R.alle_touren(3)


def test_schaetzer_randfaelle():
    assert W.rho_dach([0.4, 0.4, 0.4, 0.4]) is None                   # konstante Reihe
    assert np.isnan(W.rho_dach_zeilen(np.full((1, 5), 0.4))[0])
    assert W.rho_dach([1.0, 2.0]) == pytest.approx(-0.25 / 0.25)      # L = 2: Mittel 1,5; Zähler -0,25/1; Nenner 0,5/2
    with pytest.raises(ValueError):
        W.rho_dach([1.0, 2.0], s=2)                                   # L <= s
    with pytest.raises(ValueError):
        W.rho_dach_zeilen(np.zeros((2, 3)), s=3)
    pendel = [0.2, 0.9] * 50                                          # Wanderung, die nur zwischen zwei Zuständen pendelt
    assert W.rho_dach(pendel) == pytest.approx(-1.0, abs=1e-12)
    assert W.rho_dach(pendel, 2) == pytest.approx(1.0, abs=1e-12)


def test_ungueltige_eingaben():
    with pytest.raises(ValueError):
        NK.tabellen(4, 4, 1)                                          # K höchstens N - 1
    with pytest.raises(ValueError):
        NK.tabellen(4, -1, 1)
    with pytest.raises(ValueError):
        W.nk_wanderungen(4, 0, [1])
    with pytest.raises(ValueError):
        W.route_wanderung_2opt([[0.0] * 4 for _ in range(4)], 10, G.SplitMix64(1))
    with pytest.raises(ValueError):
        R.zugliste(6, "3-opt")
    assert NK.tau(None) is None and NK.tau(0.0) is None and NK.tau(1.0) is None and NK.tau(-0.2) is None
    assert NK.tau(0.5) == pytest.approx(1.4427, abs=1e-4)             # -1/ln(1/2) = 1/ln 2


def test_wanderung_der_laenge_eins_ist_nur_der_start():
    assert W.nk_wanderungen(5, 1, [3]).shape == (1, 1)
    d = S.route_abstaende("gleich", 6, 0)
    assert len(W.route_wanderung_2opt(d, 1, G.SplitMix64(1))) == 1


def test_guete_zeile_von_hand():
    """Zwei Instanzen, zwei Schätzungen je Instanz, exakt 0,5 und 0,8."""
    m = np.array([[0.4, 0.6], [0.6, 0.9]])
    z = ev._guete_zeile(100, m, np.array([0.5, 0.8]))
    assert z["bias"] == pytest.approx((-0.1 + 0.1 - 0.2 + 0.1) / 4)
    assert z["sd_innen"] == pytest.approx(((0.02 + 0.045) / 2) ** 0.5)   # Varianzen 0,02 und 0,045 (Nenner n - 1)
    assert z["anteil_01"] == pytest.approx(0.25)                          # nur |−0,2| liegt über 0,1 (0,1 selbst zählt nicht)
    assert z["tau_gueltig"] == 1.0
    verh = sorted([np.log(0.5) / np.log(0.4), np.log(0.5) / np.log(0.6), np.log(0.8) / np.log(0.6), np.log(0.8) / np.log(0.9)])
    assert z["tau_median"] == pytest.approx((verh[1] + verh[2]) / 2)
