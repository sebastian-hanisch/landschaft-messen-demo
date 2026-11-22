"""SplitMix64 in Blöcken: dieselben 64-Bit-Zahlen wie `lsm_rng.SplitMix64(seed).next_u64()`, aber mit numpy für viele Ziehungen auf einmal.

Der Zustand nach k Ziehungen ist seed + k * GAMMA (modulo 2^64), die k-te Zahl hängt also nur an Zufalls-Seed und Zähler. numpy rechnet
vorzeichenlose 64-Bit-Zahlen modulo 2^64, darum sind die Blöcke bitgleich zur skalaren Vorlage (tests/test_rng.py prüft das)."""

import numpy as np

MASK = (1 << 64) - 1
_GAMMA = np.uint64(0x9E3779B97F4A7C15)
_M1 = np.uint64(0xBF58476D1CE4E5B9)
_M2 = np.uint64(0x94D049BB133111EB)
_S30, _S27, _S31 = np.uint64(30), np.uint64(27), np.uint64(31)


def u64_block(seeds, count: int) -> np.ndarray:
    """Matrix (Zahl der Zufalls-Seeds, count): Zeile w enthält die ersten `count` Zahlen des Stroms mit dem Zufalls-Seed seeds[w]."""
    start = np.array([s & MASK for s in seeds], dtype=np.uint64).reshape(-1, 1)
    k = np.arange(1, count + 1, dtype=np.uint64).reshape(1, -1)
    z = k * _GAMMA + start
    z = (z ^ (z >> _S30)) * _M1
    z = (z ^ (z >> _S27)) * _M2
    return z ^ (z >> _S31)
