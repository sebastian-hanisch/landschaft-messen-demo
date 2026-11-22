"""Presets und Permalink: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Begrenzen und Einrasten."""

import lsm_constants as C
import lsm_presets as P


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_keys_cover_every_setting():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert len({spec.url_param for spec in P.SETTING_SPECS.values()}) == len(P.SETTING_SPECS)


def test_preset_values_are_valid_settings():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            spec = P.SETTING_SPECS[P.PRESET_KEYS[key]]
            assert P.einrasten(spec, value) == value, (name, key)
        n = preset.get("n", C.DEFAULT_N)
        assert preset.get("k", C.DEFAULT_K) <= n - 1, name          # K höchstens N - 1


def test_default_preset_is_empty_and_first():
    assert next(iter(C.PRESETS.values())) == {}
    assert sum(1 for p in C.PRESETS.values() if p == {}) == 1      # sonst wären zwei Presets gleichzeitig aktiv


def test_presets_unterscheiden_sich_paarweise():
    voll = []
    for preset in C.PRESETS.values():
        voll.append(tuple(preset.get(key, P.SETTING_SPECS[state].default) for key, state in P.PRESET_KEYS.items()))
    assert len(set(voll)) == len(voll)


def test_defaults_liegen_in_den_grenzen():
    for state_key, spec in P.SETTING_SPECS.items():
        assert P.einrasten(spec, spec.default) == spec.default, state_key
    assert C.DEFAULT_L in C.L_OPTIONEN and C.DEFAULT_WN in C.WN_OPTIONEN and C.K_MAX == C.N_MAX - 1


def test_einrasten_begrenzt_und_rastet_ein():
    assert P.einrasten(P.SETTING_SPECS["n_slider"], 99) == C.N_MAX and P.einrasten(P.SETTING_SPECS["n_slider"], -3) == C.N_MIN
    assert P.einrasten(P.SETTING_SPECS["l_select"], 130) == 100 and P.einrasten(P.SETTING_SPECS["l_select"], 99999) == 5000
    assert P.einrasten(P.SETTING_SPECS["l_select"], 150) == 100       # Gleichstand: der kleinere Wert
    assert P.einrasten(P.SETTING_SPECS["wn_select"], 60) == 50
    assert P.einrasten(P.SETTING_SPECS["nb_radio"], "3-opt") == "2-opt" and P.einrasten(P.SETTING_SPECS["nb_radio"], "Or-opt") == "Or-opt"


def test_bool_aus_der_adresszeile():
    assert P._bool("True") and P._bool("1") and P._bool("ja") and not P._bool("False") and not P._bool("0") and not P._bool("")
