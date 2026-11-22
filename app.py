"""Landschaft sehen und Rauigkeit messen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Erstes Stück der Reihe „Landschaften, Einstellung und Vergleich“: Autokorrelation einer Zufallswanderung am NK-Modell (exakt und geschätzt)
und an der Rundtour als Gegenbeispiel. Aufbau nach DEMO-PLAYBOOK.md §2.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import lsm_constants as C
import lsm_evaluation as ev
import lsm_layout as LY
import lsm_nk as NK
import lsm_presets as P
import lsm_route as R
import lsm_scenario as S
import lsm_texts as T
import lsm_visualization as V
import modul_frisch

modul_frisch.aktualisieren(__file__)

st.set_page_config(page_title="Landschaft sehen und Rauigkeit messen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _landschaft(n, k, idx):
    return ev.landschaft(n, k, idx)


@st.cache_data(show_spinner=False)
def _profil(n, k, idx, laenge, wseed):
    return ev.profil(_landschaft(n, k, idx)["f"], n, idx, laenge, wseed)


@st.cache_data(show_spinner=False)
def _formeln(n, k, start, instanzen):
    return ev.formeln(n, k, start, instanzen)


@st.cache_data(show_spinner=False)
def _schaetzung(n, k, start, instanzen, wanderungen):
    return ev.schaetzung(n, k, start, instanzen, wanderungen, mit_werten=True)


@st.cache_data(show_spinner=False)
def _route_exakt(n, nachbarschaft, je_familie, start, quadrat):
    return ev.route_exakt(n, nachbarschaft, je_familie, start, quadrat)


@st.cache_data(show_spinner=False)
def _route_wanderung(n, idx):
    return ev.route_wanderung(n, C.ROUTE_FAMILIE, idx)


@st.cache_data(show_spinner=False)
def _messung():
    return ev.lade_messung()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in lsm_layout.py).
st.html(LY.kopf_css(LY.dunkles_design()))
with st.container(key="kopf"):
    st.title("⛰️ Landschaft sehen und Rauigkeit messen")
st.markdown(T.EINLEITUNG)

with st.expander("So funktioniert die Messung der Rauigkeit", expanded=True):
    st.markdown(T.SO_FUNKTIONIERT)
    st.markdown(T.ABGRENZUNG)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

P.load_permalink_settings()
P.init_session_state_defaults()
P.klemme_k()

with st.sidebar:
    P.sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ NK-Landschaft")
    n = st.slider("Gene N", *P.bounds("n_slider"), key="n_slider", on_change=P.klemme_k, help="Zahl der Gene; die Landschaft hat 2^N Zustände, die alle aufgezählt werden.")
    k = st.slider("Wechselwirkung K", *P.bounds("k_slider"), key="k_slider", on_change=P.klemme_k,
                  help="An wie vielen WEITEREN Genen ein Beitrag hängt. K ist höchstens N − 1; ein größerer Wert wird auf N − 1 gesetzt.")
    mitgen = st.toggle("K zählt das Gen selbst mit (k = K + 1)", key="konv_toggle",
                       help="Nur die Schreibweise: manche Quellen zählen das Gen selbst mit. Die Landschaft bleibt dieselbe, die Texte nennen dann zusätzlich k.")
    seed = st.number_input("Zufalls-Seed der Landschaft", *P.bounds("seed_input"), key="seed_input", step=1,
                           help="Laufende Nummer der Landschaft. Die Experimente 2 und 3 nehmen diese und die folgenden Nummern.")
    st.header("🚶 Wanderung")
    laenge = st.select_slider("Länge L (Auswertungen)", options=C.L_OPTIONEN, key="l_select", help="Zahl der Zustände der Wanderung in Experiment 1; jeder kostet eine Auswertung.")
    wseed = st.number_input("Zufalls-Seed der Wanderung", *P.bounds("wseed_input"), key="wseed_input", step=1)
    st.header("🔬 Experimente 2 und 3")
    instanzen = st.slider("Landschaften", *P.bounds("inst_slider"), key="inst_slider", help="Zahl der Landschaften mit gleichem N und K.")
    wanderungen = st.slider("Wanderungen je Landschaft", *P.bounds("wand_slider"), key="wand_slider", help="Experiment 3: so viele Schätzungen je Landschaft und Länge.")
    st.header("🚚 Rundtour (Experiment 4)")
    rn = st.slider("Städte n (aufgezählt)", *P.bounds("rn_slider"), key="rn_slider", help="Alle (n−1)!/2 Touren werden aufgezählt.")
    nb = st.radio("Nachbarschaft", C.NACHBARSCHAFTEN, key="nb_radio", help="Or-opt ist ein Vorgriff auf das Gegenstück „Nachbarschaft“; die Erklärung steht in Experiment 4.")
    quadrat = st.toggle("Gegenprobe: Quadrat der Tourlänge", key="quad_toggle", help="Als Landschaft dient das Quadrat der Tourlänge, das keine Summe von Kanten ist.")
    rinst = st.slider("Instanzen je Familie", *P.bounds("rinst_slider"), key="rinst_slider", help="Fünf Familien; die Zahl gilt je Familie.")
    rseed = st.number_input("Zufalls-Seed der Rundtour-Instanzen", *P.bounds("rseed_input"), key="rseed_input", step=1, help="Laufende Nummer der ersten Instanz je Familie.")
    wn = st.select_slider("Städte n (per Wanderung)", options=C.WN_OPTIONEN, key="wn_select", help="Zu groß zum Aufzählen: 2-opt-Wanderungen gegen den Wert der Formel.")
    st.button("🎲 Neue Landschaft generieren", width="stretch", on_click=P.randomize_seed)

n, k, seed, laenge, wseed = int(n), int(k), int(seed), int(laenge), int(wseed)
instanzen, wanderungen, rn, rinst, rseed, wn = int(instanzen), int(wanderungen), int(rn), int(rinst), int(rseed), int(wn)
P.sync_query_params({
    "n_slider": n, "k_slider": k, "konv_toggle": bool(mitgen), "seed_input": seed, "l_select": laenge, "wseed_input": wseed, "inst_slider": instanzen,
    "wand_slider": wanderungen, "rn_slider": rn, "nb_radio": nb, "quad_toggle": bool(quadrat), "rinst_slider": rinst, "rseed_input": rseed, "wn_select": wn,
})
k_text = f"K = {k}" + (f" (k = {k + 1})" if mitgen else "")

land = _landschaft(n, k, seed)
prof = _profil(n, k, seed, laenge, wseed)
rho1 = land["rho"][0] if land["rho"] else None
dach1 = prof["dach"][0]
familie, endlich = NK.familienwert(n, k), NK.einzelwert_erwartung(n, k)

# --- Experiment 1 (Primäransicht) ------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Experiment 1: Höhenprofil entlang einer Wanderung")
st.caption(f"NK-Landschaft mit N = {n}, {k_text}, Zufalls-Seed {seed}; Wanderung mit L = {laenge} Auswertungen. Exakte Werte aus der Aufzählung aller {2 ** n} Zustände.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ρ(1) exakt", "nicht definiert" if rho1 is None else ev.de(rho1))
# Delta immer als „mein Wert minus Referenz“ (Schätzung minus exakter Wert).
m2.metric("ρ̂(1) der Wanderung", "nicht definiert" if dach1 is None else ev.de(dach1),
          delta=None if rho1 is None or dach1 is None else f"{ev.de(dach1 - rho1)} gegen exakt", delta_color="off")
m3.metric("Familienwert 1 − (K+1)/N", ev.de(familie))
m4.metric("Lokale Optima", f"{land['optima']}", delta=f"von {2 ** n} Zuständen", delta_color="off")
st.plotly_chart(V.build_profil(prof["reihe"]), width="stretch", key="profil_chart")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(V.build_histogramm(prof["reihe"]), width="stretch", key="hist_chart")
    st.caption("Verteilung der Fitnesswerte entlang der Wanderung.")
with c2:
    if land["rho"]:
        st.plotly_chart(V.build_rho_s(land["rho"], prof["dach"], familie), width="stretch", key="rho_s_chart")
        st.caption("Autokorrelation gegen den Schrittabstand s: exakt, als Potenz des exakten ρ(1), als Potenz des Familienwerts und als Schätzung dieser Wanderung.")
kind, text = ev.verdict_profil(n, k, rho1, dach1, laenge, land["optima"])
getattr(st, kind)(text)

# --- Kernfragen ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
st.markdown("**1. Was misst die Autokorrelation an dieser Landschaft?** Die Antwort steht im Verdikt direkt über diesem Abschnitt.")
st.markdown("**2. Welche der zwei Formeln gilt für diese Landschaft?**")
kind, text = ev.verdict_einzel(n, k, rho1, familie, endlich)
getattr(st, kind)(text)
st.markdown("**3. Wie genau ist die Messung mit einer Wanderung?**")
kind, text = ev.verdict_fehler(rho1, dach1, laenge)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2 ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Zwei Formeln, viele Landschaften")
st.caption(f"{instanzen} Landschaften mit N = {n}, {k_text} (Zufalls-Seeds {seed} bis {seed + instanzen - 1}); je Landschaft das exakte ρ(1) aus allen {2 ** n} Zuständen.")
with st.spinner(f"Zähle {instanzen} Landschaften auf (wenige Sekunden) …"):
    fo = _formeln(n, k, seed, instanzen)
if fo["werte"]:
    st.plotly_chart(V.build_formeln(fo["werte"], fo["familie"], fo["endlich"]), width="stretch", key="formeln_chart")
kind, text = ev.verdict_formeln(n, k, fo)
getattr(st, kind)(text)
with st.expander("Eingefrorene Messung: N = 16, sechs Werte von K, zweimal 30 Landschaften"):
    st.markdown(ev.tabelle_nk_exakt(_messung()))
    st.caption("Zwei getrennte Sätze von je 30 Landschaften; wo sie sich unterscheiden, steht das Band „kleiner bis größer“. ρ(5) − ρ(1)⁵ ist bei K = 1, 2, 4 und 8 "
               "in jeder der 60 Landschaften positiv: die Autokorrelation fällt dort langsamer als die Potenz. Quelle: lsm_messung.json, erzeugt von tools/lsm_make_messung.py.")

st.markdown("---")

# --- Experiment 3 ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Wie genau misst die Wanderung?")
st.caption(f"{instanzen} Landschaften × {wanderungen} Wanderungen je Länge L = 100, 1000 und 10000 (N = {n}, {k_text}); jede Schätzung gegen den exakten Wert ihrer Landschaft.")
with st.spinner(f"Rechne {instanzen * wanderungen * len(C.L_GUETE)} Wanderungen (wenige Sekunden) …"):
    sc = _schaetzung(n, k, seed, instanzen, wanderungen)
if sc["instanzen"]:
    st.plotly_chart(V.build_schaetzung(sc["zeilen"]), width="stretch", key="schaetzung_chart")
    st.caption("Kasten: mittlere Hälfte der Fehler; gepunktete Linien: Fehler von ±0,1.")
    st.markdown(
        "| L | Bias | SD innerhalb einer Instanz | Anteil mit Fehler über 0,1 | Median τ̂/τ |\n|---|---|---|---|---|\n" + "\n".join(
            f"| {z['L']} | {ev.de(z['bias'], 4)} | {ev.de(z['sd_innen'], 4)} | {ev.de(100 * z['anteil_01'], 1)} % | {ev.tau_text(z)} |" for z in sc["zeilen"])
    )
    st.caption(f"Streuung der exakten Werte zwischen den {sc['instanzen']} Landschaften: {ev.de(sc['sd_zwischen'], 4)}. τ̂/τ vergleicht die Korrelationslänge aus der Schätzung mit der aus dem "
               "exakten ρ(1); bei K ≥ 1 ist τ selbst nur eine Näherung, weil ρ(s) dort über ρ(1)ˢ liegt.")
    kind, text = ev.verdict_schaetzung(n, k, sc)
    getattr(st, kind)(text)
with st.expander("Eingefrorene Messung: N = 16, zweimal 30 Landschaften × 30 Wanderungen"):
    st.markdown(ev.tabelle_nk_schaetzer(_messung()))
    st.caption("Zwei getrennte Sätze von Landschaften und Zufalls-Seeds als Band. Quelle: lsm_messung.json, erzeugt von tools/lsm_make_messung.py.")

st.markdown("---")

# --- Experiment 4 ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Rundtour als Gegenbeispiel")
st.caption(f"n = {rn} Städte, {nb}, {rinst} Instanzen je Familie (laufende Nummern {rseed} bis {rseed + rinst - 1}); alle Touren aufgezählt.")
with st.spinner("Zähle alle Touren auf (bei n = 9 und Or-opt einige Sekunden) …"):
    ro = _route_exakt(rn, nb, rinst, rseed, bool(quadrat))
r1, r2, r3, r4 = st.columns(4)
r1.metric("Touren = Auswertungen der Aufzählung", f"{ro['touren']}")
r2.metric("Nachbarn je Tour", f"{ro['nachbarn']}")
r3.metric("ρ(1), Mittel der Instanzen", ev.de(ro["rho1"], 4))
r4.metric("ρ(2), Mittel der Instanzen", ev.de(ro["rho2"], 4), delta=f"ρ(1)² = {ev.de(ro['rho1'] ** 2, 4)}", delta_color="off")
st.plotly_chart(V.build_route(ro["zeilen"], R.formel_2opt(rn) if nb == "2-opt" and not quadrat else None, eng=not quadrat), width="stretch", key="route_chart")
kind, text = ev.verdict_route(ro)
getattr(st, kind)(text)
with st.expander("Erklärung: Nachbarschaften und Familien"):
    st.markdown(T.ERKLAERUNG_NACHBARSCHAFT)
    st.markdown(T.ERKLAERUNG_FAMILIEN)
with st.expander("Eingefrorene Messung: n = 5 bis 9, zweimal 150 Instanzen je Zeile"):
    st.markdown(ev.tabelle_route_exakt(_messung()))
    st.caption("Je Zeile zweimal 150 Instanzen (fünf Familien zu je 30). Bei Or-opt liegt ρ(2) für n = 6 bis 9 über ρ(1)²: diese Wanderung fällt nicht exakt wie eine Potenz. "
               "Quelle: lsm_messung.json, erzeugt von tools/lsm_make_messung.py.")

st.markdown(f"**Größere n per Wanderung.** n = {wn} Städte sind zu viele zum Aufzählen; {C.ROUTE_WANDERUNGEN} Wanderungen in der 2-opt-Nachbarschaft mit je {C.ROUTE_L} Auswertungen.")
with st.spinner(f"Rechne {C.ROUTE_WANDERUNGEN} Wanderungen mit je {C.ROUTE_L} Auswertungen (wenige Sekunden) …"):
    rw = _route_wanderung(wn, rseed)
w1, w2, w3 = st.columns(3)
w1.metric("ρ̂(1), Mittel der Wanderungen", ev.de(rw["mittel"], 4), delta=f"{ev.de(rw['mittel'] - rw['exakt'], 4)} gegen Formel", delta_color="off")
w2.metric("Formel 1 − 2(n−1)/(n(n−3))", ev.de(rw["exakt"], 4))
w3.metric("Korrelationslänge τ der Formel", f"{ev.de(rw['tau'], 1)} Schritte")
kind, text = ev.verdict_route_wanderung(rw)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen ---------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.GRENZEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.FORMELN)

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
