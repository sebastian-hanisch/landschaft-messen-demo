# Landschaft sehen und Rauigkeit messen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-landschaft-messen-demo.streamlit.app/)** -->

Erstes Stück der Reihe **„Landschaften, Einstellung und Vergleich“** (Bereich Optimierung, Feld „Metaheuristiken und Suche“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Demo ist die Wurzel der Reihe: Sie stellt die übliche Kennzahl für die Rauigkeit einer Suchlandschaft vor, die **Autokorrelation entlang einer Zufallswanderung**, und misst, was diese Zahl leistet und was nicht. Fahrzeug der Rauigkeit ist das **NK-Modell** (Regler K), Gegenbeispiel ist die **Rundtour** mit der 2-opt-Nachbarschaft.

Nachfolger und ihr Verhältnis zu dieser Demo stehen im Abschnitt „Ehrliche Grenzen“. Die Tauschlandschaft einer Anordnungsaufgabe vollständig zu sehen (lokale Optima, Erfolg eines Abstiegs) zeigt die Demo `quadratische-zuordnung-demo` aus der Reihe zum Anordnen; die Rauigkeit zu messen ist der Beitrag dieser Demo. Alle Instanzen sind erfunden (Zufallszahlen aus SplitMix64), es gibt keine reale Datenquelle.

## Kernfrage

Wie zerklüftet ist die Landschaft, durch die ein Suchverfahren läuft, und lässt sich das mit einer Zahl aus einer Zufallswanderung messen? Drei Teilfragen: (1) Was misst die Autokorrelation? (2) Welche der zwei Formeln für das NK-Modell gilt für die einzelne Landschaft? (3) Wie genau ist die Schätzung aus einer Wanderung, verglichen mit dem Unterschied zwischen zwei Instanzen?

Die Antwort in einem Absatz (NK-Modell mit gleichverteilten Beiträgen und zyklisch benachbarten Genen, N = 16; Rundtour mit symmetrischen Abständen; Pearson-Autokorrelation über alle Zustände; Zähleinheit Instanz bzw. Schätzung; je zwei getrennte Messreihen): Der Familienwert 1 − (K+1)/N gilt für das Mittel über die Familie, nicht für die einzelne Landschaft (K = 0: 0,9375 gegen exakt 0,8750 in jeder der 60 Landschaften). Die Schätzung aus einer Wanderung ist nach unten verschoben (bei L = 100 um −0,041 bis −0,027 für K = 0 bis 8) und streut bei L = 1000 für jedes K von 1 bis 15 stärker, als sich 30 Instanzen gleichen K unterscheiden (Verhältnis 1,1 bis 25,2 in 10 von 10 Zellen; am knappsten bei K = 1, dort innerhalb der Unsicherheit der SD aus 30 Landschaften). Auf der Rundtour ist die exakte Autokorrelation der 2-opt-Wanderung für n = 5 bis 9 in jeder von 300 aufgezählten Instanzen je n derselbe Wert 1 − 2(n−1)/(n(n−3)) (größte Spanne 3,7e−15, Rundungsfehler): Sie misst n, nicht die Instanz.

## Befunde und Korrekturen

Die Vormessung der Planung nutzte eigene Wegwerf-Skripte mit anderem Zufallsgenerator und anderen Instanzen. Im Bau wurde jede Zahl mit der gemeinsamen Basis der Reihe und SplitMix64 neu gemessen. Was sich verschoben hat:

| Punkt | Vormessung | Bau (diese README) | Grund |
|---|---|---|---|
| Zahl der lokalen Optima, N = 16 | K = 2 / 4 / 8: 25,6 / 132,0 / 767,9 (Mittel von 30) | 29,9 bis 38,2 / 171,7 bis 183,1 / 896,2 bis 899,6 | Die Vormessung ließ jeden Beitrag an K **zufällig gewählten** weiteren Genen hängen, die gemeinsame Basis der Reihe nimmt die K **zyklisch folgenden**. Gegenprobe beim Bau mit dem Skript der Vormessung auf denselben Tabellen (30 Landschaften je K, nicht im Repo, nicht im Test): 130 und 777 mit zufälligen Genen, 170 und 892 mit benachbarten (K = 4 und 8); als Größenordnung zu lesen, denn das Skript liegt nicht im Repo, und eine Nachstellung mit anderen Instanzen ergab 127 und 760 gegen 172 und 900. |
| Verschiebung der Schätzung bei L = 100 | −0,03 bis −0,04 für K = 0 bis 8; K = 15: −0,018 | −0,041 bis −0,027 für K = 0 bis 8; K = 15: −0,011 bis −0,010 | Bei K = 8 und K = 15 liegt die Verschiebung näher an null als in der Vormessung; Richtung und Größenordnung bleiben. |
| Größte Spanne von ρ(1) über die Rundtour-Instanzen | höchstens 8e−16 | 3,7e−15 | Die Basis der Reihe nimmt ganzzahlige Koordinaten bis 9999 statt des Einheitsquadrats; die Summen sind größer, der Rundungsfehler auch. Die Aussage „unter 1e−15“ der Planung ist auf „unter 1e−14“ zurückgenommen. |
| Gegenprobe „Quadrat der Tourlänge“, n = 8 | Spanne 0,0017 (30 Instanzen) | Spanne 0,0067 bis 0,0069 (150 Instanzen je Messreihe) | Andere und mehr Instanzen, darunter die nicht-euklidische Familie. Der Befund (die Instanzen unterscheiden sich) bleibt. |
| Familien der Rundtour | Regler „Familie“, vier Familien | alle fünf Familien gleichzeitig im Diagramm | Die Basis der Reihe bringt zusätzlich die Familie „Straßennetz“ mit; ein Diagramm mit allen Familien zeigt die Gleichheit direkter als ein Umschalter. |
| Preset N = 18 | als Preset empfohlen | gestrichen, N höchstens 16 | Eine Landschaft mit N = 18 und K = 17 kostete beim Bau 1,4 Sekunden (eine Messung auf dem Baurechner); Experiment 2 mit 30 Landschaften läge bei etwa 40 Sekunden. |
| Or-opt bei n = 5 | nicht betrachtet (n = 6 bis 9) | 10 Nachbarn je Tour, ρ(1) = 0 bis auf Rundung | Bei fünf Städten sind 10 der 11 anderen Touren Or-opt-Nachbarn. Die Aussagen zu Or-opt nennen deshalb n = 6 bis 9. |

Kein Befund der Planung hat sich umgedreht.

## Modell

**NK-Modell.** N Gene mit den Werten 0 oder 1. Die Fitness ist das Mittel von N Beiträgen; Beitrag i hängt am Gen i und an den K zyklisch folgenden Genen und wird aus einer Tabelle mit 2^(K+1) gleichverteilten Zufallszahlen in [0, 1) gelesen. K zählt die **weiteren** Gene (Zählweise von Kauffman); Campos u. a. 2002 und Neidhart u. a. 2013 zählen k = K + 1 einschließlich des Gens selbst (Schalter in der App). Nachbarn unterscheiden sich in genau einem Gen. Größer ist besser; ein lokales Optimum ist ein Zustand, dessen N Nachbarn alle echt schlechter sind. Regler: N = 4 bis 16, K = 0 bis N − 1.

**Rundtour.** n Städte, symmetrische Abstände, Zielgröße ist die Tourlänge. Fünf Familien: gleichverteilt, geclustert, Gitter mit Rauschen, Straßennetz (alle mit ganzzahligen Koordinaten 0 bis 9999 aus der gemeinsamen Basis der Reihe) und eine Zufallsmatrix mit ganzzahligen Abständen 1 bis 9999 ohne Lage in der Ebene (nicht-euklidisch). Nachbarschaften: 2-opt (ein Abschnitt wird umgedreht, n(n−3)/2 Nachbarn) und Or-opt (ein Abschnitt von 1 bis 3 Städten wird versetzt, vorwärts oder rückwärts; 10 / 29 / 63 / 108 / 165 verschiedene Nachbarn für n = 5 bis 9).

**Autokorrelation.** Exakt: ρ(s) = ⟨g, Aˢ g⟩ / ⟨g, g⟩ mit g = Wert minus Mittel über **alle** Zustände und A = Mittel über die Nachbarn. Schätzer ρ̂(s) aus einer Wanderung der Länge L: Kovarianz bei Verschiebung s (Summe durch L − s) durch Varianz (Summe durch L), beide mit dem Mittel der Wanderung. Korrelationslänge τ = −1/ln ρ(1). Alle Formeln stehen im 📐-Expander der App.

**Zwei Formeln für das NK-Modell.** Familienwert R₁ = 1 − (K+1)/N (Neidhart u. a. 2013, Gl. 21): Korrelation mit Mittelwert und Varianz der Landschaftsfamilie. Formel für die einzelne Landschaft (eigene Herleitung): 1 − (K+1)/(N(1 − 2^−(K+1))), das Verhältnis der Erwartungen von Zähler und Nenner; für K = 0 ist sie für jede nichtkonstante Landschaft exakt 1 − 2/N.

**Budget und Zählweise.** Budget-Einheit der Reihe ist die Auswertung. Eine Wanderung der Länge L kostet L Auswertungen, die Aufzählung 2^N bzw. (n−1)!/2. Die Zählweisen der Reihe (voll, Listen, Warteschlange) betreffen Abstiege und ändern an einer Wanderung nichts.

## Methodik

- **Exakt:** Aufzählung aller Zustände (bis 65536 beim NK-Modell, bis 20160 Touren bei n = 9) und der Operator A als Tabelle der Nachbarn.
- **Wanderung:** gleichverteilter Start, dann je Schritt ein gleichverteilt gewählter Nachbar. Zufall aus SplitMix64 (auf jeder Plattform dieselben Folgen).
- **Eingefrorene Messung** (`lsm_messung.json`, erzeugt von `tools/lsm_make_messung.py`, Stand 2026-11-21): zwei getrennte Messreihen A und B (laufende Nummern der Instanzen ab 0 bzw. ab 1000, getrennte Zufalls-Seeds der Wanderungen). Die Tabellen unten nennen beide als Band „kleiner bis größer“.
- **Live in der App:** dieselben Rechnungen für die Regler der Seitenleiste, mit Fortschrittsanzeige.

## Befunde (gemessen, keine Behauptungen)

### NK-Modell, exakt (N = 16, zweimal 30 Landschaften je K, alle 65536 Zustände aufgezählt)

| K | Familienwert | Endlichkeitskorrektur | Mittel exakt | SD zwischen Instanzen | ρ(5) − ρ(1)⁵ | lokale Optima (Mittel) |
|---|---|---|---|---|---|---|
| 0 | 0,9375 | 0,8750 | 0,8750 | 0,0000 | 0,0000 | 1,0 |
| 1 | 0,8750 | 0,8333 | 0,8290 bis 0,8335 | 0,0134 bis 0,0160 | 0,0181 bis 0,0186 | 8,6 |
| 2 | 0,8125 | 0,7857 | 0,7811 bis 0,7846 | 0,0156 bis 0,0159 | 0,0342 | 29,9 bis 38,2 |
| 4 | 0,6875 | 0,6774 | 0,6722 bis 0,6770 | 0,0117 bis 0,0132 | 0,0503 bis 0,0516 | 171,7 bis 183,1 |
| 8 | 0,4375 | 0,4364 | 0,4354 bis 0,4373 | 0,0048 bis 0,0054 | 0,0348 bis 0,0358 | 896,2 bis 899,6 |
| 15 | 0,0000 | 0,0000 | −0,0001 bis 0,0001 | 0,0014 bis 0,0016 | 0,0000 | 3856,9 bis 3859,4 |

- **K = 0:** jede der 60 Landschaften hat ρ(1) = 1 − 2/N = 0,8750 (größte Abweichung 7,8e−16) und genau ein lokales Optimum; ρ(s) ist für s = 2 und 5 die Potenz ρ(1)ˢ (Abweichung unter 1e−12).
- **Familienwert:** bei K = 1, 2 und 4 liegt er in 6 von 6 Zellen (3 K × 2 Messreihen) mehr als 4 Standardfehler über dem Mittel der exakten Werte (4,9 bis 16,9 Standardfehler); bei K = 8 sind es 0,2 bis 2,4 Standardfehler, dort ist der Unterschied der Formeln kleiner als das Rauschen von 30 Landschaften.
- **Formel für die einzelne Landschaft:** in 10 von 10 Zellen (K = 1, 2, 4, 8, 15) höchstens 2,2 Standardfehler vom Mittel entfernt.
- **Abfall langsamer als die Potenz:** ρ(5) − ρ(1)⁵ ist bei K = 1, 2, 4 und 8 in jeder der 240 Landschaften positiv (8 Zellen zu je 30), gemessen für N = 16 und s = 5. Die Korrelationslänge τ = −1/ln ρ(1) ist dort kleiner als die aus ρ(5) abgelesene Länge −5/ln ρ(5): τ unterschätzt dort die Reichweite.
- **Lokale Optima:** bei K = 1 haben die 60 Landschaften zwischen 1 und 24 Optima (eine Spanne dieser Stichprobe, keine Grenze); bei K = 15 liegt das Mittel bei 3856,9 bis 3859,4, die Erwartung 2^N/(N+1) ist 3855,1 (Tomassini, Vérel, Ochoa, arXiv 1207.4442).

### NK-Modell, Güte der Schätzung (N = 16, zweimal 30 Landschaften × 30 Wanderungen je Zelle)

| K | L | Bias | SD innerhalb einer Instanz | Anteil mit Fehler über 0,1 | Median τ̂/τ |
|---|---|---|---|---|---|
| 0 | 100 | −0,0395 bis −0,0391 | 0,0588 bis 0,0629 | 13,4 bis 15,0 % | 0,79 bis 0,80 |
| 0 | 1000 | −0,0029 | 0,0144 bis 0,0150 | 0,0 % | 0,98 |
| 0 | 10000 | −0,0005 bis −0,0003 | 0,0046 bis 0,0047 | 0,0 % | 1,00 |
| 1 | 100 | −0,0406 bis −0,0345 | 0,0622 bis 0,0668 | 14,7 bis 17,7 % | 0,82 bis 0,85 |
| 1 | 1000 | −0,0034 bis −0,0032 | 0,0169 bis 0,0177 | 0,0 % | 0,98 |
| 1 | 10000 | −0,0006 bis −0,0005 | 0,0054 bis 0,0056 | 0,0 % | 1,00 |
| 2 | 100 | −0,0395 bis −0,0393 | 0,0700 bis 0,0719 | 19,0 bis 20,2 % | 0,85 |
| 2 | 1000 | −0,0034 bis −0,0032 | 0,0197 bis 0,0213 | 0,0 bis 0,1 % | 0,98 bis 0,99 |
| 2 | 10000 | −0,0002 bis −0,0001 | 0,0061 bis 0,0064 | 0,0 % | 1,00 |
| 4 | 100 | −0,0374 bis −0,0346 | 0,0831 bis 0,0840 | 25,0 bis 25,3 % | 0,89 bis 0,90 |
| 4 | 1000 | −0,0044 bis −0,0043 | 0,0239 bis 0,0249 | 0,0 bis 0,1 % | 0,98 bis 0,99 |
| 4 | 10000 | −0,0004 | 0,0075 bis 0,0078 | 0,0 % | 1,00 |
| 8 | 100 | −0,0277 bis −0,0271 | 0,0960 bis 0,0964 | 31,9 bis 32,2 % | 0,94 |
| 8 | 1000 | −0,0033 bis −0,0031 | 0,0302 bis 0,0308 | 0,2 % | 0,99 |
| 8 | 10000 | −0,0007 bis 0,0001 | 0,0093 bis 0,0097 | 0,0 % | 1,00 |
| 15 | 100 | −0,0114 bis −0,0099 | 0,1057 bis 0,1083 | 35,8 % | nicht sinnvoll (ρ(1) nahe 0) |
| 15 | 1000 | −0,0017 bis −0,0010 | 0,0335 bis 0,0357 | 0,3 bis 0,7 % | nicht sinnvoll (ρ(1) nahe 0) |
| 15 | 10000 | −0,0003 bis 0,0001 | 0,0105 bis 0,0107 | 0,0 % | nicht sinnvoll (ρ(1) nahe 0) |

Der Bias ist das Mittel von Schätzung minus exaktem Wert der jeweiligen Landschaft. τ̂/τ vergleicht die Korrelationslänge aus der Schätzung mit der aus dem exakten ρ(1) (nur Schätzungen mit 0 < ρ̂ < 1).

| K | Messreihe | SD der Schätzung innerhalb einer Instanz (L = 1000) | SD der exakten Werte zwischen 30 Instanzen | Verhältnis |
|---|---|---|---|---|
| 0 | A | 0,0150 | 0,0000 | kein Unterschied zwischen Instanzen |
| 0 | B | 0,0144 | 0,0000 | kein Unterschied zwischen Instanzen |
| 1 | A | 0,0177 | 0,0160 | 1,1 |
| 1 | B | 0,0169 | 0,0134 | 1,3 |
| 2 | A | 0,0213 | 0,0159 | 1,3 |
| 2 | B | 0,0197 | 0,0156 | 1,3 |
| 4 | A | 0,0239 | 0,0117 | 2,1 |
| 4 | B | 0,0249 | 0,0132 | 1,9 |
| 8 | A | 0,0308 | 0,0054 | 5,7 |
| 8 | B | 0,0302 | 0,0048 | 6,3 |
| 15 | A | 0,0357 | 0,0014 | 25,2 |
| 15 | B | 0,0335 | 0,0016 | 21,1 |

In 10 von 10 Zellen mit K ≥ 1 streut die Schätzung bei L = 1000 stärker, als sich die 30 Instanzen unterscheiden; bei K = 1 ist der Abstand klein (Verhältnis 1,1 bis 1,3), bei K = 2 ebenso (1,3). Die SD zwischen den Instanzen stammt aus nur 30 Werten (relativer Standardfehler etwa 13 %); bei K = 1 und 2 liegt der Abstand innerhalb dieser Unsicherheit. Bei K = 0 gibt es zwischen Instanzen keinen Unterschied. Zwei Instanzen gleichen K lassen sich in dieser Messung mit einer Wanderung der Länge 1000 nicht zuverlässig unterscheiden: bei K = 1 und 2 ist das Rauschen nur knapp größer als der Unterschied zwischen den Instanzen, ab K = 8 deutlich größer (Verhältnis 5,7 bis 25,2).

### Rundtour, exakt (n = 5 bis 9, zweimal 150 Instanzen je Zeile: fünf Familien zu je 30)

| n | Nachbarschaft | Touren | Nachbarn je Tour | ρ(1) | ρ(2) | ρ(1)² | größte Spanne von ρ(1) |
|---|---|---|---|---|---|---|---|
| 5 | 2-opt | 12 | 5 | 0,200000 | 0,040000 | 0,040000 | 1,4e−16 |
| 5 | Or-opt | 12 | 10 | 0,000000 | 0,000000 | 0,000000 | 1,1e−28 |
| 6 | 2-opt | 60 | 9 | 0,444444 | 0,197531 | 0,197531 | 7,2e−16 |
| 6 | Or-opt | 60 | 29 | 0,252874 | 0,066587 | 0,063945 | 3,9e−16 |
| 7 | 2-opt | 360 | 14 | 0,571429 | 0,326531 | 0,326531 | 8,9e−16 |
| 7 | Or-opt | 360 | 63 | 0,404762 | 0,165533 | 0,163832 | 5,0e−16 |
| 8 | 2-opt | 2520 | 20 | 0,650000 | 0,422500 | 0,422500 | 8,9e−16 |
| 8 | Or-opt | 2520 | 108 | 0,507407 | 0,259551 | 0,257462 | 6,7e−16 |
| 9 | 2-opt | 20160 | 27 | 0,703704 | 0,495199 | 0,495199 | 3,7e−15 |
| 9 | Or-opt | 20160 | 165 | 0,579798 | 0,337570 | 0,336166 | 6,7e−16 |

- **2-opt:** ρ(1) = 1 − 2(n−1)/(n(n−3)), also 1/5, 4/9, 4/7, 13/20, 19/27, und ρ(2) = ρ(1)² in jeder Instanz (Abweichung unter 1e−12).
- **Or-opt:** ebenfalls in jeder Instanz derselbe Wert, aber ρ(2) liegt für n = 6 bis 9 um 0,0014 bis 0,0026 über ρ(1)²: diese Wanderung fällt nicht wie eine Potenz.
- **Or-opt (mehr Nachbarn) hat ein kleineres ρ(1) als 2-opt:** n = 9: 0,7037 bei 27 Nachbarn (2-opt), 0,5798 bei 165 (Or-opt). Belegt ist der Vergleich dieser zwei Nachbarschaften; Zahl der Nachbarn und Art des Zuges sind dabei nicht getrennt. Die Zahl hängt an der Nachbarschaft.
- **Gegenprobe:** Mit dem Quadrat der Tourlänge als Landschaft (n = 8, 2-opt) unterscheiden sich die Instanzen: Spanne 0,0067 bis 0,0069 über je 150 Instanzen. Das ist ein einzelnes Gegenbeispiel mit kleiner Spanne; dass die Gleichheit an der Tourlänge als Summe von Kanten hängt, folgt aus der Skizze der Herleitung (nicht bewiesen), nicht aus dieser Messung.

### Rundtour per Wanderung (2-opt, nicht aufgezählt)

| n | Familie | L | Messreihe | Mittel von ρ̂(1) über 10 Wanderungen | Formel | Abstand in Standardfehlern |
|---|---|---|---|---|---|---|
| 9 | gleichverteilt | 20000 | A | 0,70421 | 0,70370 | 0,3 |
| 9 | gleichverteilt | 20000 | B | 0,70374 | 0,70370 | 0,0 |
| 30 | gleichverteilt | 100000 | A | 0,92873 | 0,92840 | 0,8 |
| 30 | gleichverteilt | 100000 | B | 0,92786 | 0,92840 | 1,2 |
| 30 | geclustert | 100000 | A | 0,92801 | 0,92840 | 0,9 |
| 30 | geclustert | 100000 | B | 0,92760 | 0,92840 | 1,8 |
| 100 | gleichverteilt | 200000 | A | 0,97957 | 0,97959 | 0,2 |
| 100 | gleichverteilt | 200000 | B | 0,97928 | 0,97959 | 2,2 |

Alle 8 Zeilen liegen höchstens 2,2 Standardfehler vom Wert der Formel. Die Korrelationslänge der Formel ist 2,8 / 13,5 / 48,5 / 98,5 Schritte für n = 9 / 30 / 100 / 200, also etwa n/2 für große n (für n = 9 nur 2,8 gegen 4,5).

Güte der Schätzung auf der Rundtour (gleichverteilte Familie, zweimal 20 Instanzen × 10 Wanderungen je Zelle):

| n | L | Bias | SD innerhalb einer Instanz | Anteil mit Fehler über 0,1 | Median τ̂/τ |
|---|---|---|---|---|---|
| 30 | 100 | −0,0457 bis −0,0424 | 0,0520 bis 0,0549 | 10,5 bis 16,0 % | 0,62 bis 0,65 |
| 30 | 1000 | −0,0037 bis −0,0035 | 0,0119 bis 0,0129 | 0,0 % | 0,97 |
| 30 | 10000 | −0,0003 | 0,0035 bis 0,0036 | 0,0 % | 1,00 |
| 100 | 100 | −0,0512 bis −0,0488 | 0,0427 bis 0,0431 | 10,0 bis 13,0 % | 0,31 |
| 100 | 1000 | −0,0047 bis −0,0040 | 0,0078 bis 0,0079 | 0,0 % | 0,84 bis 0,86 |
| 100 | 10000 | −0,0008 bis −0,0004 | 0,0021 | 0,0 % | 0,98 |

Bei n = 100 und L = 1000 ist der Median von τ̂/τ 0,84 bis 0,86, bei L = 10000 0,98: Auch L = 1000, rund das 20-Fache von τ ≈ n/2, schätzt τ im Median noch 14 bis 16 % zu niedrig; die Wanderung muss deutlich länger sein als τ.

### Zahl → Test

| Zahl oder Aussage | Test | Art |
|---|---|---|
| Handbeispiele: 1/2, 1/4, 1/32; 2/3 und 1/3 (56 von 64); 1/9; 5/19; −5/8 und −5/16; 1/5, 4/9, 19/27; drei verschiedene Werte der Gegenprobe | `tests/test_handbeispiele.py` | exakt (Brüche, Demo auf 1e−12) |
| Tabellen dieser README | `tests/test_claims.py::test_tabellen_der_readme_stammen_aus_der_messung` | wortgleich aus `lsm_messung.json` |
| Zahlen im Fließtext dieser README | `tests/test_claims.py` (je Aussage ein Test) | aus `lsm_messung.json` abgeleitet |
| `lsm_messung.json` selbst, Teile: K = 0 und K = 4 exakt, Rundtour n = 5 bis 7, eine Zelle des Schätzers | `tests/test_messung.py` | neu gerechnet, Gleitkomma relativ 1e−9, Schätzer als Band |
| `lsm_messung.json` vollständig | `python tools/lsm_make_messung.py --check` | Messung dieser README, nicht in der Testsuite (etwa 2 Minuten) |
| Zahlen der Spalte „Vormessung“ und die Gegenprobe 130 / 777 gegen 170 / 892 | – | Angaben der Planung bzw. einmalige Messung beim Bau (als Größenordnung), nicht im Test |
| Rechenzeiten (1,4 Sekunden, 40 Sekunden) | – | einmalige Messung auf dem Baurechner, nicht im Test |

## Ehrliche Grenzen

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

Weitere Grenzen:

- Die eingefrorene Messung hat N = 16; für N = 14 und N = 18 ist nichts gemessen. Alle Aussagen gelten für gleichverteilte Beiträge und zyklisch benachbarte Gene.
- „Glatt“ und „rau“ in der App sind Wörter mit festen Schwellen (ab 0,5 bzw. unter 0,1), keine Fachbegriffe mit eigener Aussage.
- Die Streuung zwischen Instanzen ist aus 30 Landschaften je Zelle geschätzt und selbst unsicher; deshalb stehen zwei Messreihen nebeneinander.

## 🚧 Bewusst nicht enthalten / nicht gemessen

- **Weitere Nachbarschaften der Rundtour** (3-opt, Vereinigungen) und eine Formel für Or-opt in n.
- **Gerichtete Touren** (asymmetrische Abstände) und ein Beweis der Formel für 2-opt; die Begründung im 📐-Expander ist eine Skizze.
- **N = 14 und N = 18** sowie Schrittabstände über 5 in der eingefrorenen Messung.
- **Rauigkeit, die nicht über alle Zustände mittelt** (zum Beispiel nur entlang von Abstiegen oder nur über gute Touren); dafür kann die Gleichheit auf der Rundtour fallen.
- **Schätzer aus Abstiegsbahnen** statt aus Zufallswanderungen.
- **Andere Anordnungsaufgaben:** Die Vormessung fand für eine quadratische Zuordnung mit sechs Bauteilen eine von der Instanz abhängige Rauigkeit; das wurde im Bau nicht wiederholt und ist hier nicht belegt.
- **Die Gegenprobe „längste Kante der Tour“** und die Nachrechnung einer älteren Messreihe der Planung (Zusammenhang der Schätzung mit n) wurden nicht nachgebaut.
- **PDF-Export.**

## Tests

**303 Tests** (`pytest --collect-only -q tests`), Laufzeit lokal rund 140 Sekunden mit zwei Prozessen (eine Messung unter Last, nicht im Test). Keine Mutationstests.

| Datei | Tests | Inhalt |
|---|---|---|
| `tests/test_handbeispiele.py` | 16 | Handbeispiele als exakte Tests: Sollwert als Bruch auf eigenem Rechenweg, Demo auf 1e−12 |
| `tests/test_oracle_landschaft_messen.py` | 58 | Orakel: Matrixpotenz der Übergangsmatrix, Direktberechnung je Zustand, Schleife über alle Zustände, Kantenmengen, Or-opt in Knotensprache, Bellman-Held-Karp, Wanderung gegen exakt (Band von 4 Standardfehlern) |
| `tests/test_eigenschaften.py` | 84 | Eigenschaften (Skalieren, Umbenennen, Spiegeln, K = 0, 2-opt je Instanz) und Randfälle (konstante Landschaft, N = 1, n = 4, L = 2, Pendeln, ungültige Eingaben) |
| `tests/test_zaehlung.py` | 5 | Zähltest: Auswertungen der Wanderung und der Aufzählung gegen die Handzählung |
| `tests/test_basis.py`, `tests/test_rng.py` | 21 | Kopie-Test der gemeinsamen Basis gegen `tests/data/basis_eingefroren.json`, blockweiser Zufallsstrom gegen die skalare Vorlage |
| `tests/test_messung.py` | 17 | eingefrorene Messung in Teilen neu gerechnet |
| `tests/test_claims.py` | 19 | Zahlen und Tabellen dieser README gegen die Messung, Testzahl, Pflichtabschnitte |
| `tests/test_verdicts.py` | 19 | jede Schwelle und jede Zahl der Verdikt-Texte an handgesetzten Werten |
| `tests/test_app_demo.py`, `tests/test_app.py` | 17 | AppTest: je Preset die erwarteten Verdikt-Zeilen, Schalter, Ränder, jeder Button, jeder Regler am Minimum und Maximum |
| `tests/test_layout.py`, `tests/test_presets.py` | 37 | Schnellstart in der Seitenleiste, fester Kopf, Hervorhebung, Permalink (Begrenzen, Einrasten), K höchstens N − 1 |
| `tests/test_footer.py`, `tests/test_runtime_imports.py`, `tests/test_modul_frisch.py` | 10 | Footer, Laufzeit-Importe, Neuladen der Hilfsmodule |

Im Browser sind die Abbildungen und der feste Kopf nicht durch Tests gedeckt (AppTest sieht nur die Daten der Abbildungen).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App (Aufbau nach DEMO-PLAYBOOK §2) |
| `lsm_basis.py` | unveränderte Kopie der gemeinsamen Basis der Reihe (Instanzfamilien, Seeds, NK-Tabellen, Zählregeln) |
| `lsm_rng.py` | unveränderte Kopie des SplitMix64-Generators |
| `lsm_rngblock.py` | derselbe Zufallsstrom blockweise mit numpy |
| `lsm_nk.py` | NK-Modell: alle Zustände, exakte Autokorrelation, lokale Optima, die zwei Formeln |
| `lsm_route.py` | Rundtour: Aufzählung, Zugtabellen für 2-opt und Or-opt, exakte Autokorrelation |
| `lsm_walk.py` | Zufallswanderungen und Schätzer |
| `lsm_scenario.py` | Instanzen (Basisfamilien und die nicht-euklidische Zufallsmatrix) |
| `lsm_evaluation.py` | Auswertungen der Experimente, Tabellen, Verdikte als reine Funktionen |
| `lsm_messung.json` | eingefrorene Messung (Quelle und Stand je Teil) |
| `lsm_constants.py`, `lsm_presets.py`, `lsm_layout.py`, `lsm_texts.py`, `lsm_visualization.py` | Regler-Grenzen und Presets, Permalink, fester Kopf, feste Texte, Abbildungen |
| `modul_frisch.py` | lädt geänderte Hilfsmodule nach einem Update neu |
| `tools/lsm_make_messung.py` | erzeugt und prüft `lsm_messung.json` |
| `tests/` | siehe Abschnitt „Tests“ |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
