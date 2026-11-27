# Knowledge Garden für die Sozialwirtschaft

Dieses Repository ist ein Obsidian-Vault. Es zeigt, wie eine kleine Ontologie und echte Dokumente ein vernetztes Wiki ergeben. Eine **Ontologie** legt hier die Typen und Beziehungen des Wissens fest. Das Modell ist ein leichtgewichtiges Fachmodell. Es enthält keine OWL-Logik.

Alle Erläuterungen und alle vier Projektquellen sind deutsch. Obsidian benötigt keine zusätzlichen Erweiterungen.

## Sofort ansehen

Öffne diesen Ordner in Obsidian. Öffne [[Willkommen|Willkommen]] und dann [[demo/ABLAUF|den Demo-Ablauf]]. Die erzeugten Seiten und alle drei Wiki-Stände sind bereits vorhanden.

## Demo erneut ausführen

Voraussetzung: Python 3.10 oder neuer. Wechsle im Terminal in diesen Ordner.

```bash
python3 skripte/garten.py demo
python3 skripte/garten.py pruefen --alle-links
python3 -m unittest discover -s tests -v
```

Die Demo benötigt weder Netzwerk noch API-Schlüssel. Sie liest die lokal gesicherten Quellen und die bereits erstellten KI-Extraktionen. Sie verändert keine Originalquelle. Sie bricht ab, wenn jemand eine erzeugte Seite manuell verändert hat.

Ergebnisse dieses Aufbaus: [[protokolle/DEMO-PRUEFBERICHT|Prüfbericht der Demo]] und [[protokolle/TESTBERICHT|Bericht der 17 automatisierten Tests]].

**Was macht die KI?** In dieser Einrichtung hat der KI-Agent die Quellen gelesen, Aussagen extrahiert und das Modell sowie den Änderungsvorschlag ausgearbeitet. Neue Dokumente verarbeitet ein KI-Agent mit [[prompts/01-QUELLE-EINARBEITEN|dieser Arbeitsanweisung]].

**Was macht Python?** Das Programm prüft die gespeicherten Extraktionen. Es verbindet gleiche Kennungen. Es erzeugt Markdown-Seiten und führt feste Graphabfragen aus. Ein erneuter Demo-Aufruf wiederholt diese Verarbeitung. Er führt keine neue Sprachmodell-Extraktion aus.

## Vier Schritte vorführen

| Stand | Quellen | Modell | Einstieg |
|---|---|---|---|
| 01 · Basis | Q01 und Q02 | 1.0.0 | [[demo/staende/01-basis/wiki/index|Erster Garten]] |
| 02 · Neue Quelle | zusätzlich Q03 | unverändert 1.0.0 | [[demo/staende/02-neue-quelle/wiki/index|Erweiterter Garten]] |
| 03 · Modelllücke | Versuch mit Q04 | 1.0.0 reicht nicht | [[demo/ABGEWIESEN|Tatsächliche Ablehnung]] |
| 04 · Modell erweitert | zusätzlich Q04 | 1.1.0, Demo-Freigabe | [[demo/staende/04-modell-erweitert/wiki/index|Garten mit Barrieren]] |

Der Ordner `wiki/` zeigt den vollständigen letzten Stand. Historische Stände bleiben in eigenen Ordnern. Die Vorführung muss daher keine Dateien zurücksetzen.

## Ordner

| Pfad | Inhalt | Pflege |
|---|---|---|
| `raw/originale/` | Drei PDFs und eine gesicherte Webseite | Originale nicht ändern |
| `raw/manifest.json` | Herkunft, Abrufdatum und SHA-256-Prüfsummen | Neue Quellen anhängen |
| `raw/texte/` | Gesicherte Lesetexte mit PDF-Seiten | Aus Originalen abgeleitet |
| `ontologie/` | Zwei Modellversionen, Fragen und Änderungsvorschlag | Bewusste Modellentscheidung |
| `extraktionen/` | Aussagen, Belege, Entitäten und Beziehungen | KI erstellt; Team prüft |
| `wiki/` | Erzeugte Seiten, Quellenverweise und Fragen | Über Extraktionen neu erzeugen |
| `demo/` | Ablauf, historische Stände und Unterschiede | Reproduzierbar erzeugt |
| `prompts/` | Arbeitsanweisungen für den KI-Agenten | Gemeinsam pflegen |
| `vorlagen/` | Vorlage für Extraktionen und Erfahrungsinterviews | Für weitere Quellen |
| `protokolle/` | Ereignisse, technische Prüfberichte und offene Arbeit | Tatsächliche Arbeit dokumentieren |

