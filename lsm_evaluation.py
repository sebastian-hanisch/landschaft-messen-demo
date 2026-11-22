"""Auswertungen der vier Experimente und alle Verdikte als reine Funktionen (Art, Text).

Zähleinheiten: „Instanz“ (eine Landschaft oder eine Abstandsmatrix), „Schätzung“ (eine Wanderung), „Auswertung“ (ein Wert der Zielfunktion).
Die Rechenfunktionen werden von der App und von `tools/lsm_make_messung.py` gleichermaßen benutzt."""

import json
import math
from pathlib import Path

import numpy as np

import lsm_basis as B
import lsm_constants as C
import lsm_nk as NK
import lsm_rng as G
import lsm_route as R
import lsm_scenario as S
import lsm_walk as W

MESSUNG_PFAD = Path(__file__).resolve().parent / "lsm_messung.json"


def de(x: float, stellen: int = 3) -> str:
    """Zahl mit Dezimalkomma und echtem Minuszeichen (−). Ein Ergebnis, das zu null rundet, bekommt kein Minuszeichen."""
    text = f"{x:.{stellen}f}"
    if float(text) == 0.0:
        text = text.lstrip("-")
    return text.replace(".", ",").replace("-", "−")


def de_exp(x: float) -> str:
    """Sehr kleine Zahl als Zehnerpotenz mit Dezimalkomma, zum Beispiel 3,1e−16; die Null bleibt 0."""
    if x == 0:
        return "0"
    mantisse, exponent = f"{abs(x):.1e}".split("e")
    return f"{'−' if x < 0 else ''}{mantisse.replace('.', ',')}e{'−' if int(exponent) < 0 else ''}{abs(int(exponent))}"


def sd(werte) -> float:
    """Standardabweichung mit Nenner n - 1; bei weniger als zwei Werten 0."""
    w = np.asarray(werte, dtype=float)
    return float(w.std(ddof=1)) if len(w) > 1 else 0.0


# --------------------------------------------------------------------------------------------------------------------- NK: eine Landschaft


def landschaft(n: int, k: int, idx: int, smax: int = C.S_MAX) -> dict:
    """Eine Landschaft vollständig: Fitness aller Zustände, exakte Autokorrelation bis smax, Zahl der lokalen Optima."""
    f = NK.fitness_alle(NK.tabellen(n, k, NK.nk_seed(n, k, idx)))
    return {"f": f, "rho": NK.rho_exakt(f, n, smax), "optima": NK.zahl_optima(f, n)}


def profil(f: np.ndarray, n: int, idx: int, laenge: int, wseed: int) -> dict:
    """Eine Wanderung der Länge `laenge` auf der Landschaft f: Reihe der Fitnesswerte und Schätzer für s = 1 … S_MAX (None, wo nicht definiert)."""
    zustaende = W.nk_wanderungen(n, laenge, [B.lauf_seed(idx, C.VERFAHREN_PROFIL, wseed)])[0]
    reihe = f[zustaende]
    dach = [W.rho_dach(reihe, s) if laenge > s else None for s in range(1, C.S_MAX + 1)]
    return {"reihe": reihe, "dach": dach}


# --------------------------------------------------------------------------------------------------------------------- NK: zwei Formeln


def formeln(n: int, k: int, start: int, instanzen: int, smax: int = 1, mit_optima: bool = False) -> dict:
    """Exaktes rho(1) (bis smax) je Instanz für `instanzen` Landschaften ab der laufenden Nummer `start`."""
    rho, optima = [], []
    for i in range(instanzen):
        f = NK.fitness_alle(NK.tabellen(n, k, NK.nk_seed(n, k, start + i)))
        rho.append(NK.rho_exakt(f, n, smax))
        if mit_optima:
            optima.append(NK.zahl_optima(f, n))
    werte = [r[0] for r in rho if r is not None]
    return {
        "rho": rho, "werte": werte, "optima": optima,
        "familie": NK.familienwert(n, k), "endlich": NK.einzelwert_erwartung(n, k),
        "mittel": float(np.mean(werte)) if werte else None, "sd": sd(werte),
        "se": sd(werte) / math.sqrt(len(werte)) if werte else None,
    }


# --------------------------------------------------------------------------------------------------------------------- NK: Güte der Schätzung


