"""Gemeinsamer Importpfad und Hilfen der Tests: exakte Bruchrechnung als unabhängiger Rechenweg (stdlib `fractions`)."""

import itertools
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def bruch_rho(werte: dict, nachbarn, smax: int = 2) -> list:
    """rho(1) … rho(smax) in Brüchen. `werte`: Zustand -> Wert (int oder Fraction); `nachbarn(zustand)` liefert die Liste der Nachbarn."""
    zustaende = list(werte)
    mittel = Fraction(sum(werte.values()), 1) / len(zustaende)
    g = {x: Fraction(werte[x]) - mittel for x in zustaende}
    nenner = sum(v * v for v in g.values())
    nb = {x: list(nachbarn(x)) for x in zustaende}
    out, v = [], g
    for _ in range(smax):
        v = {x: sum((v[y] for y in nb[x]), Fraction(0)) / len(nb[x]) for x in zustaende}
        out.append(sum(g[x] * v[x] for x in zustaende) / nenner)
    return out


def bit_nachbarn(x: tuple) -> list:
    return [x[:b] + (1 - x[b],) + x[b + 1:] for b in range(len(x))]


def alle_bits(n: int) -> list:
    return list(itertools.product((0, 1), repeat=n))


def tour_kanten(tour) -> frozenset:
    n = len(tour)
    return frozenset(frozenset((tour[i], tour[(i + 1) % n])) for i in range(n))
