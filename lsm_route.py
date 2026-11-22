"""Rundtour: alle (n-1)!/2 Touren aufzählen, Nachbarschaften als Zugtabellen, exakte Autokorrelation.

Eine Tour steht in Normalform: Stadt 0 zuerst, zweite Stadt kleiner als die letzte (Richtung festgelegt). Die Touren stehen in
lexikographischer Reihenfolge. Ein Zug ist eine Umordnung der Positionen; er wirkt auf jede Tour gleich, darum hat jede Tour gleich viele
verschiedene Nachbarn (geprüft in tests/test_route.py).

* 2-opt: ein Abschnitt der Tour wird umgedreht; n(n-3)/2 verschiedene Nachbarn.
* Or-opt (Standardfassung der Linie: Abschnitte von 1 bis 3 Städten, in jede andere Lücke, vorwärts und rückwärts; alle verschiedenen
  Nachbartouren zählen einmal)."""

import itertools
from functools import lru_cache

import numpy as np

NACHBARSCHAFTEN = ("2-opt", "Or-opt")


def formel_2opt(n: int) -> float:
    """rho(1) der 2-opt-Wanderung auf der Tourlänge: 1 - 2(n-1) / (n(n-3)). Aufgezählt bestätigt für n = 5 bis 9 (README)."""
    return 1.0 - 2.0 * (n - 1) / (n * (n - 3))


@lru_cache(maxsize=8)
def alle_touren(n: int) -> np.ndarray:
    """Alle (n-1)!/2 Touren in Normalform, lexikographisch; Matrix (Touren × n)."""
    if n < 4:
        raise ValueError("n mindestens 4")
    zeilen = [(0,) + p for p in itertools.permutations(range(1, n)) if p[0] < p[-1]]
    return np.array(zeilen, dtype=np.int64)


def _schluessel(zeilen: np.ndarray, n: int) -> np.ndarray:
    gewichte = n ** np.arange(n - 1, -1, -1, dtype=np.int64)
    return zeilen @ gewichte


def normalform(zeilen: np.ndarray) -> np.ndarray:
    """Jede Zeile so drehen, dass Stadt 0 vorn steht, und so richten, dass die zweite Stadt kleiner ist als die letzte."""
    z = np.asarray(zeilen, dtype=np.int64)
    n = z.shape[1]
    pos0 = np.argmax(z == 0, axis=1)
    idx = (pos0[:, None] + np.arange(n)[None, :]) % n
    z = np.take_along_axis(z, idx, axis=1)
    drehen = z[:, 1] > z[:, -1]
    z[drehen, 1:] = z[drehen, 1:][:, ::-1]
    return z


def zuege_2opt(n: int) -> list:
    """Züge als Positionslisten: die Positionen i … j (1 <= i < j <= n-1, ohne (1, n-1)) werden umgedreht."""
    out = []
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            if i == 1 and j == n - 1:
                continue
            out.append(list(range(i)) + list(range(j, i - 1, -1)) + list(range(j + 1, n)))
    return out


def zuege_oropt_roh(n: int) -> list:
    """Alle Or-opt-Züge vor dem Streichen gleicher Ergebnisse: Abschnitt der Länge 1 bis 3 ab Position s, hinter jede Position der übrigen Tour, vorwärts und rückwärts."""
    out = []
    for laenge in (1, 2, 3):
        if n - laenge < 2:
            continue
        for s in range(n):
            abschnitt = [(s + k) % n for k in range(laenge)]
            rest = [(s + laenge + k) % n for k in range(n - laenge)]
            for g in range(len(rest)):
                for richtung in (abschnitt, abschnitt[::-1]):
                    out.append(rest[: g + 1] + richtung + rest[g + 1:])
    return out


def verschiedene_zuege(n: int, zuege: list) -> list:
    """Züge, die verschiedene Nachbartouren geben (ohne die Tour selbst). Entschieden an der Tour 0, 1, …, n-1: da ein Zug nur Positionen
    umordnet, gilt dieselbe Auswahl für jede Tour."""
    if not zuege:
        return []
    nf = normalform(np.array(zuege, dtype=np.int64))
    schl = _schluessel(nf, n)
    selbst = int(_schluessel(np.arange(n, dtype=np.int64)[None, :], n)[0])
    gesehen, out = {selbst}, []
    for zug, s in zip(zuege, schl.tolist()):
        if s not in gesehen:
            gesehen.add(s)
            out.append(zug)
    return out


@lru_cache(maxsize=16)
def zugliste(n: int, nachbarschaft: str) -> tuple:
    if nachbarschaft == "2-opt":
        zuege = verschiedene_zuege(n, zuege_2opt(n))
    elif nachbarschaft == "Or-opt":
        zuege = verschiedene_zuege(n, zuege_oropt_roh(n))
    else:
        raise ValueError(f"unbekannte Nachbarschaft: {nachbarschaft}")
    return tuple(tuple(z) for z in zuege)


@lru_cache(maxsize=16)
def nachbar_tabelle(n: int, nachbarschaft: str) -> np.ndarray:
    """Matrix (Touren × Nachbarn): Nummer der Nachbartour je Tour und Zug."""
    touren = alle_touren(n)
    schl = _schluessel(touren, n)                     # aufsteigend, weil die Touren lexikographisch stehen
    zuege = zugliste(n, nachbarschaft)
    tab = np.empty((len(touren), len(zuege)), dtype=np.int64)
    for c, zug in enumerate(zuege):
        ziel = _schluessel(normalform(touren[:, list(zug)]), n)
        pos = np.searchsorted(schl, ziel)
        if not np.array_equal(schl[pos], ziel):
            raise AssertionError("Nachbartour nicht in der Aufzählung")
        tab[:, c] = pos
    return tab


def tourlaengen(d, touren: np.ndarray) -> np.ndarray:
    """Länge jeder Tour; summiert in Tourreihenfolge ab Position 0 (wie `lsm_basis.tourlaenge`)."""
    dm = np.asarray(d, dtype=float)
    n = touren.shape[1]
    gesamt = np.zeros(len(touren))
    for i in range(n):
        gesamt += dm[touren[:, i], touren[:, (i + 1) % n]]
    return gesamt


def rho_exakt(werte: np.ndarray, tabelle: np.ndarray, smax: int = 2):
    """rho(1) … rho(smax) = <g, A^s g> / <g, g> über alle Touren; A = Mittel über die Nachbarn. Konstante Werte: None."""
    g = werte - werte.mean()
    nenner = float(g @ g)
    if nenner <= 0.0:
        return None
    out, v = [], g
    for _ in range(smax):
        v = v[tabelle].mean(axis=1)
        out.append(float(g @ v) / nenner)
    return out