def _guete_zeile(laenge: int, schaetzungen: np.ndarray, exakt: np.ndarray) -> dict:
    """Kennzahlen einer Zelle: `schaetzungen` ist die Matrix (Instanzen × Wanderungen), `exakt` der exakte Wert je Instanz."""
    fehler = schaetzungen - exakt[:, None]
    innen = np.nanvar(schaetzungen, axis=1, ddof=1) if schaetzungen.shape[1] > 1 else np.zeros(len(exakt))
    with np.errstate(divide="ignore", invalid="ignore"):
        gueltig = (schaetzungen > 0) & (schaetzungen < 1) & ((exakt > 0) & (exakt < 1))[:, None]
        verhaeltnis = np.where(gueltig, np.log(np.where(exakt > 0, exakt, 0.5))[:, None] / np.log(np.where(gueltig, schaetzungen, 0.5)), np.nan)
    tau = verhaeltnis[gueltig]
    return {
        "L": laenge,
        "bias": float(np.nanmean(fehler)),
        "sd_innen": float(np.sqrt(np.mean(innen))),
        "anteil_01": float(np.mean(np.abs(fehler) > 0.1)),
        "anteil_ueber_005": float(np.mean(schaetzungen > 0.05)),
        "tau_gueltig": float(np.mean(gueltig)),
        "tau_median": float(np.median(tau)) if tau.size else None,
        "tau_q05": float(np.quantile(tau, 0.05)) if tau.size else None,
        "tau_q95": float(np.quantile(tau, 0.95)) if tau.size else None,
        "sd_instanzmittel": sd(np.nanmean(fehler, axis=1)),
    }


def schaetzung(n: int, k: int, start: int, instanzen: int, wanderungen: int, laengen=C.L_GUETE, mit_werten: bool = False) -> dict:
    """Je Länge L: `instanzen` × `wanderungen` Schätzungen von rho(1) gegen den exakten Wert der jeweiligen Landschaft."""
    exakt, je_l = [], {laenge: [] for laenge in laengen}
    for i in range(instanzen):
        f = NK.fitness_alle(NK.tabellen(n, k, NK.nk_seed(n, k, start + i)))
        r = NK.rho_exakt(f, n, 1)
        if r is None:
            continue
        exakt.append(r[0])
        for li, laenge in enumerate(laengen):
            seeds = [B.lauf_seed(start + i, C.VERFAHREN_GUETE + li, w) for w in range(wanderungen)]
            je_l[laenge].append(W.rho_dach_zeilen(f[W.nk_wanderungen(n, laenge, seeds)]))
    ex = np.array(exakt)
    zeilen = []
    for laenge in laengen:
        m = np.array(je_l[laenge])
        zeile = _guete_zeile(laenge, m, ex)
        if mit_werten:
            zeile["fehler"] = (m - ex[:, None]).reshape(-1)
        zeilen.append(zeile)
    return {"zeilen": zeilen, "sd_zwischen": sd(exakt), "instanzen": len(exakt), "wanderungen": wanderungen, "exakt_mittel": float(ex.mean()) if len(ex) else None}


# --------------------------------------------------------------------------------------------------------------------- Rundtour


def route_exakt(n: int, nachbarschaft: str, je_familie: int, start: int, quadrat: bool = False, familien=S.FAMILIEN) -> dict:
    """Exaktes rho(1) und rho(2) je Instanz über alle Touren. `quadrat`: Gegenprobe mit dem Quadrat der Tourlänge als Landschaft."""
    touren = R.alle_touren(n)
    tabelle = R.nachbar_tabelle(n, nachbarschaft)
    zeilen = []
    for familie in familien:
        for i in range(je_familie):
            werte = R.tourlaengen(S.route_abstaende(familie, n, start + i), touren)
            if quadrat:
                werte = werte * werte
            r = R.rho_exakt(werte, tabelle, 2)
            if r is not None:
                zeilen.append({"familie": familie, "idx": start + i, "rho1": r[0], "rho2": r[1]})
    r1 = [z["rho1"] for z in zeilen]
    r2 = [z["rho2"] for z in zeilen]
    return {
        "n": n, "nachbarschaft": nachbarschaft, "quadrat": quadrat, "touren": int(len(touren)), "nachbarn": int(tabelle.shape[1]), "zeilen": zeilen,
        "instanzen": len(zeilen), "familien": len(familien),
        "rho1": float(np.mean(r1)), "rho2": float(np.mean(r2)), "min1": min(r1), "max1": max(r1),
        "spanne1": max(r1) - min(r1), "spanne2": max(r2) - min(r2),
    }


