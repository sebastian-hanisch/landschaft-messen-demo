"""Zufallswanderungen und der Schätzer der Autokorrelation.

Eine Wanderung der Länge L besteht aus L Zuständen (L Auswertungen der Zielfunktion): ein gleichverteilter Start, danach L - 1 Schritte zu je
einem gleichverteilt gewählten Nachbarn. Der Zufall kommt aus SplitMix64 (blockweise, bitgleich zur skalaren Vorlage)."""

import numpy as np

import lsm_rngblock as RB


def rho_dach(reihe, s: int = 1):
    """Schätzer: Kovarianz bei Verschiebung s (Summe durch L - s) durch Varianz (Summe durch L), beide mit dem Stichprobenmittel der Reihe.

    Konstante Reihe: None (nicht definiert). L <= s: ValueError."""
    r = np.asarray(reihe, dtype=float)
    laenge = len(r)
    if laenge <= s:
        raise ValueError("Die Wanderung muss länger sein als der Schrittabstand s")
    c = r - r.mean()
    nenner = float(c @ c) / laenge
    if nenner <= 0.0:
        return None
    return float(c[: laenge - s] @ c[s:]) / (laenge - s) / nenner


def rho_dach_zeilen(reihen: np.ndarray, s: int = 1) -> np.ndarray:
    """Wie `rho_dach`, für jede Zeile einer Matrix (Wanderungen × L); konstante Zeilen geben nan."""
    r = np.asarray(reihen, dtype=float)
    laenge = r.shape[1]
    if laenge <= s:
        raise ValueError("Die Wanderung muss länger sein als der Schrittabstand s")
    c = r - r.mean(axis=1, keepdims=True)
    nenner = (c * c).sum(axis=1) / laenge
    zaehler = (c[:, : laenge - s] * c[:, s:]).sum(axis=1) / (laenge - s)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(nenner > 0.0, zaehler / nenner, np.nan)


def nk_wanderungen(n: int, laenge: int, seeds) -> np.ndarray:
    """Matrix (Zahl der Zufalls-Seeds × laenge) von Zuständen: Zeile w ist die Wanderung mit dem Zufalls-Seed seeds[w].

    Die erste Zufallszahl wählt den Start (modulo 2^N), jede weitere das Bit, das wechselt (modulo N)."""
    if laenge < 1:
        raise ValueError("Länge mindestens 1")
    z = RB.u64_block(seeds, laenge)
    schritte = np.empty(z.shape, dtype=np.int64)
    schritte[:, 0] = (z[:, 0] % np.uint64(1 << n)).astype(np.int64)
    if laenge > 1:
        schritte[:, 1:] = np.int64(1) << (z[:, 1:] % np.uint64(n)).astype(np.int64)
    return np.bitwise_xor.accumulate(schritte, axis=1)


def route_wanderung_2opt(d: list, laenge: int, rng) -> list:
    """Tourlängen entlang einer Zufallswanderung in der 2-opt-Nachbarschaft (L Werte, L Auswertungen).

    Start: zufällige Reihenfolge (rng.shuffle). Schritt: ein gleichverteilter der n(n-3)/2 Züge, das heißt ein Paar 1 <= i < j <= n-1 ohne
    (1, n-1); die Positionen i … j werden umgedreht. Die Länge wird mit der Änderung aus vier Kanten fortgeschrieben."""
    n = len(d)
    if n < 5:
        raise ValueError("n mindestens 5")
    tour = list(range(n))
    rng.shuffle(tour)
    aktuell = 0.0
    for i in range(n):
        aktuell += d[tour[i]][tour[(i + 1) % n]]
    reihe = [aktuell]
    for _ in range(laenge - 1):
        # gleichverteiltes Paar per Verwerfen: i = j und das Paar (1, n-1) (dieselbe Tour, nur andersherum) werden neu gezogen
        while True:
            i = 1 + rng.below(n - 1)
            j = 1 + rng.below(n - 1)
            if i > j:
                i, j = j, i
            if i != j and not (i == 1 and j == n - 1):
                break
        a, b, c, e = tour[i - 1], tour[i], tour[j], tour[(j + 1) % n]
        aktuell += d[a][c] + d[b][e] - d[a][b] - d[c][e]
        tour[i:j + 1] = tour[i:j + 1][::-1]
        reihe.append(aktuell)
    return reihe
