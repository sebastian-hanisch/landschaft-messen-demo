"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import lsm_constants as C
import lsm_scenario as S


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_profil(reihe):
    """Fitness entlang der Wanderung (Schritt 0 ist der Start)."""
    fig = go.Figure(go.Scatter(x=list(range(len(reihe))), y=list(reihe), mode="lines", line=dict(color=C.COLOR_LINE, width=1.2),
                               hovertemplate="Schritt %{x}: %{y:.4f}<extra></extra>", name="Fitness"))
    fig.update_xaxes(title_text="Schritt der Wanderung")
    fig.update_yaxes(title_text="Fitness")
    return _base(fig)


def build_histogramm(reihe):
    """Verteilung der Fitnesswerte, die die Wanderung gesehen hat."""
    fig = go.Figure(go.Histogram(x=list(reihe), nbinsx=30, marker_color=C.COLOR_SECOND, hovertemplate="Fitness %{x}: %{y} Schritte<extra></extra>", name="Schritte"))
    fig.update_xaxes(title_text="Fitness")
    fig.update_yaxes(title_text="Zahl der Schritte")
    return _base(fig)


def build_rho_s(exakt, dach, familie: float):
    """Autokorrelation gegen den Schrittabstand: exakt, Potenz des exakten rho(1), Schätzung der Wanderung, Familienwert hoch s."""
    xs = list(range(1, len(exakt) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=list(exakt), mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3), name="exakt ρ(s)",
                             hovertemplate="s = %{x}: %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[exakt[0] ** s for s in xs], mode="lines", line=dict(color=C.COLOR_GREY, dash="dot"), name="ρ(1) hoch s",
                             hovertemplate="s = %{x}: %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[familie ** s for s in xs], mode="lines", line=dict(color=C.COLOR_THIRD, dash="dash"), name="Familienwert hoch s",
                             hovertemplate="s = %{x}: %{y:.4f}<extra></extra>"))
    punkte = [(s, d) for s, d in zip(xs, dach) if d is not None]
    if punkte:
        fig.add_trace(go.Scatter(x=[p[0] for p in punkte], y=[p[1] for p in punkte], mode="markers", marker=dict(color=C.COLOR_SECOND, size=9, symbol="x"),
                                 name="Schätzung der Wanderung", hovertemplate="s = %{x}: %{y:.4f}<extra></extra>"))
    fig.update_xaxes(title_text="Schrittabstand s", dtick=1)
    fig.update_yaxes(title_text="Autokorrelation")
    return _base(fig)


def build_formeln(werte, familie: float, endlich: float):
    """Exaktes rho(1) je Instanz als Punkte, die zwei Formeln als waagerechte Linien."""
    xs = list(range(1, len(werte) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=list(werte), mode="markers", marker=dict(color=C.COLOR_LINE, size=8), name="exakt, je Landschaft",
                             hovertemplate="Landschaft %{x}: %{y:.4f}<extra></extra>"))
    rand = [0.5, len(werte) + 0.5]
    fig.add_trace(go.Scatter(x=rand, y=[familie, familie], mode="lines", line=dict(color=C.COLOR_THIRD, dash="dash"), name="Familienwert 1 − (K+1)/N", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=rand, y=[endlich, endlich], mode="lines", line=dict(color=C.COLOR_SECOND), name="Formel für die einzelne Landschaft", hoverinfo="skip"))
    fig.update_xaxes(title_text="Landschaft (laufende Nummer in der Stichprobe)")
    fig.update_yaxes(title_text="ρ(1)")
    return _base(fig)


def build_schaetzung(zeilen):
    """Fehler der Schätzungen (Schätzwert minus exakter Wert der Landschaft) je Länge als Kastendiagramm."""
    fig = go.Figure()
    farben = (C.COLOR_THIRD, C.COLOR_SECOND, C.COLOR_LINE)
    for z, farbe in zip(zeilen, farben):
        fig.add_trace(go.Box(y=list(z["fehler"]), name=f"L = {z['L']}", marker_color=farbe, boxpoints="outliers", hoverinfo="y"))
    fig.add_hline(y=0, line=dict(color=C.COLOR_GREY, width=1))
    for grenze in (-C.FEHLER_GROB, C.FEHLER_GROB):
        fig.add_hline(y=grenze, line=dict(color=C.COLOR_GREY, width=1, dash="dot"))
    fig.update_yaxes(title_text="Schätzung minus exakter Wert")
    fig.update_layout(showlegend=False)
    return _base(fig)


def build_route(zeilen, formel=None, eng: bool = True):
    """Exaktes rho(1) je Rundtour-Instanz, nach Familie gefärbt. `eng`: feste Achse von ±0,05 um das Mittel (zeigt, dass alle Punkte auf einer Linie liegen)."""
    fig = go.Figure()
    for familie in S.FAMILIEN:
        teil = [z for z in zeilen if z["familie"] == familie]
        if not teil:
            continue
        fig.add_trace(go.Scatter(x=[z["idx"] for z in teil], y=[z["rho1"] for z in teil], mode="markers", marker=dict(color=C.FAMILIEN_FARBEN[familie], size=8),
                                 name=S.FAMILIEN_TEXT[familie], hovertemplate="Instanz %{x}: %{y:.6f}<extra></extra>"))
    if formel is not None:
        xs = [min(z["idx"] for z in zeilen) - 0.5, max(z["idx"] for z in zeilen) + 0.5]
        fig.add_trace(go.Scatter(x=xs, y=[formel, formel], mode="lines", line=dict(color=C.COLOR_GREY, dash="dot"), name="Formel 1 − 2(n−1)/(n(n−3))", hoverinfo="skip"))
    if eng and zeilen:
        mitte = sum(z["rho1"] for z in zeilen) / len(zeilen)
        fig.update_yaxes(range=[mitte - 0.05, mitte + 0.05])
    fig.update_xaxes(title_text="laufende Nummer der Instanz")
    fig.update_yaxes(title_text="ρ(1), exakt")
    return _base(fig)