def route_wanderungen(n: int, familie: str, idx: int, wanderungen: int, laenge: int) -> list:
    """`wanderungen` Schätzungen von rho(1) aus 2-opt-Wanderungen der Länge `laenge` auf einer Instanz."""
    d = S.route_abstaende(familie, n, idx)
    return [W.rho_dach(W.route_wanderung_2opt(d, laenge, G.SplitMix64(B.lauf_seed(idx, C.VERFAHREN_ROUTE, w)))) for w in range(wanderungen)]


def route_wanderung(n: int, familie: str, idx: int, wanderungen: int = C.ROUTE_WANDERUNGEN, laenge: int = C.ROUTE_L) -> dict:
    werte = [w for w in route_wanderungen(n, familie, idx, wanderungen, laenge) if w is not None]
    exakt = R.formel_2opt(n)
    mittel = float(np.mean(werte))
    return {
        "n": n, "familie": familie, "L": laenge, "wanderungen": len(werte), "werte": werte, "mittel": mittel,
        "se": sd(werte) / math.sqrt(len(werte)), "exakt": exakt, "tau": NK.tau(exakt), "tau_dach": NK.tau(mittel),
    }


def route_guete(n: int, start: int, instanzen: int, wanderungen: int, laengen=C.L_GUETE, familie: str = "gleich") -> list:
    """Güte des Schätzers auf der Rundtour (2-opt): je Länge Bias, Streuung und tau-Verhältnis gegen den Wert der Formel."""
    exakt = np.full(instanzen, R.formel_2opt(n))
    zeilen = []
    for li, laenge in enumerate(laengen):
        m = np.empty((instanzen, wanderungen))
        for i in range(instanzen):
            d = S.route_abstaende(familie, n, start + i)
            for w in range(wanderungen):
                m[i, w] = W.rho_dach(W.route_wanderung_2opt(d, laenge, G.SplitMix64(B.lauf_seed(start + i, C.VERFAHREN_ROUTE + 1 + li, w))))
        zeilen.append(_guete_zeile(laenge, m, exakt))
    return zeilen


# --------------------------------------------------------------------------------------------------------------------- eingefrorene Messung


def lade_messung() -> dict:
    return json.loads(MESSUNG_PFAD.read_text(encoding="utf-8"))


def band(a: float, b: float, stellen: int = 3) -> str:
    """Zwei Messreihen als Band „kleiner bis größer“; gleiche gerundete Werte nur einmal."""
    lo, hi = de(min(a, b), stellen), de(max(a, b), stellen)
    return lo if lo == hi else f"{lo} bis {hi}"


TAU_OHNE_SINN = "nicht sinnvoll (ρ(1) nahe 0)"


def tau_sinnvoll(z: dict) -> bool:
    """Das Verhältnis der Korrelationslängen ist nur sinnvoll, wenn es für mindestens die Hälfte der Schätzungen definiert ist (0 < Wert < 1, exakt und geschätzt)."""
    return z["tau_median"] is not None and z["tau_gueltig"] >= 0.5


def tau_text(z: dict) -> str:
    return de(z["tau_median"], 2) if tau_sinnvoll(z) else TAU_OHNE_SINN


def tabelle_nk_exakt(m: dict) -> str:
    """Markdown-Tabelle der eingefrorenen exakten Werte (zwei Messreihen A und B als Band)."""
    kopf = "| K | Familienwert | Endlichkeitskorrektur | Mittel exakt | SD zwischen Instanzen | ρ(5) − ρ(1)⁵ | lokale Optima (Mittel) |\n|---|---|---|---|---|---|---|\n"
    zeilen = []
    for a, b in zip(m["nk_exakt"]["reihen"]["A"], m["nk_exakt"]["reihen"]["B"]):
        zeilen.append(
            f"| {a['k']} | {de(a['familie'], 4)} | {de(a['endlich'], 4)} | {band(a['mittel'], b['mittel'], 4)} | {band(a['sd'], b['sd'], 4)} | "
            f"{band(a['diff5_mittel'], b['diff5_mittel'], 4)} | {band(a['optima_mittel'], b['optima_mittel'], 1)} |"
        )
    return kopf + "\n".join(zeilen)


