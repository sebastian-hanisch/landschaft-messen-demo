"""NK-Modell: alle 2^N Zustände auf einmal (numpy), exakte Autokorrelation über den Operator A, Zahl der lokalen Optima, die zwei Formeln.

Konvention (wie `lsm_basis.nk_tabellen`): N Gene, Beitrag i hängt an Gen i und den K zyklisch folgenden Genen; K zählt OHNE das Gen selbst.
Fitness = Mittel der N Beiträge, größer ist besser. Nachbarschaft = Wechsel eines Bits. Ein Zustand ist die ganze Zahl s mit x_i = Bit i von s."""

import math

import numpy as np

import lsm_rngblock as RB


def nk_seed(n: int, k: int, idx: int) -> int:
    """Fester Zufalls-Seed je NK-Landschaft (N, K, laufende Nummer); eigene Formel dieser Demo, getrennt von den Seeds der Rundtour-Familien."""
    return 3_000_017 + 10_007 * n + 1_009 * k + 104_729 * idx


def tabellen(n: int, k: int, seed: int) -> np.ndarray:
    """Tabellen der Landschaft (gleichverteilte Beiträge in [0, 1)): dieselben Zahlen wie `lsm_basis.nk_tabellen(SplitMix64(seed), n, k)`,
    aber blockweise mit numpy gezogen (bei K = N - 1 sind es N * 2^N Zufallszahlen) und als Matrix (N × 2^(K+1)). tests/test_basis.py prüft die Gleichheit."""
    if not 0 <= k < n:
        raise ValueError("0 <= k < n verlangt")
    groesse = 1 << (k + 1)
    z = RB.u64_block([seed], n * groesse)[0]
    werte = (z >> np.uint64(11)).astype(np.float64) / float(1 << 53)
    return werte.reshape(n, groesse)


def bits(s: int, n: int) -> list:
    """Zustand als Bitliste x_0 … x_{n-1} (x_i = Bit i von s), die Form, die `lsm_basis.nk_wert` erwartet."""
    return [(s >> i) & 1 for i in range(n)]


def fitness_alle(tab) -> np.ndarray:
    """Fitness aller 2^N Zustände: Summe der Beiträge in der Reihenfolge i = 0 … N-1 (wie `lsm_basis.nk_wert`), geteilt durch N.

    Der Tabellenindex von Beitrag i sind die Bits (x_i, x_{i+1}, …, x_{i+K}) mit x_i als höchstwertigem Bit. Gerechnet wird er aus dem um i
    Stellen gedrehten Zustand (dort steht x_i unten), die Tabelle wird dafür einmal in gespiegelter Bitfolge gelesen."""
    n = len(tab)
    k = len(tab[0]).bit_length() - 2
    groesse = 1 << (k + 1)
    w = np.arange(groesse, dtype=np.int64)
    gespiegelt = np.zeros(groesse, dtype=np.int64)        # gespiegelt[w]: Index mit x_i als höchstwertigem Bit, wenn in w x_i das niedrigste ist
    for j in range(k + 1):
        gespiegelt |= ((w >> j) & 1) << (k - j)
    s = np.arange(1 << n, dtype=np.int64)
    voll = (1 << n) - 1
    gesamt = np.zeros(1 << n)
    for i in range(n):
        gedreht = ((s >> i) | (s << (n - i))) & voll
        gesamt += np.asarray(tab[i], dtype=float)[gespiegelt][gedreht & (groesse - 1)]
    return gesamt / n


def nachbar_mittel(v: np.ndarray, n: int) -> np.ndarray:
    """Operator A: Mittel von v über die n Nachbarn (je ein Bit gewechselt). Als Würfel mit n Achsen der Länge 2 ist der Wechsel eines Bits das Spiegeln einer Achse."""
    wuerfel = v.reshape((2,) * n)
    out = np.zeros_like(wuerfel)
    for achse in range(n):
        out += np.flip(wuerfel, axis=achse)
    return out.reshape(-1) / n


def rho_exakt(f: np.ndarray, n: int, smax: int = 1):
    """Exakte Autokorrelation rho(1) … rho(smax) = <g, A^s g> / <g, g>, g = f minus Mittel über alle Zustände. Konstante Landschaft: None."""
    g = f - f.mean()
    nenner = float(g @ g)
    if nenner <= 0.0:
        return None
    out, v = [], g
    for _ in range(smax):
        v = nachbar_mittel(v, n)
        out.append(float(g @ v) / nenner)
    return out


def zahl_optima(f: np.ndarray, n: int) -> int:
    """Zahl der strengen lokalen Maxima: jeder der n Nachbarn ist echt schlechter."""
    wuerfel = f.reshape((2,) * n)
    ist = np.ones(wuerfel.shape, dtype=bool)
    for achse in range(n):
        ist &= wuerfel > np.flip(wuerfel, axis=achse)
    return int(ist.sum())


def familienwert(n: int, k: int) -> float:
    """R_1 = 1 - (K+1)/N: Korrelation mit Mittelwert und Varianz der Landschaftsfamilie."""
    return 1.0 - (k + 1) / n


def einzelwert_erwartung(n: int, k: int) -> float:
    """1 - (K+1) / (N (1 - 2^-(K+1))): Verhältnis der Erwartungen für die einzelne, mit ihrem eigenen Mittel zentrierte Landschaft.

    Für K = 0 ist das für jede nichtkonstante Landschaft exakt 1 - 2/N."""
    return 1.0 - (k + 1) / (n * (1.0 - 2.0 ** (-(k + 1))))


def tau(rho):
    """Korrelationslänge -1/ln rho(1); nur für 0 < rho < 1 definiert, sonst None. Setzt exponentiellen Abfall voraus."""
    if rho is None or not 0.0 < rho < 1.0:
        return None
    return -1.0 / math.log(rho)