## Feste Fragen ausprobieren

```bash
python3 skripte/garten.py fragen KF01 --wiki demo/staende/01-basis/wiki
python3 skripte/garten.py fragen KF01 --wiki demo/staende/02-neue-quelle/wiki
python3 skripte/garten.py fragen KF06 --wiki demo/staende/02-neue-quelle/wiki
python3 skripte/garten.py fragen KF06
```

Der dritte Aufruf endet absichtlich mit Code `2`: Das Modell unterstützt die Frage noch nicht. Der vierte Aufruf zeigt zwei Zuordnungen mit Belegen. Freie Fragen verarbeitet der KI-Agent nach [[prompts/02-FRAGE-BEANTWORTEN|dem Frage-Prompt]].

## Weitere Quelle einarbeiten

1. Sichere eine geeignete Datei außerhalb der Originalsammlung.
2. Registriere die Datei mit dem folgenden Befehl. Ersetze die Beispielwerte durch die wirklichen Angaben.
3. Lass den KI-Agenten eine Extraktion erstellen. Nutze [[prompts/01-QUELLE-EINARBEITEN|den Einarbeitungs-Prompt]].
4. Prüfe die Ausgabe und die Änderungen. Nutze einen neuen Stand für die erste Erzeugung.

```bash
python3 skripte/garten.py registrieren --id Q05 --datei /pfad/bericht.pdf --url https://herausgeber.example/bericht --titel "Titel des Berichts" --herausgeber "Herausgeber" --jahr 2026
python3 skripte/garten.py bauen --ontologie 1.1.0 --demo-freigabe --pakete extraktionen/Q01.json extraktionen/Q02.json extraktionen/Q03.json extraktionen/Q04.json extraktionen/Q05.json --ausgabe demo/staende/05-weitere-quelle/wiki
python3 skripte/garten.py pruefen --wiki demo/staende/05-weitere-quelle/wiki
```

Neue PDFs benötigen zur Textextraktion `pdftotext` aus Poppler. Unter macOS kann Poppler mit `brew install poppler` installiert werden. Die vorhandene Demo benötigt Poppler nicht mehr. UTF-8-Text und HTML mit einem `main`-Element funktionieren ohne weitere Programme. Bildscans benötigen vorher Texterkennung.

`--demo-freigabe` bestätigt ausschließlich die vorbereitete Modellentscheidung. Die Option ersetzt keine Fachprüfung. Ein neues produktives Modell erhält eine eigene Version und eine dokumentierte Teamentscheidung.

## Grenzen und Weiterarbeit

- Öffentliche Berichte erschließen dokumentiertes Wissen. Sie ersetzen keine Gespräche mit Projektbeteiligten. Die [[vorlagen/ERFAHRUNGSINTERVIEW|Interviewvorlage]] bereitet diesen Schritt vor.
- Die technische Prüfung findet fehlende Belege, fehlerhafte Fundstellen und unzulässige Beziehungen. Ein gefundener Suchtext beweist noch nicht die Aussage.
- Die Fachprüfung aller Erkenntnisse und beider Modelle steht aus. Zuständigkeiten stehen in [[METHODIK|Methode und Rollen]].
- Die Erzeugung schützt manuell veränderte Dateien. Eigene ergänzende Notizen gehören in einen anderen Ordner.
- Die Fremdquellen behalten ihre Rechte. Eine spätere Veröffentlichung muss die Rechte der Originale gesondert beachten. Siehe [[raw/QUELLEN|Quellenübersicht]].

Das Verzeichnis enthielt zu Beginn keine Git-Historie. Modellversionen, Unterschiede und Ereignisse liegen deshalb als Dateien vor. Ein Team kann diese Dateien zusätzlich mit Git verwalten.