def tabelle_nk_schaetzer(m: dict) -> str:
    kopf = "| K | L | Bias | SD innerhalb einer Instanz | Anteil mit Fehler über 0,1 | Median τ̂/τ |\n|---|---|---|---|---|---|\n"
    zeilen = []
    for a, b in zip(m["nk_schaetzer"]["reihen"]["A"], m["nk_schaetzer"]["reihen"]["B"]):
        tau = band(a["tau_median"], b["tau_median"], 2) if tau_sinnvoll(a) and tau_sinnvoll(b) else TAU_OHNE_SINN
        zeilen.append(
            f"| {a['k']} | {a['L']} | {band(a['bias'], b['bias'], 4)} | {band(a['sd_innen'], b['sd_innen'], 4)} | "
            f"{band(100 * a['anteil_01'], 100 * b['anteil_01'], 1)} % | {tau} |"
        )
    return kopf + "\n".join(zeilen)


def tabelle_route_exakt(m: dict) -> str:
    kopf = "| n | Nachbarschaft | Touren | Nachbarn je Tour | ρ(1) | ρ(2) | ρ(1)² | größte Spanne von ρ(1) |\n|---|---|---|---|---|---|---|---|\n"
    zeilen = []
    for a, b in zip(m["route_exakt"]["reihen"]["A"], m["route_exakt"]["reihen"]["B"]):
        zeilen.append(
            f"| {a['n']} | {a['nachbarschaft']} | {a['touren']} | {a['nachbarn']} | {de(a['rho1'], 6)} | {de(a['rho2'], 6)} | {de(a['rho1'] ** 2, 6)} | "
            f"{de_exp(max(a['spanne1'], b['spanne1']))} |"
        )
    return kopf + "\n".join(zeilen)


# --------------------------------------------------------------------------------------------------------------------- Verdikte


def glaette_wort(rho: float) -> str:
    """Einordnung nach festen Schwellen: ab 0,5 „glatt“, unter 0,1 (im Betrag) „rau“, dazwischen „mittel“."""
    if rho >= C.SCHWELLE_GLATT:
        return "glatt"
    if abs(rho) < C.SCHWELLE_RAU:
        return "rau"
    return "mittel"


def verdict_profil(n: int, k: int, rho1, dach1, laenge: int, optima: int) -> tuple[str, str]:
    """Experiment 1 und Kernfrage 1: was die Autokorrelation an dieser Landschaft misst."""
    if rho1 is None:
        return "warning", "Diese Landschaft ist konstant: jede Wanderung zeigt denselben Wert, die Autokorrelation ist nicht definiert."
    wort = glaette_wort(rho1)
    deutung = {
        "glatt": f"benachbarte Zustände haben ähnliche Werte (ab {de(C.SCHWELLE_GLATT, 1)} nennt die Demo das **glatt**)",
        "rau": f"der Wert eines Nachbarn sagt fast nichts über den eigenen (unter {de(C.SCHWELLE_RAU, 1)} nennt die Demo das **rau**)",
        "mittel": "die Landschaft liegt zwischen glatt und rau",
    }[wort]
    schaetz = "Die Wanderung ist konstant, ihr Schätzwert ist nicht definiert." if dach1 is None else (
        f"Die eine Wanderung mit {laenge} Auswertungen schätzt {de(dach1)}.")
    return "info", (
        f"N = {n}, K = {k}: exakt ist ρ(1) = **{de(rho1)}**, {deutung}. {schaetz} "
        + (f"Von den {2 ** n} Zuständen ist **1** ein lokales Optimum (kein Nachbar ist besser)." if optima == 1 else
           f"Von den {2 ** n} Zuständen sind **{optima}** lokale Optima (kein Nachbar ist besser).")
    )


