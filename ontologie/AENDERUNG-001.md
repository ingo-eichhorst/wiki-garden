# Änderung 001: Barrieren gezielt auffindbar machen

Status: **für die Demo simuliert übernommen**. Die fachliche Entscheidung des Teams steht aus.

## Auslöser

Der Leitfaden [[wiki/quellen/Q04|Q04]] nennt Anpassungen für Videokonferenzen. Die neue Kompetenzfrage [[COMPETENCY-QUESTIONS#KF06|KF06]] fragt nach der Zuordnung von Maßnahmen zu Barrieren.

## Modelllücke

Das Modell 1.0.0 kennt Maßnahmen und Kontexte. Es kennt keine typisierte Zuordnung zwischen einer Maßnahme und einem konkreten Hindernis. Das Programm zeigt diese Lücke im [[demo/ABGEWIESEN|abgewiesenen Versuch]].

Die Extraktion enthält den Vorschlag bereits. Die Ablehnung entsteht deshalb aus der Prüfung gegen das alte Schema. Das Programm entdeckt einen neuen Fachbegriff nicht selbstständig.

## Optionen

| Option                                      | Vorteil                                                     | Nachteil                                                                        |
| ------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Barriere im Freitext behalten               | Kein neues Modell nötig                                     | Keine eindeutige Graphabfrage für KF06                                          |
| Barriere als besonderen Kontext modellieren | Weniger Typen                                               | Anlass und Hindernis bleiben vermischt; eine neue Beziehung wäre trotzdem nötig |
| Typ `Barriere` ergänzen                     | Maßnahmen und Hindernisse werden wiederverwendbar verknüpft | Zusätzlicher Typ und zusätzliche Pflege                                         |

## Entscheidung für die Vorführung

Die Demo verwendet die dritte Option.

- Neuer Typ: `Barriere`.
- Neue Beziehung: `Massnahme → adressiert → Barriere`.
- Neue Beziehung: `Barriere → tritt_auf_in → Kontext`.
- Erweiterung der Herkunftsbeziehung: Auch Barrieren brauchen Quellen.
- Neue Modellversion: `1.1.0`.

Die beiden Modellversionen liegen vollständig vor. [[demo/ONTOLOGIE.diff|Der Unterschied]] wird beim Demo-Aufruf erzeugt.

## Auswirkungen und Migration

1. Alte Kennungen bleiben gleich.
2. Q01 bis Q03 werden mit dem neuen Schema erneut geprüft.
3. Q04 ergänzt H01, H02, zwei Maßnahmen und E05.
4. E04 bleibt erhalten. Der Eintrag wird durch zusätzliche Bedingungen eingeordnet.
5. KF06 liefert zwei belegte Zuordnungen.
6. Alte Wiki-Stände bleiben unverändert lesbar.

Dies ist eine additive Änderung. Die bisherigen Typen und Beziehungen bleiben zulässig. Es ist keine Umbenennung bestehender Daten nötig.

## Fachlich noch zu entscheiden

- Ist `Barriere` für das Team der passende Begriff?
- Ist die Abgrenzung zu `Kontext` im Alltag verständlich?
- Sind die Quellen hinreichend für die beiden konkreten Zuordnungen?
- Soll das Team künftig `adressiert` nach Planung, Umsetzung und Wirkung unterscheiden?

Die Demo-Freigabe beantwortet diese Fragen nicht. Eine echte Entscheidung erhält Name, Datum und Begründung im Ereignisprotokoll.
