"""Feste Texte der App. Der Abschnitt GRENZEN steht wortgleich in der README (tests/test_claims.py vergleicht)."""

EINLEITUNG = """
Ein Suchverfahren bewegt sich durch eine **Landschaft**: jede Lösung hat einen Wert, und ein Schritt führt zu einem Nachbarn. Wie zerklüftet
diese Landschaft ist, wird üblicherweise mit **einer Zahl** gemessen, der **Autokorrelation** entlang einer **Zufallswanderung**: wie eng hängt
der Wert einer Lösung mit dem Wert nach s Schritten zusammen? Diese Demo misst die Zahl am **NK-Modell** (Regler K stellt die Rauigkeit ein)
exakt und per Wanderung und zeigt **zwei Fallen**: Die bekannte Formel 1 − (K+1)/N gilt für das Mittel über viele Landschaften, nicht für die
einzelne, und die Schätzung aus einer Wanderung ist verzerrt und streut. Als **Gegenbeispiel** dient die **Rundtour**: dort ist die exakte Zahl
für jede aufgezählte Instanz gleicher Größe (5 bis 9 Städte) dieselbe, sie misst die Zahl der Städte und nicht die Instanz.

Erstes Stück der Reihe „Landschaften, Einstellung und Vergleich“. Alle Instanzen sind erfunden (Zufallszahlen), es gibt keine reale Datenquelle.
Weiter unten: vier Abschnitte **🔬 Experiment**, der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
1. **Landschaft.** Im NK-Modell hat eine Lösung N Gene mit den Werten 0 oder 1. Die Fitness ist das Mittel von N Beiträgen; Beitrag i hängt am
   Gen i und an K weiteren Genen (hier: den K zyklisch folgenden). Nachbarn unterscheiden sich in genau einem Gen. Größer ist besser.
2. **Zufallswanderung.** Start an einem zufälligen Zustand, dann L − 1 Schritte zu je einem zufällig gewählten Nachbarn. Das kostet
   L **Auswertungen** der Zielfunktion (die Budget-Einheit dieser Reihe).
3. **Autokorrelation ρ(s).** Die Korrelation zweier Werte, die s Schritte auseinanderliegen. Nahe 1: Nachbarn haben ähnliche Werte. Nahe 0: der
   Wert eines Nachbarn sagt nichts über den eigenen.
4. **Exakt oder geschätzt.** Für kleine Aufgaben zählt die Demo alle Zustände auf und rechnet ρ(s) exakt. Die Schätzung ρ̂(s) nimmt nur die
   Werte einer Wanderung. Der Abstand zwischen beiden ist der Gegenstand der Experimente 1 und 3.
5. **Warum das zählt:** Wer zwei Instanzen an ihrer Rauigkeit unterscheiden will, muss wissen, ob ein Unterschied der Schätzwerte größer ist
   als das Rauschen des Schätzers. In der Messung dieser Demo (NK-Modell, N = 16, K ≥ 1, Wanderung mit 1000 Auswertungen) ist er das nicht: das Rauschen ist größer als der Unterschied zwischen den Instanzen, bei K = 1 und 2 nur knapp, ab K = 8 deutlich;
   auf der Rundtour haben die aufgezählten Instanzen gleicher Größe (5 bis 9 Städte) gar keinen Unterschied der exakten Werte.
"""