def verdict_einzel(n: int, k: int, rho1, familie: float, endlich: float) -> tuple[str, str]:
    """Kernfrage 2: die zwei Formeln an der einen Landschaft der Seitenleiste."""
    if rho1 is None:
        return "warning", "Für eine konstante Landschaft ist keine der beiden Formeln anwendbar."
    text = (f"Familienwert 1 − (K+1)/N = {de(familie, 4)}, Formel für die einzelne Landschaft {de(endlich, 4)}, diese Landschaft exakt **{de(rho1, 4)}**: "
            f"Abstand zum Familienwert {de(abs(rho1 - familie), 4)}, zur Formel für die einzelne Landschaft {de(abs(rho1 - endlich), 4)}.")
    if k == 0:
        return "success", text + f" Bei K = 0 hat jede nichtkonstante Landschaft exakt 1 − 2/N = {de(1 - 2 / n, 4)}; der Familienwert liegt um 1/N = {de(1 / n, 4)} darüber."
    return "info", text + " Bei K ≥ 1 streut die einzelne Landschaft um ihre Formel; Experiment 2 zeigt viele Instanzen."


def verdict_fehler(rho1, dach1, laenge: int) -> tuple[str, str]:
    """Kernfrage 3: der Fehler der einen Wanderung."""
    if rho1 is None or dach1 is None:
        return "warning", "Für eine konstante Reihe ist der Schätzer nicht definiert."
    fehler = dach1 - rho1
    text = f"Die Wanderung mit L = {laenge} schätzt {de(dach1)} statt {de(rho1)}: Fehler **{de(fehler)}**."
    if abs(fehler) > C.FEHLER_GROB:
        return "warning", text + f" Das ist mehr als {de(C.FEHLER_GROB, 1)}; Experiment 3 zählt, wie oft das bei dieser Länge vorkommt."
    return "info", text + " Eine einzelne Wanderung sagt nicht, wie stark die Schätzung streut; das misst Experiment 3."


def verdict_formeln(n: int, k: int, f: dict) -> tuple[str, str]:
    """Experiment 2: Familienwert gegen die exakten Werte vieler Instanzen. `f` ist das Ergebnis von `formeln`."""
    werte = f["werte"]
    if not werte:
        return "warning", "Keine der Landschaften ist nichtkonstant; es gibt nichts zu vergleichen."
    anzahl = len(werte)
    if k == 0:
        abw = max(abs(w - (1 - 2 / n)) for w in werte)
        return "success", (
            f"N = {n}, K = 0: jede der {anzahl} Landschaften hat ρ(1) = 1 − 2/N = **{de(1 - 2 / n, 4)}** (größte Abweichung {de_exp(abw)}). "
            f"Der Familienwert {de(f['familie'], 4)} liegt um {de(f['familie'] - (1 - 2 / n), 4)} darüber: er gilt für das Mittel über die Familie, nicht für die einzelne Landschaft."
        )
    if anzahl < 2 or f["se"] == 0:
        return "info", f"N = {n}, K = {k}: eine Landschaft mit ρ(1) = {de(werte[0], 4)}; für einen Vergleich mit dem Familienwert {de(f['familie'], 4)} braucht es mehrere."
    z_fam = (f["mittel"] - f["familie"]) / f["se"]
    z_end = (f["mittel"] - f["endlich"]) / f["se"]
    kopf = (f"N = {n}, K = {k}, {anzahl} Landschaften: Mittel der exakten Werte **{de(f['mittel'], 4)}** (Standardfehler {de(f['se'], 4)}, Streuung zwischen den Instanzen {de(f['sd'], 4)}). "
            f"Familienwert {de(f['familie'], 4)}: {de(abs(z_fam), 1)} Standardfehler entfernt; Formel für die einzelne Landschaft {de(f['endlich'], 4)}: {de(abs(z_end), 1)} Standardfehler entfernt.")
    if abs(z_fam) > C.Z_GRENZE >= abs(z_end):
        return "success", kopf + f" In dieser Stichprobe ist der Familienwert damit unterscheidbar (über {de(C.Z_GRENZE, 0)} Standardfehler), die Formel für die einzelne Landschaft nicht."
    if abs(z_fam) <= C.Z_GRENZE:
        return "info", kopf + f" In dieser Stichprobe ist der Familienwert vom Mittel nicht zu unterscheiden (höchstens {de(C.Z_GRENZE, 0)} Standardfehler); der Unterschied der Formeln ist hier kleiner als das Rauschen."
    return "warning", kopf + f" Beide Formeln liegen über {de(C.Z_GRENZE, 0)} Standardfehler vom Mittel dieser Stichprobe entfernt."


