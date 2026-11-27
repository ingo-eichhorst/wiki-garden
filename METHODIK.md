# Methode und Rollen

Der Garten verbindet konkrete Erfahrungen, kleine Modellschritte und gemeinsame Fachentscheidungen. Die folgende Kombination ist eine Anpassung für diesen Hackathon. Sie ist keine vollständig umgesetzte formale Ontologiemethode.

## Arbeitszyklus

1. **Fragen festlegen.** Das Team formuliert fünf bis zehn Fragen für ein Nachfolgeprojekt.
2. **Erfahrung sichern.** Das Team liest Berichte und führt kurze Erfahrungsinterviews. Die [[vorlagen/ERFAHRUNGSINTERVIEW|Interviewvorlage]] nutzt einen strukturierten Rückblick.
3. **Ein kleines Modell bilden.** Das Team definiert wenige Typen und Beziehungen. Beispiele zeigen, wo die Grenzen liegen.
4. **Eine Quelle einarbeiten.** Die KI schlägt Entitäten, Beziehungen und Erkenntnisse vor. Die KI nennt Quellen und Unsicherheit.
5. **Fragen testen.** Das Programm prüft Struktur und Fundstellen. Das Team prüft Bedeutung und Übertragbarkeit.
6. **Gemeinsam entscheiden.** Das Team diskutiert strittige Aussagen und Modelllücken. Erst danach übernimmt es eine produktive Modelländerung.
7. **Pflegen.** Neue Quellen, neue Fragen und neue Erfahrungen starten den nächsten Zyklus.

## Bezug zu den Methoden

| Ansatz | Verwendung im Garten | Grenze der Anpassung |
|---|---|---|
| After Action Review | Geplanter und tatsächlicher Verlauf, Gründe und nächste Schritte | In dieser Demo wurden keine Interviews durchgeführt. |
| Ontology Development 101 | Domäne, Begriffe, Typen, Beziehungen und Beispiele | Das Ergebnis ist ein kleines Fachmodell ohne formalen Reasoner. |
| SAMOD | Kleine Schritte und Tests gegen konkrete Fragen | Keine vollständige SAMOD-Umsetzung mit OWL-Testfällen. |
| HCOME | Fachleute handeln Bedeutung und Modelländerungen aus | Die echte Teamdiskussion steht noch aus. |
| Karpathys LLM Wiki | Originalquellen, KI-gepflegtes Wiki, Arbeitsregeln sowie Einarbeiten, Fragen und Pflegen | Die Wiederholung nutzt geprüfte Datenpakete und keinen eingebauten Sprachmodell-Dienst. |

SAMOD verbindet kleine Modellschritte mit Beispielen und Tests. HCOME bezieht die Wissensgemeinschaft in die laufende Ontologieentwicklung ein. Das sind die beiden wichtigsten methodischen Bezugspunkte für diesen Ablauf. [SAMOD: Originalprojekt von Silvio Peroni](https://github.com/essepuntato/samod), [HCOME: Originalpublikation](https://link.springer.com/article/10.1007/s10115-005-0227-4).

Karpathys Original beschreibt das Arbeitsmuster aus Quellen, Wiki und Agentenregeln. [LLM Wiki: Original von Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Die übrigen Grundlagen sind der iterative Modellierungsleitfaden von Noy und McGuinness sowie der strukturierte Rückblick der WHO. [Ontology Development 101](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf), [WHO: After Action Review](https://www.who.int/emergencies/operations/emergency-response-reviews/after-action-review).

## Rollen im Team

| Perspektive | Aufgabe | Ergebnis |
|---|---|---|
| NGO/NPO | Erfahrungen, Bedingungen und Übertragbarkeit prüfen | Fachliche Einordnung |
| GenAI | Extraktionsanweisungen verbessern; Fehler untersuchen | Belegbare Vorschläge |
| Open Source | Dateien, Prüfungen und Änderungen nachvollziehbar halten | Portabler Arbeitsablauf |
| BWL | Aufwand, Nutzen und Verantwortung für die Pflege klären | Tragfähiger Betrieb |
| Moderation | Kompetenzfragen und Modellentscheidungen moderieren | Dokumentierte gemeinsame Entscheidung |

Die Rollen sind Aufgaben. Sie weisen keiner realen Person ohne Absprache eine Verantwortung zu.

## Vorschlag für sechs Stunden

| Zeit | Arbeit |
|---|---|
| 0:00–0:45 | Fragen und Geltungsbereich festlegen |
| 0:45–1:30 | Zwei Projektgeschichten im Rückblick erfassen |
| 1:30–2:15 | Begriffe und Beispiele gemeinsam definieren |
| 2:15–3:30 | Quellen einzeln einarbeiten und prüfen |
| 3:30–4:30 | Neue Quelle und mögliche Modelllücke bearbeiten |
| 4:30–5:15 | Kompetenzfragen und Übertragbarkeit prüfen |
| 5:15–6:00 | Vorführung üben und Pflege vereinbaren |

## Pflege nach dem Hackathon

- Bei jeder Nutzung: Fehler und fehlende Bedingungen festhalten.
- Bei jeder neuen Quelle: ähnliche Entitäten und abweichende Aussagen suchen.
- Monatlich: offene Fragen, verwaiste Inhalte und Modellvorschläge gemeinsam prüfen.
- Nach einem Projektende: ein Erfahrungsinterview durchführen und die nächsten Schritte einer Person zuordnen.

Die Pflege kann sich später an KCS orientieren. Für diese Demo wird daraus kein zusätzlicher Prozess eingeführt.
