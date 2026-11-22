"""Szenario: Instanzen der beiden Aufgaben. Alle Instanzen sind erfunden (Zufallszahlen aus SplitMix64), keine reale Datenquelle.

* NK-Landschaften: Tabellen aus `lsm_nk.tabellen` (dieselben Zahlen wie die gemeinsame Basis `lsm_basis.nk_tabellen`).
* Rundtouren: die vier Familien der gemeinsamen Basis (`lsm_basis.rundtour_punkte`, ganzzahlige Koordinaten) und zusätzlich die Familie
  „zufall“ dieser Demo: eine symmetrische Abstandsmatrix aus ganzen Zufallszahlen ohne Lage in der Ebene (nicht-euklidisch)."""

import lsm_basis as B
import lsm_rng as G

FAMILIE_ZUFALL = "zufall"
FAMILIEN = B.FAMILIEN + (FAMILIE_ZUFALL,)
FAMILIEN_TEXT = dict(B.FAMILIEN_TEXT)
FAMILIEN_TEXT["netz"] = "Straßennetz"
FAMILIEN_TEXT[FAMILIE_ZUFALL] = "Zufallsmatrix (nicht-euklidisch)"
ZUFALL_MAX = 9999   # Einträge der Zufallsmatrix: ganze Zahlen 1 … ZUFALL_MAX


def zufall_seed(n: int, idx: int) -> int:
    """Fester Zufalls-Seed der Familie „zufall“ (eigene Formel dieser Demo, getrennt von `lsm_basis.instanz_seed`)."""
    return 5_000_011 + 7919 * n + 104_729 * idx


def zufallsmatrix(rng, n: int) -> list:
    """Symmetrische Matrix mit ganzzahligen Einträgen 1 … ZUFALL_MAX oberhalb der Diagonale, Diagonale 0."""
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d[i][j] = d[j][i] = float(1 + rng.below(ZUFALL_MAX))
    return d


def route_abstaende(familie: str, n: int, idx: int) -> list:
    """Abstandsmatrix der Instanz (Familie, n, laufende Nummer)."""
    if familie == FAMILIE_ZUFALL:
        return zufallsmatrix(G.SplitMix64(zufall_seed(n, idx)), n)
    return B.abstaende(B.rundtour_punkte(G.SplitMix64(B.instanz_seed(familie, n, idx)), familie, n))
