# IKR Semantic Diff – Implementierungs-Checkliste

## A. Allgemeine Regeln (verbindlich)

☐ Diff arbeitet ausschließlich auf IKR-Objekten
☐ Kein Zugriff auf MusicXML im Diff
☐ Kein textueller Vergleich (diff, difflib, etc.)
☐ Diff ist deterministisch (gleiche Inputs → gleiche Ausgabe)
☐ Ausgabe ist sortiert (Score → Part → Voice → Measure → Event)
☐ Jede Diff-Zeile ist musikalisch erklärbar (keine technischen Begriffe)

## B. Score-Ebene (Pflicht, v1)

☐ Key / Tonart
- geändert (z.B. C major → D major)
- implizit durch Transposition entstanden

☐ Global Meter / Time Signature
- Änderung der Taktart
- Wechsel zwischen geraden / ungeraden Metren

☐ Global Tempo (falls modelliert)
- numerische Änderung
- relative Änderung („slightly faster“, falls erlaubt)

☐ Style / Stil-Tag
- z.B. „Renaissance → Romantic"
- nur melden, wenn explizit verändert

## C. Part / Voice-Ebene (Pflicht, v1)

☐ Voice-Struktur
- neue Stimme hinzugefügt
- Stimme entfernt
- Stimmen zusammengelegt / aufgeteilt

☐ Instrument / Role
- z.B. „Alto → Tenor"
- Begleitstimme hinzugefügt

☐ Transposition
- absolute Halbtonzahl
- Richtung explizit („+2 semitones")

## D. Measure-Ebene (Pflicht, v1)

☐ Taktgrenzen
- Takt hinzugefügt / entfernt
- Taktanzahl verändert

☐ Taktart innerhalb des Werks
- Wechsel innerhalb einer Stimme
- z.B. 3/4 → 4/4

☐ Polyrhythmik
- explizit markieren, wenn Stimmen unterschiedliche Metren behalten

## E. Rhythmus-Ebene (Pflicht, v1 – sehr wichtig)

☐ Notendauer
- z.B. ♪♪ → ♩
- Triole → binär
- Punktierung entfernt / hinzugefügt

☐ Rhythmische Vereinfachung
- nur melden, wenn explizit angefordert
- Formulierung: "Rhythm simplified: complex subdivision → regular pattern"

☐ Rhythmische Verdichtung
- z.B. ♩ → ♪♪

## F. Pitch / Melody-Ebene (Pflicht, v1)

☐ Einzeltonhöhe
- absolute Änderung
- relative Änderung (Intervall)

☐ Melodische Kontur
- nur melden, wenn bewusst verändert
- keine Meldung bei reiner Transposition

☐ Leaps vs. Steps
- größere Sprünge eingeführt / reduziert (optional markieren)

## G. Harmonik-Ebene (Pflicht, v1 – falls vorhanden)

☐ Harmonische Ereignisse
- Akkordfunktion geändert
- neue Akkorde eingeführt

☐ Reharmonisation
- explizit kennzeichnen
- z.B. "Harmony reharmonized: diatonic → secondary dominants"

☐ Tonartfremde Akkorde
- nur melden, wenn neu hinzugefügt

## H. Note-Level Details (Optional, v2)

☐ Artikulation
☐ Dynamik
☐ Phrasierung
☐ Akzente
☐ Beaming

➡️ Nicht in v1 diffen, sonst wird der Diff zu technisch.

## I. Negative Regeln (wichtig!)

☐ Keine Diff-Meldung, wenn:
- Änderung rein durch Rundung / Normalisierung entsteht
- MusicXML-Export/Import leichte Strukturänderungen verursacht
- Reihenfolge ohne musikalische Bedeutung geändert wurde

☐ Keine Diff-Meldung für:
- Layout
- Zeilenumbrüche
- Stimmen-Reihenfolge ohne Bedeutung

## J. Output-Qualität (UX-Kriterien)

Jede Diff-Zeile muss:
- für einen Chorleiter ohne Technikkenntnisse verständlich sein
- einen musikalischen Mehrwert liefern
- maximal 1 musikalisches Konzept enthalten

❌ Schlecht:
„Duration changed from 0.5 to 1.0"

✅ Gut:
„Rhythm simplified: eighth + eighth → quarter"

## K. Testfälle (Pflicht für Abnahme)

☐ Reine Transposition → nur Transpositions-Diff
☐ Rhythm Simplify → nur Rhythm-Diff
☐ Style Change → nur Style-Diff
☐ Kombinierte Transformation → mehrere, sauber getrennte Diff-Einträge
☐ Roundtrip ohne Transformation → kein Diff

## Abschließende Empfehlung

Diese Checkliste sollte:
- als docs/IKR_DIFF_CHECKLIST.md ins Repo
- bei jeder Erweiterung des Diff-Systems aktualisiert werden
- als Definition of Done für semantische Änderungen gelten