GRENZEN = """
| Annahme oder Grenze | Was dahinter steht | Wer setzt an |
|---|---|---|
| **Eine Zahl für die ganze Landschaft beschreibt die Instanz.** | Auf der Rundtour gilt das nicht (Experiment 4: ρ(1) ist in allen aufgezählten Instanzen gleich), im NK-Modell nur über K. Wohin ein Abstieg führt, sieht die Zahl nicht. | Nachfolger „Einzugsgebiete“ hebt die Annahme auf. |
| **Jeder Zustand hat seinen eigenen Wert, ein lokales Optimum ist ein eindeutiger Punkt.** | Hier gilt das, weil die Beiträge des NK-Modells stetig gleichverteilt sind: zwei Zustände mit demselben Wert kommen praktisch nicht vor. | Nachfolger „Plateaus“ hebt die Annahme mit groben, ganzzahligen Werten auf. |
| **Die Landschaft hat exakt gegebene Werte.** | Jede Auswertung liefert den Wert des Zustands. In dieser Demo rauscht nur der Schätzer (die Wanderung), nicht die Zielfunktion. | Nachfolger „Einstellen“ hebt die Annahme auf: dort ist die Güte einer Einstellung nur als verrauschter Lauf beobachtbar. |
| Gemessen wird entlang einer Wanderung über **alle** Zustände. | Wie die lokalen Optima zueinander liegen, misst diese Demo nicht. | Gegenstück „Tal oder Trichter“ (Gegensatz, keine aufgehobene Annahme). |
| Je Nachbarschaft **eine** Kennzahl. | ρ(1) ist in Experiment 4 bei Or-opt (mehr Nachbarn) kleiner als bei 2-opt; Zahl der Nachbarn und Art des Zuges sind dabei nicht getrennt. Zahl der Optima, Erfolg eines Abstiegs und Ergebnis bei gleichem Budget zeigt die Kennzahl nicht. Der Schalter „Or-opt“ ist ein Vorgriff. | Gegenstück „Nachbarschaft“ (Gegensatz, keine aufgehobene Annahme). |
| Zählweise | Budget-Einheit ist die Auswertung; eine Wanderung der Länge L kostet L Auswertungen, die Aufzählung 2^N bzw. (n−1)!/2. Die Zählweisen der Reihe (voll, Listen, Warteschlange) betreffen Abstiege; eine Wanderung bewertet je Schritt genau einen zufälligen Nachbarn, die Zählweise ändert hier nichts. | Den Umschalter der Zählweisen zeigt das Gegenstück „Nachbarschaft“. |
| Die Aussage zur Rundtour ist aufgezählt für n = 5 bis 9. | Für größere n ist sie nicht aufgezählt: Wanderungen laufen gegen den Wert der Formel. Die Herleitung ist eine Skizze, kein bewiesener Satz. Sie gilt für symmetrische Abstände, die Tourlänge als Summe von Kanten und eine Nachbarschaft, die sich beim Umbenennen der Städte nicht ändert. Gerichtete Touren sind nicht untersucht. | – |
| Die Korrelationslänge τ = −1/ln ρ(1) setzt exponentiellen Abfall voraus. | Bei K = 0 und bei 2-opt gilt ρ(s) = ρ(1)ˢ; in der Messung (N = 16, K = 1, 2, 4 und 8, s = 5) liegt ρ(s) darüber: τ ist dort kleiner als die aus ρ(5) abgelesene Länge −5/ln ρ(5) und unterschätzt die Reichweite. | – |
| Nutzen für die Wahl eines Verfahrens | Ob die Rauigkeit bei der Wahl eines Suchverfahrens hilft, ist **nicht gesichert** und kommt in dieser Demo nicht vor. | – |
"""

