"""Der blockweise Generator liefert bitgleich die Zahlen der skalaren Vorlage; die Wanderung nutzt genau diese Zahlen."""

import pytest

import lsm_rng as G
import lsm_rngblock as RB
import lsm_walk as W


@pytest.mark.parametrize("seed", [0, 1, 12345, 2 ** 63 + 5, 2 ** 64 - 1])
def test_block_gleich_skalar(seed):
    rng = G.SplitMix64(seed)
    assert RB.u64_block([seed], 200)[0].tolist() == [rng.next_u64() for _ in range(200)]


def test_mehrere_seeds_geben_mehrere_zeilen():
    block = RB.u64_block([3, 4], 5)
    assert block.shape == (2, 5)
    for zeile, seed in zip(block.tolist(), (3, 4)):
        rng = G.SplitMix64(seed)
        assert zeile == [rng.next_u64() for _ in range(5)]


def test_bekannter_wert_von_splitmix64():
    # Referenzwert des Verfahrens für den Zufalls-Seed 0 (erste Ausgabe), unabhängig von beiden Umsetzungen
    assert G.SplitMix64(0).next_u64() == 0xE220A8397B1DCDAF
    assert int(RB.u64_block([0], 1)[0, 0]) == 0xE220A8397B1DCDAF


def test_wanderung_folgt_dem_skalaren_strom():
    n, laenge, seed = 6, 50, 77
    rng = G.SplitMix64(seed)
    zustand = rng.below(1 << n)
    erwartet = [zustand]
    for _ in range(laenge - 1):
        zustand ^= 1 << rng.below(n)
        erwartet.append(zustand)
    assert W.nk_wanderungen(n, laenge, [seed])[0].tolist() == erwartet
