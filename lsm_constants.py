"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# NK-Modell
N_MIN, N_MAX, DEFAULT_N = 4, 16, 16
K_MIN, K_MAX, DEFAULT_K = 0, N_MAX - 1, 4
SEED_MAX, DEFAULT_SEED = 999999, 1          # laufende Nummer der Landschaft (Zufalls-Seed der Tabellen: lsm_nk.nk_seed)
L_OPTIONEN = (50, 100, 200, 500, 1000, 2000, 5000)
DEFAULT_L = 1000
DEFAULT_WSEED = 1
S_MAX = 10                                   # Schrittabstände 1 … S_MAX im Diagramm der Autokorrelation
INST_MIN, INST_MAX, DEFAULT_INST = 10, 50, 30
WAND_MIN, WAND_MAX, DEFAULT_WAND = 5, 30, 10
L_GUETE = (100, 1000, 10000)                 # Längen in Experiment 3

# Rundtour
RN_MIN, RN_MAX, DEFAULT_RN = 5, 9, 7         # aufgezählt
NACHBARSCHAFTEN = ("2-opt", "Or-opt")
RINST_MIN, RINST_MAX, DEFAULT_RINST = 5, 30, 10
RSEED_MAX, DEFAULT_RSEED = 999, 0
WN_OPTIONEN = (20, 30, 50, 100, 200)         # per Wanderung
DEFAULT_WN = 30
ROUTE_L = 20000                              # Auswertungen je Wanderung in Experiment 4
ROUTE_WANDERUNGEN = 5
ROUTE_FAMILIE = "gleich"

# Verfahrensnummern für lsm_basis.lauf_seed (getrennte Zufallsströme je Zweck)
VERFAHREN_PROFIL = 0
VERFAHREN_GUETE = 1                          # 1, 2, 3: je Länge in L_GUETE
VERFAHREN_ROUTE = 10                         # 10: lange Wanderung; 11, 12, 13: Güte je Länge

# Schwellen der Verdikte
SCHWELLE_GLATT = 0.5
SCHWELLE_RAU = 0.1
FEHLER_GROB = 0.1                            # „um mehr als 0,1 daneben“
Z_GRENZE = 3.0                               # Standardfehler, ab denen Experiment 2 eine Formel als unterscheidbar meldet
Z_BAND = 4.0                                 # Band der Wanderung gegen die Formel in Experiment 4
NULL_SPANNE = 1e-9                           # Spanne, unter der Werte als gleich gelten (Rundungsfehler)

COLOR_LINE = "#2F6B65"
COLOR_SECOND = "#4c78a8"
COLOR_THIRD = "#d98a2b"
COLOR_GREY = "rgba(120,120,120,0.75)"
FAMILIEN_FARBEN = {"gleich": "#2F6B65", "cluster": "#4c78a8", "gitter": "#d98a2b", "netz": "#8e5ea2", "zufall": "#c44e52"}

PRESETS = {
    "NK, K = 4 (Voreinstellung)": {},
    "Von Hand: K = 0, N = 4": {"n": 4, "k": 0},
    "NK, K = 0": {"k": 0},
    "NK, K = 15": {"k": 15},
    "Wanderung L = 100": {"L": 100},
    "Rundtour n = 8": {"rn": 8},
    "Rundtour n = 100": {"wn": 100},
}
PRESET_HELP = {
    "NK, K = 4 (Voreinstellung)": "NK-Landschaft mit 16 Genen, jeder Beitrag hängt an 4 weiteren Genen; Wanderung mit 1000 Auswertungen.",
    "Von Hand: K = 0, N = 4": "Das Handbeispiel: 16 Zustände, jeder Beitrag hängt nur am eigenen Gen. Exakt ist ρ(1) = 1/2, der Familienwert wäre 3/4.",
    "NK, K = 0": "16 Gene ohne Wechselwirkung: jede Landschaft hat exakt ρ(1) = 0,875 und genau ein lokales Optimum.",
    "NK, K = 15": "Jeder Beitrag hängt an allen 16 Genen: benachbarte Zustände haben unabhängige Werte, ρ(1) liegt bei null.",
    "Wanderung L = 100": "Eine kurze Wanderung mit 100 Auswertungen: der Schätzwert kann deutlich neben dem exakten Wert liegen.",
    "Rundtour n = 8": "Experiment 4 mit 8 Städten: 2520 Touren aufgezählt, ρ(1) je Instanz.",
    "Rundtour n = 100": "Experiment 4 mit 100 Städten per Wanderung (nicht aufgezählt) gegen den Wert der Formel.",
}
