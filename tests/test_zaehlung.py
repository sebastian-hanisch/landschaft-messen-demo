"""Zähltest: die angezeigten Auswertungen stimmen an Mini-Instanzen mit der Handzählung überein.

Budget-Einheit der Reihe ist die Auswertung. In dieser Demo gibt es zwei Kostenarten: eine Wanderung der Länge L (L Auswertungen: der Start und
L - 1 Nachbarn) und die vollständige Aufzählung (2^N Zustände bzw. (n-1)!/2 Touren)."""

import lsm_evaluation as ev
import lsm_rng as G
import lsm_route as R
import lsm_scenario as S
import lsm_walk as W


class ZaehlMatrix(list):
    """Abstandsmatrix, die jeden Zugriff auf einen Eintrag zählt."""

    def __init__(self, d):
        self.zugriffe = 0
        aussen = self

        class Zeile(list):
            def __getitem__(self, j):
                aussen.zugriffe += 1
                return list.__getitem__(self, j)

        super().__init__(Zeile(z) for z in d)


def test_route_wanderung_fuenf_staedte_vier_auswertungen_von_hand():
    """n = 5, L = 4. Handzählung: die Startlänge liest 5 Kanten (eine Auswertung), jeder der 3 Schritte liest 4 Kanten (eine Auswertung je
    Nachbar: zwei entfernte, zwei neue Kanten). Das sind 5 + 3·4 = 17 Zugriffe und 4 Werte."""
    d = ZaehlMatrix(S.route_abstaende("gleich", 5, 0))
    reihe = W.route_wanderung_2opt(d, 4, G.SplitMix64(3))
    assert len(reihe) == 4
    assert d.zugriffe == 5 + 3 * 4 == 17


def test_route_wanderung_zaehlt_allgemein_n_plus_vier_je_schritt():
    for n, laenge in ((6, 1), (8, 50), (12, 200)):
        d = ZaehlMatrix(S.route_abstaende("cluster", n, 1))
        assert len(W.route_wanderung_2opt(d, laenge, G.SplitMix64(n))) == laenge
        assert d.zugriffe == n + 4 * (laenge - 1)


def test_nk_wanderung_hat_genau_l_zustaende():
    for laenge in (1, 2, 50, 1000):
        assert W.nk_wanderungen(6, laenge, [5]).shape == (1, laenge)
    land = ev.landschaft(4, 0, 1)
    assert len(ev.profil(land["f"], 4, 1, 50, 1)["reihe"]) == 50


def test_aufzaehlung_kostet_zwei_hoch_n_bzw_die_zahl_der_touren():
    assert len(ev.landschaft(4, 0, 1)["f"]) == 16                 # von Hand: 2^4
    assert len(ev.landschaft(3, 2, 1)["f"]) == 8
    r = ev.route_exakt(5, "2-opt", 1, 0)
    assert r["touren"] == 12 and r["nachbarn"] == 5                # von Hand: 4!/2 = 12 Touren, 5·2/2 = 5 Nachbarn
    assert ev.route_exakt(6, "Or-opt", 1, 0)["touren"] == 60       # 5!/2
    assert len(R.alle_touren(7)) == 360                            # 6!/2


def test_guete_zaehlt_instanzen_mal_wanderungen_schaetzungen():
    s = ev.schaetzung(5, 1, 0, 3, 4, laengen=(20, 40), mit_werten=True)
    assert s["instanzen"] == 3 and s["wanderungen"] == 4
    assert [len(z["fehler"]) for z in s["zeilen"]] == [12, 12]     # Zähleinheit Schätzung: 3 Instanzen × 4 Wanderungen je Länge
    w = ev.route_wanderung(6, "gleich", 0, wanderungen=3, laenge=200)
    assert w["wanderungen"] == 3 and len(w["werte"]) == 3 and w["L"] == 200
