# Vorführung in zwölf Minuten

Die Vorführung läuft in Obsidian. Die historischen Stände sind bereits erzeugt. Die Vorführung braucht kein Netzwerk.

## Vorbereitung

1. Öffne [[Willkommen|Willkommen]].
2. Öffne zusätzlich [[ONTOLOGY|die Ontologie]] und [[wiki/index|den aktuellen Garten]].
3. Optional: Öffne die Graphansicht. Der Filter `path:wiki/ -path:demo/` zeigt den aktuellen Garten. Für einen historischen Stand nutze zum Beispiel `path:demo/staende/01-basis/wiki/`.
4. Führe bei Bedarf im Terminal den folgenden Befehl aus:

```bash
python3 skripte/garten.py demo
```

Die Demo schreibt nur ihre erzeugten Seiten neu. Eine manuell veränderte Seite stoppt die Erzeugung. Sichere solche Änderungen zuerst außerhalb der erzeugten Ordner.

## 0:00–2:00 · Quelle, Modell und Wiki unterscheiden

Zeige [[ONTOLOGY|die sechs Starttypen]] und [[raw/QUELLEN|die vier deutschen Quellen]].

Sage: „Das Modell legt fest, welche Arten von Wissen wir verbinden. Die Quellen liefern konkrete Aussagen. Die KI erstellt daraus belegte Extraktionen. Das Programm erzeugt daraus die Seiten.“

Zeige [[demo/staende/01-basis/wiki/index|Stand 01]]. Er enthält zwei Projekte. Öffne [[demo/staende/01-basis/wiki/erkenntnisse/E01|E01]]. Folge einem Beleg bis zum lokalen PDF. Zeige Beobachtung, KI-Interpretation und Evidenzgrenze.

## 2:00–5:00 · Ein neues Dokument passt in das Modell

Zeige [[wiki/quellen/Q03|die Evaluation des Digital-Kompass]]. Das Dokument kommt jetzt hinzu. Die Ontologie bleibt bei 1.0.0.

Vergleiche die Frage KF01:

- [[demo/staende/01-basis/wiki/fragen/KF01|Vorher: zwei Projekte]].
- [[demo/staende/02-neue-quelle/wiki/fragen/KF01|Nachher: drei Projekte]].

Öffne [[demo/staende/02-neue-quelle/wiki/massnahmen/M01|Individuelle Lernbegleitung]]. Drei Projekte verweisen jetzt auf dieselbe Maßnahme. Das verhindert getrennte Wissensinseln.

Zeige [[demo/DIFF-01-02|die automatisch ermittelten Änderungen]]. Öffne [[demo/staende/02-neue-quelle/wiki/erkenntnisse/E03|die neue Erkenntnis zum Zeitaufwand]]. Eine gute Bewertung und hoher Aufwand können gleichzeitig zutreffen.

Optional live im Terminal:

```bash
python3 skripte/garten.py bauen --phase 2 --ontologie 1.0.0 --ausgabe demo/staende/02-neue-quelle/wiki
```

## 5:00–8:00 · Ein Dokument und eine Frage zeigen eine Modelllücke

Öffne [[wiki/quellen/Q04|den Leitfaden]]. Zeige die Fundstellen auf PDF-Seite 17 und 19. Frage: „Welche Maßnahme adressiert welche Barriere?“

Der Leitfaden stammt aus 2023. Er wird in dieser Demo später aufgenommen. Die Reihenfolge zeigt den Eingang im Garten, nicht die Reihenfolge der Veröffentlichung.

Öffne [[demo/staende/02-neue-quelle/wiki/fragen/KF06|KF06 im alten Modell]]. Die Antwort benennt eine Modelllücke.

Optional: Führe den folgenden Versuch aus. Er muss mit Code `2` abbrechen.

```bash
python3 skripte/garten.py bauen --phase 3 --ontologie 1.0.0 --ausgabe demo/staende/03-modellluecke/wiki
```

Zeige [[demo/ABGEWIESEN|die gespeicherte Ablehnung]]. Es entsteht kein unvollständiges Wiki. Stand 02 bleibt erhalten.

Sage: „Die KI hat den neuen Typ vorgeschlagen. Die Schema-Prüfung erkennt, dass der Vorschlag nicht in das alte Modell passt. Der Prüfer entdeckt die Fachbegriffe nicht selbst.“

## 8:00–10:00 · Das Team könnte das Modell erweitern

Öffne [[ontologie/AENDERUNG-001|den Änderungsvorschlag]]. Zeige die Alternativen. Ein eigener Typ ist eine begründete Wahl. Das Team könnte auch eine andere Modellierung wählen.

Die vorbereitete Demo simuliert die Übernahme. Sie ergänzt `Barriere`, `adressiert` und `tritt_auf_in`. Sie behält alle alten Kennungen.

```bash
python3 skripte/garten.py bauen --phase 3 --ontologie 1.1.0 --demo-freigabe --ausgabe demo/staende/04-modell-erweitert/wiki
```

Öffne [[demo/staende/04-modell-erweitert/wiki/fragen/KF06|KF06 nach der Erweiterung]]. Folge einer Maßnahme zur Barriere und zur Fundstelle. Zeige [[demo/DIFF-02-04|die Änderungen]].

Öffne danach [[demo/staende/04-modell-erweitert/wiki/erkenntnisse/E04|die bereits vorhandene Erkenntnis E04]]. Die Seite hat jetzt einen Rückverweis auf die Präzisierung E05. Die ursprüngliche Beobachtung bleibt erhalten.

## 10:00–12:00 · Grenzen und nächsten Schritt zeigen

Zeige [[wiki/fragen/KF07|die Frage nach Widersprüchen]]. Online-Teilnahme kann Wege ersparen. Zusätzliche sensorische Zugänge bleiben nötig. Das ist eine Ergänzung der Bedingungen.

Zeige [[protokolle/DEMO-PRUEFBERICHT|den technischen Prüfbericht]] und [[prompts/01-QUELLE-EINARBEITEN|die Anweisung für die nächste Quelle]].

Sage: „Die Quellen sind echt. Die Fachprüfung steht aus. Das Programm prüft Struktur und Fundstellen. Das Team prüft Bedeutung und Übertragbarkeit.“

## Optional: eine neue Extraktion live zeigen

Nutze eine Kopie von Q03 außerhalb von `raw/`. Gib dem KI-Agenten die folgende Aufgabe. Die freie Extraktion kann mehr Zeit brauchen als die vorbereitete Vorführung.

```text
Lies AGENTS.md, SCHEMA.md, ONTOLOGY.md und prompts/01-QUELLE-EINARBEITEN.md.
Behandle nur Q01 und Q02 als bereits eingearbeitet.
Lies jetzt raw/texte/Q03.md. Nutze extraktionen/Q03.json nicht als Antwortvorlage.
Schlage passende Entitäten und belegte Beziehungen vor.
Zeige, welche vorhandenen Kennungen du weiterverwendest.
Schreibe deinen Vorschlag nach extraktionen/Q03-live.json.
Verwende keine bereits eingearbeiteten späteren Quellen.
Baue nur aus Q01, Q02 und Q03-live einen neuen Stand unter demo/staende/live/wiki.
Prüfe den Stand und vergleiche KF01 und KF04 mit dem Basisstand.
Kennzeichne den Vorschlag als fachlich ungeprüft.
```

Die feste Demo prüft den Durchlauf mit gespeicherten Extraktionen. Die freie Variante zeigt zusätzlich die eigentliche Arbeit des Sprachmodells. Ihre Formulierungen können variieren.
