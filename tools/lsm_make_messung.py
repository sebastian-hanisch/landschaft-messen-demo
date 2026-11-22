"""Erzeugt `lsm_messung.json`: die eingefrorene Messung, aus der README und App ihre Zahlen nehmen.

Aufruf (im Demo-Ordner):  python tools/lsm_make_messung.py            schreibt die Datei (einige Minuten)
                          python tools/lsm_make_messung.py --check    rechnet alles neu und vergleicht (Gleitkomma relativ 1e-9)
                          python tools/lsm_make_messung.py --teil nk_exakt   nur einen Teil neu rechnen (nk_exakt, nk_schaetzer, route_exakt, route_wanderung)

Jeder Teil läuft mit zwei getrennten Sätzen von Instanzen und Zufalls-Seeds („A“ ab laufender Nummer 0, „B“ ab 1000); README und App nennen
beide als Band. Zähleinheiten: Instanz (Landschaft oder Abstandsmatrix), Schätzung (eine Wanderung), Auswertung (ein Wert der Zielfunktion)."""

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

import lsm_evaluation as ev  # noqa: E402
import lsm_route as R  # noqa: E402

STAND = "2026-11-21"
REIHEN = {"A": 0, "B": 1000}
N = 16
K_EXAKT = (0, 1, 2, 4, 8, 15)
K_SCHAETZER = (0, 1, 2, 4, 8, 15)
INSTANZEN, WANDERUNGEN = 30, 30
ROUTE_JE_FAMILIE = 30
ROUTE_LANG = ((9, "gleich", 20000), (30, "gleich", 100000), (30, "cluster", 100000), (100, "gleich", 200000))
ROUTE_LANG_WANDERUNGEN = 10
ROUTE_GUETE_N = (30, 100)
ROUTE_GUETE_INSTANZEN, ROUTE_GUETE_WANDERUNGEN = 20, 10
TEILE = ("nk_exakt", "nk_schaetzer", "route_exakt", "route_wanderung")


def nk_exakt() -> dict:
    reihen = {}
    for name, start in REIHEN.items():
        zeilen = []
        for k in K_EXAKT:
            f = ev.formeln(N, k, start, INSTANZEN, smax=5, mit_optima=True)
            rho = [r for r in f["rho"] if r is not None]
            diff5 = [r[4] - r[0] ** 5 for r in rho]
            diff2 = [r[1] - r[0] ** 2 for r in rho]
            zeilen.append({
                "k": k, "familie": f["familie"], "endlich": f["endlich"], "mittel": f["mittel"], "sd": f["sd"], "se": f["se"],
                "min": min(f["werte"]), "max": max(f["werte"]),
                "diff2_mittel": float(np.mean(diff2)), "diff5_mittel": float(np.mean(diff5)), "diff5_min": min(diff5), "diff5_max": max(diff5),
                "diff5_positiv": int(sum(d > 1e-12 for d in diff5)),
                "optima_mittel": float(np.mean(f["optima"])), "optima_sd": ev.sd(f["optima"]), "optima_min": min(f["optima"]), "optima_max": max(f["optima"]),
            })
        reihen[name] = zeilen
    return {
        "quelle": "tools/lsm_make_messung.py, Teil nk_exakt: Aufzählung aller 2^16 Zustände je Landschaft", "stand": STAND,
        "n": N, "instanzen": INSTANZEN, "reihen": reihen,
    }


def nk_schaetzer() -> dict:
    reihen = {}
    for name, start in REIHEN.items():
        zeilen = []
        for k in K_SCHAETZER:
            s = ev.schaetzung(N, k, start, INSTANZEN, WANDERUNGEN)
            for z in s["zeilen"]:
                zeilen.append({"k": k, "sd_zwischen": s["sd_zwischen"], **z})
        reihen[name] = zeilen
    return {
        "quelle": "tools/lsm_make_messung.py, Teil nk_schaetzer: Zufallswanderungen gegen den exakten Wert derselben Landschaft", "stand": STAND,
        "n": N, "instanzen": INSTANZEN, "wanderungen": WANDERUNGEN, "reihen": reihen,
    }


