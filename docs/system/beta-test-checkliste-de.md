# BETA-TEST-CHECKLISTE — CHORMUSIK TRANSFORMATION ENGINE (v1.1)

## Ziel der Beta

Validierung, dass das System:

- musikalisch korrekt arbeitet,
- für professionelle Chorleiter/Arrangeure vertrauenswürdig ist,
- deterministisch und erklärbar transformiert.

## 1. Testmaterial (Pflicht)

### 1.1 Repertoire-Mix

Mindestens:

- 1× Renaissance (z. B. Palestrina, Lassus)
- 1× Barock (z. B. Bach-Choralsatz)
- 1× Romantik (z. B. Mendelssohn)
- 1× Zeitgenössisch (20./21. Jh., aber tonal)
- 1× mit Begleitinstrument (Orgel/Klavier)

### 1.2 Technische Vielfalt

Mindestens ein Werk mit:

- ungeradem Metrum (5/8, 7/8)
- Auftakt
- geteilten Stimmen (S1/S2)
- durchgehenden Lyrics
- Fermaten oder langen Haltenoten

## 2. Baseline-Tests (ohne Transformation)

### 2.1 Roundtrip-Test

**Aktion:**
MusicXML → System → MusicXML (ohne LLM-Transformation)

**Erwartung:**

- Keine Notenänderung
- Keine Rhythmusänderung
- Stimmenanzahl identisch
- Taktstruktur identisch

**Abbruchkriterium:**
Eine einzige musikalische Abweichung.

### 2.2 Anzeige-Konsistenz

**Aktion:**
Vergleich:

- Originalnotation
- SPN-Anzeige
- Helmholtz-Anzeige

**Erwartung:**

- Pitch-Identität
- Oktavlagen korrekt
- Keine enharmonischen Überraschungen

## 3. Transpositionstests

### 3.1 Global

**Aktion:**
Transposition aller Stimmen ±2, ±3, ±5 Halbtöne

**Prüfen:**

- Alle Stimmen identisch transponiert
- Ambitus sinnvoll (keine Extremfehler)
- Keine Rhythmusänderung

### 3.2 Stimmenbezogen (negativ)

**Aktion:**
Versuch, nur einzelne Stimmen zu transponieren (nicht erlaubt)

**Erwartung:**
System verweigert oder ignoriert Anfrage.

## 4. Rhythmische Transformationen

### 4.1 Vereinfachung

**Aktion:**
`rhythm_simplify = true`

**Prüfen:**

- Taktlängen exakt erhalten
- Notenreihenfolge unverändert
- Keine Stimmen-Overlaps
- Polyphonie bleibt verständlich

### 4.2 Polyrhythmik

**Aktion:**
Vereinfachung bei gleichzeitig unterschiedlichen Stimmenrhythmen

**Erwartung:**

- Stimmen bleiben unabhängig
- Keine rhythmische „Nivellierung“

## 5. Harmonische Transformationen

### 5.1 Explizite Harmonieänderung

**Aktion:**
`harmonic_reharm = true`

**Prüfen:**

- Harmonieänderungen ausschließlich über HARMONY-Events
- Pitch-Änderungen harmonisch erklärbar
- Keine versteckten Modulationen

### 5.2 Negativtest

**Aktion:**
Harmonieänderung anfordern, aber `harmonic_reharm = false`

**Erwartung:**
Keine Harmonieänderung.

## 6. Stilistische Transformationen

### 6.1 Stiltreue

**Aktion:**
`style_change = true`
z. B. „romantic homophonic“

**Prüfen:**

- Stimmenzahl unverändert
- Metrum unverändert
- Keine „kompositorischen Gags"
- Ergebnis plausibel für Chorleiter

### 6.2 Grenzen

**Aktion:**
Stilwechsel + zusätzliche nicht erlaubte Wünsche

**Erwartung:**
System ignoriert oder verweigert unzulässige Änderungen.

## 7. Erklärender Dialog

### 7.1 Nachvollziehbarkeit

**Aktion:**
Fragen wie:

- „Warum wurde im Alt Takt 12 das Gis zu G?"
- „Welche Harmonie liegt hier vor?“

**Erwartung:**

Antwort referenziert:

- Part
- Voice
- Measure

Keine schwammigen Aussagen, keine kreative Rechtfertigung

## 8. Diff-Analyse (UX-Test)

**Aktion:**
Vergleich Vorher/Nachher (TLR)

**Prüfen:**

- Änderungen klar sichtbar
- Änderungen auf Takt/Voice-Ebene lokalisierbar
- Keine „versteckten" Modifikationen

## 9. Robustheit & Fehlertoleranz

### 9.1 Ungültige LLM-Ausgabe

**Aktion:**
Provozierte Regelverletzung (z. B. negative Dauer)

**Erwartung:**

- Transformation wird verworfen
- Original bleibt erhalten
- Klare Fehlermeldung

### 9.2 Große Werke

**Aktion:**
Mehrseitiger Chorsatz (>300 Takte)

**Prüfen:**

- Performance akzeptabel
- Kein Abbruch
- Kein Kontextverlust

## 10. Abnahmekriterien (Go / No-Go)

**GO, wenn:**

- Kein einziger musikalischer Fehler
- Chorleiter versteht alle Änderungen
- Vertrauen in Wiederholbarkeit

**NO-GO, wenn:**

- Ungefragte Änderungen
- Nicht erklärbare Harmonik
- Instabile Wiederholungsergebnisse

## 11. Abschlussfrage an Beta-Tester (entscheidend)

„Würdest du dieses Werkzeug bei einer realen Proben- oder Arrangiersituation einsetzen?“

Alles unter einem klaren „Ja" ist kein Release.