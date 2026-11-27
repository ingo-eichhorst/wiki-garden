# Arbeitsregeln und Dateiformate

Das Schema regelt die Verarbeitung. [[ONTOLOGY|Die Ontologie]] regelt die fachliche Bedeutung.

## Drei Schichten

1. **Quelle:** Das Original bleibt erhalten. `raw/manifest.json` hält die Herkunft und SHA-256 fest. SHA-256 ist eine Prüfsumme zum Erkennen geänderter Dateien.
2. **Wissensbasis:** Eine KI-Extraktion beschreibt belegte Entitäten und Beziehungen. Eine Entität ist ein einzelnes Projekt, eine Maßnahme oder ein anderes benanntes Objekt.
3. **Wiki:** Das Programm erzeugt lesbare Markdown-Seiten. YAML-Frontmatter enthält Typ und Status. Frontmatter sind Metadaten am Dateianfang.

Der KI-Agent übernimmt das Lesen und Einordnen. Das Programm übernimmt wiederholbare Strukturprüfungen und die Seitenerzeugung.

## Extraktion

Eine Datei je Quelle. Die Datei ist JSON. Die [[vorlagen/EXTRAKTION.json|Dateivorlage]] zeigt die Form. Kennungen bleiben stabil. Gleiche Kennungen bezeichnen dieselbe Entität.

| Feld | Bedeutung |
|---|---|
| `quelle` | Registrierte Kennung wie `Q01` |
| `status` | Fachlicher Prüfstatus; zunächst `fachlich-ungeprueft` |
| `belege` | Fundstellen mit lokaler Kennung, Suchtext und vorsichtiger Paraphrase |
| `entitaeten` | Benannte Instanzen eines Ontologietyps |
| `beziehungen` | Gerichtete Verknüpfungen mit benannter Bedeutung und Belegen |

Belegkennungen sind global eindeutig: `Q01:B02`. PDF-Fundstellen nutzen die Dateiseite ab 1. Bei Webseiten werden Abschnitt und Suchtext gespeichert.

Jede Fachentität und jede Beziehung braucht mindestens einen Beleg. Quellenentitäten entstehen aus dem Manifest. Das Programm erzeugt `belegt_durch` aus den Belegen.

## Erkenntnisse

Jede Erkenntnis braucht diese Angaben:

1. Beobachtung oder Empfehlung aus der Quelle.
2. Getrennte Interpretation der KI.
3. Bedingungen für die Übertragung.
4. Grenzen der Evidenz.
5. Offene Frage.
6. Aussageart: `beobachtung`, `empfehlung` oder `hypothese`.
7. Beziehungen zu Projekt, Maßnahme und Kontext.

Eine Interpretation bleibt als Interpretation erkennbar. Eine Empfehlung ist kein Nachweis einer Umsetzung. Eine positive Rückmeldung ist kein allgemeiner kausaler Wirksamkeitsnachweis.

## Gleichheit und Änderungen

- Bei gleicher Kennung vereinigt das Programm die Belege.
- Andere Felder derselben Kennung müssen gleich bleiben. Das verhindert stilles Überschreiben einer Deutung.
- Bei abweichenden Deutungen erstellt der Agent getrennte Erkenntnisse. Das Team entscheidet später über eine Zusammenführung.
- Ein neuer Begriff ist zunächst eine neue Instanz. Ein neuer Typ braucht eine Definition, eine Beziehung und einen Nutzen für eine konkrete Frage.
- Ein neuer Beziehungstyp braucht erlaubte Ausgangs- und Zieltypen.
- Eine Modelländerung erhält eine neue Datei. Alte Modellversionen bleiben erhalten.

## Erzeugen und prüfen

`bauen` prüft Quellen und Extraktionen vor dem Schreiben. Ein unbekannter Typ oder eine unbekannte Beziehung führt zu Code `2`. Das Programm verwirft keine unbekannten Angaben und erzeugt kein halbfertiges Wiki.

`wiki/.generiert.json` enthält Prüfsummen aller erzeugten Dateien. Die erneute Erzeugung schützt veränderte und fremde Dateien. Die historischen Stände verwenden denselben Schutz.

`graph.json` hält auch die Prüfsummen der verwendeten Extraktionen, der Ontologie und der Kompetenzfragen fest. Die Prüfung erkennt damit eine Änderung an den Eingaben nach der letzten Erzeugung.

`pruefen --alle-links` prüft außerdem die Wiki-Links aller Markdown-Dateien außerhalb versteckter Ordner. Das Programm prüft Linkziele und Belegüberschriften. Codebeispiele werden übersprungen.

## Fachprüfung

Technische Konsistenz ist keine fachliche Freigabe. Der Stand `fachlich-geprueft` verlangt eine echte Prüfung mit Name, Datum und Begründung im Ereignisprotokoll. Die vorhandene Demo nutzt diesen Stand nicht.

Ein KI-Agent prüft mögliche Widersprüche nach [[prompts/03-GARTEN-PFLEGEN|dem Pflege-Prompt]]. Das Programm erkennt Widersprüche nicht selbstständig.