def route_exakt() -> dict:
    reihen, quadrat = {}, {}
    for name, start in REIHEN.items():
        zeilen = []
        for n in range(5, 10):
            for nb in R.NACHBARSCHAFTEN:
                r = ev.route_exakt(n, nb, ROUTE_JE_FAMILIE, start)
                zeilen.append({k: r[k] for k in ("n", "nachbarschaft", "touren", "nachbarn", "instanzen", "familien", "rho1", "rho2", "spanne1", "spanne2")})
        reihen[name] = zeilen
        q = ev.route_exakt(8, "2-opt", ROUTE_JE_FAMILIE, start, quadrat=True)
        quadrat[name] = {k: q[k] for k in ("n", "nachbarschaft", "instanzen", "min1", "max1", "spanne1")}
    return {
        "quelle": "tools/lsm_make_messung.py, Teil route_exakt: Aufzählung aller (n-1)!/2 Touren je Instanz, fünf Familien", "stand": STAND,
        "je_familie": ROUTE_JE_FAMILIE, "reihen": reihen, "gegenprobe_quadrat": quadrat,
    }


def route_wanderung() -> dict:
    lang, guete = {}, {}
    for name, start in REIHEN.items():
        zeilen = []
        for n, familie, laenge in ROUTE_LANG:
            w = ev.route_wanderung(n, familie, start, ROUTE_LANG_WANDERUNGEN, laenge)
            zeilen.append({k: w[k] for k in ("n", "familie", "L", "wanderungen", "mittel", "se", "exakt")})
        lang[name] = zeilen
        zeilen = []
        for n in ROUTE_GUETE_N:
            for z in ev.route_guete(n, start, ROUTE_GUETE_INSTANZEN, ROUTE_GUETE_WANDERUNGEN):
                zeilen.append({"n": n, **z})
        guete[name] = zeilen
    return {
        "quelle": "tools/lsm_make_messung.py, Teil route_wanderung: 2-opt-Zufallswanderungen gegen den Wert der Formel", "stand": STAND,
        "lang_wanderungen": ROUTE_LANG_WANDERUNGEN, "guete_instanzen": ROUTE_GUETE_INSTANZEN, "guete_wanderungen": ROUTE_GUETE_WANDERUNGEN,
        "lang": lang, "guete": guete,
    }


def gleich(a, b, pfad="") -> list:
    """Rekursiver Vergleich: Gleitkomma relativ 1e-9 (absolut 1e-12), alles andere exakt. Rückgabe: Liste der Abweichungen."""
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [f"{pfad}: Schlüssel verschieden"]
        return [x for k in a for x in gleich(a[k], b[k], f"{pfad}/{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{pfad}: Länge verschieden"]
        return [x for i, (p, q) in enumerate(zip(a, b)) for x in gleich(p, q, f"{pfad}[{i}]")]
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None or not math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12):
            return [f"{pfad}: {a} gegen {b}"]
        return []
    return [] if a == b else [f"{pfad}: {a} gegen {b}"]


def main(argv) -> int:
    ziel = ROOT / "lsm_messung.json"
    teile = TEILE
    if "--teil" in argv:
        teile = (argv[argv.index("--teil") + 1],)
    alt = json.loads(ziel.read_text(encoding="utf-8")) if ziel.exists() else {}
    neu = dict(alt)
    neu["hinweis"] = ("Eingefrorene Messung der Demo landschaft-messen-demo. Alle Instanzen sind erfunden (SplitMix64). "
                      "Reihen A und B: getrennte Instanzen und Zufalls-Seeds (laufende Nummern ab 0 bzw. ab 1000).")
    neu["skript"] = "tools/lsm_make_messung.py"
    for teil in teile:
        t0 = time.time()
        neu[teil] = globals()[teil]()
        print(f"{teil}: {time.time() - t0:.1f} s", flush=True)
    if "--check" in argv:
        fehler = [x for teil in teile for x in gleich(alt.get(teil), neu[teil], teil)]
        for x in fehler[:20]:
            print("ABWEICHUNG", x)
        print(f"GESAMT: {len(teile)} Teile geprüft, {len(fehler)} Abweichungen")
        return 1 if fehler else 0
    ziel.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("geschrieben:", ziel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