def verdict_schaetzung(n: int, k: int, s: dict) -> tuple[str, str]:
    """Experiment 3: Verzerrung und Streuung des Schätzers gegen die Streuung zwischen Instanzen. `s` ist das Ergebnis von `schaetzung`."""
    zeilen = {z["L"]: z for z in s["zeilen"]}
    kurz, mittel = zeilen[C.L_GUETE[0]], zeilen[C.L_GUETE[1]]
    kopf = (f"N = {n}, K = {k}, {s['instanzen']} Instanzen × {s['wanderungen']} Wanderungen: bei L = {kurz['L']} ist die Schätzung im Mittel um {de(kurz['bias'])} verschoben, "
            f"{de(100 * kurz['anteil_01'], 0)} % der Schätzungen liegen um mehr als 0,1 daneben; bei L = {mittel['L']} beträgt die Verschiebung {de(mittel['bias'], 4)}, "
            f"die Streuung innerhalb einer Instanz {de(mittel['sd_innen'], 4)}.")
    zw = s["sd_zwischen"]
    if zw < C.NULL_SPANNE:
        return "info", kopf + f" Zwischen den Instanzen gibt es hier keinen Unterschied (alle haben denselben exakten Wert); jede Abweichung zweier Schätzungen ist Schätzrauschen."
    if mittel["sd_innen"] > zw:
        return "warning", kopf + (f" Die Schätzung streut damit stärker, als sich die {s['instanzen']} Instanzen unterscheiden ({de(mittel['sd_innen'], 4)} gegen {de(zw, 4)}): "
                                  f"zwei Instanzen gleichen K sind mit einer Wanderung der Länge {mittel['L']} nicht zuverlässig zu unterscheiden (Verhältnis {de(mittel['sd_innen'] / zw, 1)}; je näher an 1, desto knapper).")
    return "info", kopf + (f" In dieser Stichprobe unterscheiden sich die {s['instanzen']} Instanzen stärker, als die Schätzung streut ({de(zw, 4)} gegen {de(mittel['sd_innen'], 4)}).")


def verdict_route(r: dict) -> tuple[str, str]:
    """Experiment 4, aufgezählt: ist rho(1) in allen Instanzen gleich? `r` ist das Ergebnis von `route_exakt`."""
    n, nb = r["n"], r["nachbarschaft"]
    wo = f"n = {n}, {nb}, {r['instanzen']} Instanzen aus {r['familien']} Familien, alle {r['touren']} Touren aufgezählt"
    gleich = r["spanne1"] < C.NULL_SPANNE
    if r["quadrat"]:
        if gleich:
            return "info", f"Gegenprobe ({wo}): auch mit dem Quadrat der Tourlänge ist ρ(1) in allen Instanzen gleich ({de(r['rho1'], 4)})."
        return "info", (f"Gegenprobe ({wo}): mit dem **Quadrat der Tourlänge** als Landschaft unterscheiden sich die Instanzen, ρ(1) reicht von {de(r['min1'], 4)} bis {de(r['max1'], 4)} "
                        f"(Spanne {de(r['spanne1'], 4)}). Dass die Gleichheit an der Tourlänge als Summe von Kanten hängt, folgt aus der Skizze der Herleitung (nicht bewiesen), nicht aus dieser Messung.")
    if not gleich:
        return "warning", f"{wo}: ρ(1) reicht von {de(r['min1'], 6)} bis {de(r['max1'], 6)}; die Instanzen unterscheiden sich (Spanne {de_exp(r['spanne1'])})."
    formel = ""
    if nb == "2-opt":
        formel = f" Die Formel 1 − 2(n−1)/(n(n−3)) gibt {de(R.formel_2opt(n), 6)}."
    return "success", (
        f"{wo}: ρ(1) = **{de(r['rho1'], 6)}** in jeder Instanz (Spanne {de_exp(r['spanne1'])}, Rundungsfehler der Gleitkommarechnung).{formel} "
        f"Ein Unterschied zwischen diesen Instanzen in einer Schätzung ρ̂ ist Schätzrauschen: die Zahl misst hier n und die Nachbarschaft, nicht die Instanz."
    )