FORMELN = r"""
**Lesehilfe.** Gegeben ist eine Landschaft: eine Menge von Zuständen, eine Nachbarschaft und ein Wert $f(x)$ je Zustand. Gesucht ist eine Zahl
für den Zusammenhang benachbarter Werte.

| Symbol | Bedeutung |
|---|---|
| $N$ | Zahl der Gene im NK-Modell; $2^N$ Zustände |
| $K$ | Zahl der **weiteren** Gene, an denen ein Beitrag hängt (Zählweise von Kauffman); $0 \le K \le N-1$ |
| $k = K + 1$ | Zählweise einschließlich des Gens selbst (Campos u. a. 2002, Neidhart u. a. 2013) |
| $g = f - \bar f$ | Abweichung vom Mittel über **alle** Zustände der einen Landschaft |
| $A$ | Mittelung über die Nachbarn: $(Av)(x)$ ist das Mittel von $v$ über die Nachbarn von $x$ |
| $\rho(s)$ | exakte Autokorrelation im Abstand $s$ Schritte |
| $\hat\rho(s)$ | Schätzung aus einer Wanderung $f_1, \dots, f_L$ |
| $\tau$ | Korrelationslänge |
| $n$ | Zahl der Städte der Rundtour; $(n-1)!/2$ Touren |

**Exakt.**

$$\rho(s) = \frac{\langle g, A^s g \rangle}{\langle g, g \rangle}$$

Das ist die Korrelation zweier Werte im Abstand $s$ Schritte einer Zufallswanderung, die gleichverteilt über alle Zustände beginnt.

**Schätzer** mit dem Mittel $\bar f_L$ der Wanderung:

$$\hat\rho(s) = \frac{\frac{1}{L-s}\sum_{t=1}^{L-s} (f_t - \bar f_L)(f_{t+s} - \bar f_L)}{\frac{1}{L}\sum_{t=1}^{L} (f_t - \bar f_L)^2}$$

**Korrelationslänge** (setzt voraus, dass $\rho(s)$ wie $\rho(1)^s$ fällt):

$$\tau = -\frac{1}{\ln \rho(1)}$$

**Zwei Formeln für das NK-Modell.** Der Familienwert (Neidhart u. a. 2013, Gl. 21, dort mit $k = K+1$) nimmt Mittelwert und Varianz über die
Familie aller Landschaften:

$$R_1 = 1 - \frac{K+1}{N}$$

Für die einzelne Landschaft, die mit ihrem eigenen Mittel zentriert wird, ergibt das Verhältnis der Erwartungen von Zähler und Nenner (eigene
Herleitung, in Brüchen geprüft für $N = 3$, $K = 1$):

$$\rho(1) \approx 1 - \frac{K+1}{N\,\left(1 - 2^{-(K+1)}\right)}$$

Für $K = 0$ gilt das für jede nichtkonstante Landschaft exakt: $\rho(1) = 1 - 2/N$. Grund: der zentrierte Beitrag eines Gens ist
$d_i\,(x_i - \tfrac12)$; ein Wechsel des Gens kehrt sein Vorzeichen um (Korrelation $-1$), in der Familie wäre er neu gezogen (Korrelation $0$).

**Rundtour, 2-opt.** Aufgezählt für $n = 5$ bis $9$ ist für jede Instanz

$$\rho(1) = 1 - \frac{2(n-1)}{n(n-3)}, \qquad \rho(2) = \rho(1)^2$$

**Skizze der Begründung (kein bewiesener Satz).** Die Tourlänge ist eine Summe $\sum_e w_e \cdot 1[e \in \text{Tour}]$ über Kanten. Der Anteil
der Gewichte, der an einzelnen Städten hängt, ist auf allen Touren gleich, weil jede Stadt genau zwei Kanten hat. Auf dem verbleibenden Anteil
wirkt eine Nachbarschaft, die sich beim Umbenennen der Städte nicht ändert, wie die Multiplikation mit einer Zahl; diese Zahl hängt an $n$ und
an der Nachbarschaft, nicht an den Gewichten. Eine Quelle für die Formel wird nicht genannt; verwandt ist der Begriff der elementaren
Landschaft (Stadler 1996).

**Literatur.** Gelesen: Neidhart, Szendro, Krug (2013), Exact results for amplitude spectra of fitness landscapes, arXiv 1301.1923 (Gl. 21);
Campos, Adami, Wilke (2002), Optimal adaptive performance and delocalization in NK fitness landscapes, Physica A 304:495–506, arXiv
physics/0109020 (Zählweise $k$ einschließlich des Gens); Tomassini, Vérel, Ochoa, arXiv 1207.4442 (erwartete Zahl lokaler Optima $2^N/(N+1)$
bei $K = N-1$). Nicht gelesen (nur Abstract oder Sekundärquelle): Weinberger (1990), Correlated and uncorrelated fitness landscapes and how
to tell the difference, Biological Cybernetics 63(5):325–336; Stadler (1996), Landscapes and their correlation functions, J. Math. Chem.
20:1–45. Autokorrelation und NK-Modell sind Lehrbuchstoff; diese Demo behauptet nichts Neues, sie führt die Messung mit Zähleinheiten vor.
"""

ABGRENZUNG = """
**Abgrenzung.** „Autokorrelation“ heißt dieselbe Rechnung auch bei Zeitreihen (der Wert hängt vom Wert davor ab). Hier läuft die Reihe nicht
über die Zeit, sondern entlang einer Zufallswanderung im Suchraum. Die Tauschlandschaft einer Anordnungsaufgabe vollständig zu sehen
(lokale Optima, Erfolg eines Abstiegs) zeigt die Demo zur quadratischen Zuordnung; die Rauigkeit zu **messen** ist der Beitrag dieser Demo.
"""

ERKLAERUNG_NACHBARSCHAFT = """
| Nachbarschaft | Was ein Zug tut | Zahl der Nachbarn je Tour |
|---|---|---|
| **2-opt** | Zwei Kanten der Tour werden entfernt, der Abschnitt dazwischen wird umgedreht. | n(n−3)/2 |
| **Or-opt** | Ein Abschnitt von 1 bis 3 Städten wird herausgenommen und an anderer Stelle wieder eingesetzt, vorwärts oder rückwärts; gleiche Ergebnisse zählen einmal. | 10 / 29 / 63 / 108 / 165 für n = 5 bis 9 (gezählt) |
"""

ERKLAERUNG_FAMILIEN = """
| Familie | Wie die Instanz entsteht |
|---|---|
| gleichverteilt | Städte gleichverteilt im Quadrat |
| geclustert | Städte um wenige Zentren gestreut |
| Gitter mit Rauschen | Städte auf einem Gitter, leicht verschoben |
| Straßennetz | Städte entlang weniger Strecken |
| Zufallsmatrix (nicht-euklidisch) | Abstände sind ganze Zufallszahlen ohne Lage in der Ebene |
"""
