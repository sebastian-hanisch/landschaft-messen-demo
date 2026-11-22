"""Kopie-Test der gemeinsamen Basis der Linie: `lsm_basis.py` und `lsm_rng.py` sind unveränderte Kopien.

Geprüft wird gegen `tests/data/basis_eingefroren.json` (Prüfwerte der Referenzfassung: Koordinaten, Längen, NK-Werte, Seeds). Liegt die
Referenz im Nachbarordner (lokal), wird zusätzlich der Wortlaut verglichen; in der CI fehlt sie, dann überspringt sich dieser Teil."""

import json
from pathlib import Path

import pytest

import lsm_basis as B
import lsm_nk as NK
import lsm_rng as G

ROOT = Path(__file__).resolve().parent.parent
DATEN = json.loads((ROOT / "tests" / "data" / "basis_eingefroren.json").read_text(encoding="utf-8"))
PROJEKTE = ROOT.parent


def test_rundtour_instanzen_der_kopie_stimmen_mit_den_eingefrorenen_werten():
    assert len(DATEN["rundtour"]) == 12
    for e in DATEN["rundtour"]:
        assert B.instanz_seed(e["familie"], e["n"], e["idx"]) == e["seed"]
        punkte = B.rundtour_punkte(G.SplitMix64(e["seed"]), e["familie"], e["n"])
        assert len(punkte) == e["n"] == len(set(punkte))
        assert [list(p) for p in punkte[:4]] == e["erste_punkte"]
        assert sum(p[0] for p in punkte) == e["summe_x"] and sum(p[1] for p in punkte) == e["summe_y"]
        laenge = B.tourlaenge(B.abstaende(punkte), list(range(e["n"])))
        assert laenge == pytest.approx(float(e["laenge_identitaet"]), rel=1e-12)


def test_nk_werte_der_kopie_stimmen_mit_den_eingefrorenen_werten():
    assert len(DATEN["nk"]) == 6
    for e in DATEN["nk"]:
        n = e["n"]
        tab = B.nk_tabellen(G.SplitMix64(e["seed"]), n, e["k"], e["stufen"])
        zustaende = [[0] * n, [1] * n, [(i * 7 + 3) % 2 for i in range(n)], [1 if i % 3 == 0 else 0 for i in range(n)]]
        for x, erwartet in zip(zustaende, e["werte"]):
            wert = B.nk_wert(tab, x)
            if e["stufen"]:
                assert wert == int(erwartet)
            else:
                assert wert == pytest.approx(float(erwartet), rel=1e-12)


def test_lauf_seeds_der_kopie():
    assert B.lauf_seed(0, 0, 0) == DATEN["seeds"]["lauf_seed_0_0_0"]
    assert B.lauf_seed(5, 2, 7) == DATEN["seeds"]["lauf_seed_5_2_7"]


@pytest.mark.parametrize("kopie, quelle", [
    ("lsm_basis.py", PROJEKTE / "landschaften-planung" / "gemeinsam" / "lsv_basis.py"),
    ("lsm_rng.py", PROJEKTE / "sebastianhanisch-website" / "tools" / "templates" / "rng_splitmix64_exact.py"),
    ("tests/data/basis_eingefroren.json", PROJEKTE / "landschaften-planung" / "gemeinsam" / "eingefroren.json"),
])
def test_kopie_ist_wortgleich_mit_der_quelle_falls_vorhanden(kopie, quelle):
    if not quelle.exists():
        pytest.skip("Quelle nicht vorhanden (CI ohne den Nachbarordner)")
    assert (ROOT / kopie).read_text(encoding="utf-8").replace("\r\n", "\n") == quelle.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.mark.parametrize("n, k, seed", [(8, 0, 1), (12, 3, 7), (10, 9, 99), (5, 2, 3), (2, 1, 3), (1, 0, 4)])
def test_schnelle_tabellen_sind_dieselben_zahlen_wie_die_der_basis(n, k, seed):
    assert NK.tabellen(n, k, seed).tolist() == B.nk_tabellen(G.SplitMix64(seed), n, k)


def test_familie_heisst_netz():
    assert B.FAMILIEN == ("gleich", "cluster", "gitter", "netz")