def verdict_route_wanderung(w: dict) -> tuple[str, str]:
    """Experiment 4, große n: läuft die Wanderung gegen den Wert der Formel? `w` ist das Ergebnis von `route_wanderung`."""
    abstand = abs(w["mittel"] - w["exakt"])
    kopf = (f"n = {w['n']}, 2-opt, eine Instanz ({S.FAMILIEN_TEXT[w['familie']]}), {w['wanderungen']} Wanderungen mit je {w['L']} Auswertungen (nicht aufgezählt): "
            f"Mittel der Schätzungen **{de(w['mittel'], 4)}**, Formel {de(w['exakt'], 4)}, Korrelationslänge der Formel τ = {de(w['tau'], 1)} Schritte (etwa n/2 für große n).")
    if w["se"] == 0:
        return "info", kopf
    z = abstand / w["se"]
    if z <= C.Z_BAND:
        return "success", kopf + f" Der Abstand {de(abstand, 4)} sind {de(z, 1)} Standardfehler: die Schätzung ist mit dem Wert der Formel verträglich (Band {de(C.Z_BAND, 0)} Standardfehler, Standardfehler aus {w['wanderungen']} Wanderungen)."
    return "warning", kopf + f" Der Abstand {de(abstand, 4)} sind {de(z, 1)} Standardfehler, mehr als das Band von {de(C.Z_BAND, 0)}."


# --------------------------------------------------------------------------------------------------------------------- weitere Tabellen der eingefrorenen Messung


def tabelle_streuung(m: dict) -> str:
    """Streuung der Schätzung bei L = 1000 gegen die Streuung der exakten Werte zwischen den Instanzen, je K und Messreihe."""
    kopf = "| K | Messreihe | SD der Schätzung innerhalb einer Instanz (L = 1000) | SD der exakten Werte zwischen 30 Instanzen | Verhältnis |\n|---|---|---|---|---|\n"
    zeilen = []
    for reihe in ("A", "B"):
        for z in m["nk_schaetzer"]["reihen"][reihe]:
            if z["L"] != 1000:
                continue
            verh = "kein Unterschied zwischen Instanzen" if z["sd_zwischen"] < C.NULL_SPANNE else de(z["sd_innen"] / z["sd_zwischen"], 1)
            zeilen.append((z["k"], reihe, f"| {z['k']} | {reihe} | {de(z['sd_innen'], 4)} | {de(z['sd_zwischen'], 4)} | {verh} |"))
    return kopf + "\n".join(text for _, _, text in sorted(zeilen))


def tabelle_route_wanderung(m: dict) -> str:
    kopf = "| n | Familie | L | Messreihe | Mittel von ρ̂(1) über 10 Wanderungen | Formel | Abstand in Standardfehlern |\n|---|---|---|---|---|---|---|\n"
    zeilen = []
    for reihe in ("A", "B"):
        for i, z in enumerate(m["route_wanderung"]["lang"][reihe]):
            abstand = abs(z["mittel"] - z["exakt"]) / z["se"]
            zeilen.append((i, reihe, f"| {z['n']} | {S.FAMILIEN_TEXT[z['familie']]} | {z['L']} | {reihe} | {de(z['mittel'], 5)} | {de(z['exakt'], 5)} | {de(abstand, 1)} |"))
    return kopf + "\n".join(text for _, _, text in sorted(zeilen))


def tabelle_route_guete(m: dict) -> str:
    kopf = "| n | L | Bias | SD innerhalb einer Instanz | Anteil mit Fehler über 0,1 | Median τ̂/τ |\n|---|---|---|---|---|---|\n"
    zeilen = []
    for a, b in zip(m["route_wanderung"]["guete"]["A"], m["route_wanderung"]["guete"]["B"]):
        zeilen.append(
            f"| {a['n']} | {a['L']} | {band(a['bias'], b['bias'], 4)} | {band(a['sd_innen'], b['sd_innen'], 4)} | "
            f"{band(100 * a['anteil_01'], 100 * b['anteil_01'], 1)} % | {band(a['tau_median'], b['tau_median'], 2)} |"
        )
    return kopf + "\n".join(zeilen)
