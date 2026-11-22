"""Permalink (Begrenzen und Einrasten), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio)."""

import random
from dataclasses import dataclass

import streamlit as st

import lsm_constants as C


def _bool(text) -> bool:
    return str(text).strip().lower() in ("1", "true", "ja")


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: object
    default: object
    lo: float | None = None
    hi: float | None = None
    options: tuple | None = None    # feste Auswahl (select_slider, radio): ein Wert aus der Adresszeile rastet auf den nächsten ein


SETTING_SPECS = {
    "n_slider": SettingSpec("N", int, C.DEFAULT_N, C.N_MIN, C.N_MAX),
    "k_slider": SettingSpec("K", int, C.DEFAULT_K, C.K_MIN, C.K_MAX),
    "konv_toggle": SettingSpec("mitgen", _bool, False),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "l_select": SettingSpec("L", int, C.DEFAULT_L, options=C.L_OPTIONEN),
    "wseed_input": SettingSpec("wseed", int, C.DEFAULT_WSEED, 0, C.SEED_MAX),
    "inst_slider": SettingSpec("inst", int, C.DEFAULT_INST, C.INST_MIN, C.INST_MAX),
    "wand_slider": SettingSpec("wand", int, C.DEFAULT_WAND, C.WAND_MIN, C.WAND_MAX),
    "rn_slider": SettingSpec("rn", int, C.DEFAULT_RN, C.RN_MIN, C.RN_MAX),
    "nb_radio": SettingSpec("nb", str, C.NACHBARSCHAFTEN[0], options=C.NACHBARSCHAFTEN),
    "quad_toggle": SettingSpec("quadrat", _bool, False),
    "rinst_slider": SettingSpec("rinst", int, C.DEFAULT_RINST, C.RINST_MIN, C.RINST_MAX),
    "rseed_input": SettingSpec("rseed", int, C.DEFAULT_RSEED, 0, C.RSEED_MAX),
    "wn_select": SettingSpec("wn", int, C.DEFAULT_WN, options=C.WN_OPTIONEN),
}
PRESET_KEYS = {
    "n": "n_slider", "k": "k_slider", "mitgen": "konv_toggle", "seed": "seed_input", "L": "l_select", "wseed": "wseed_input", "inst": "inst_slider",
    "wand": "wand_slider", "rn": "rn_slider", "nb": "nb_radio", "quadrat": "quad_toggle", "rinst": "rinst_slider", "rseed": "rseed_input", "wn": "wn_select",
}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def einrasten(spec: SettingSpec, value):
    """Wert auf die Grenzen begrenzen bzw. auf die nächste erlaubte Auswahl setzen; unbekannte Texte geben den Standard."""
    if spec.options is not None:
        if value in spec.options:
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return min(spec.options, key=lambda o: (abs(o - value), o))
        return spec.default
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, begrenzt bzw. eingerastet."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = einrasten(spec, value)
    st.session_state["permalink_loaded"] = True


def klemme_k():
    """K ist höchstens N - 1 (jeder Beitrag hängt höchstens an allen anderen Genen)."""
    n = st.session_state.get("n_slider", C.DEFAULT_N)
    if st.session_state.get("k_slider", C.DEFAULT_K) > n - 1:
        st.session_state["k_slider"] = n - 1


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Ein Preset setzt ALLE Regler: die genannten auf seinen Wert, alle übrigen auf den Standard."""
    preset = C.PRESETS[name]
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for state_key, spec in SETTING_SPECS.items():
        st.session_state[state_key] = preset.get(preset_key_of[state_key], spec.default)


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden (setzt alle Regler):")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
