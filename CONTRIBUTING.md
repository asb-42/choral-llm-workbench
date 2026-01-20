CONTRIBUTING.md — Semantic Diff & Test Discipline

Purpose of This Document

This project relies on a Semantic Diff system for musical scores based on an internal IKR representation.
Correctness is defined musically, not syntactically.

The accompanying test suite is therefore not optional.
It is the formal specification of what the system is allowed to output.

Any contribution that affects musical analysis, transformation, or description must comply with the rules below.



Core Principle

  If the Semantic Diff tests fail, the implementation is incorrect.

This applies regardless of:

* how plausible the output looks,
* whether the UI appears correct,
* or whether an LLM generated the code.



Scope of the Semantic Diff Test Suite

The Semantic Diff test suite validates:

* musical correctness of detected changes
* score-level analysis (key, meter, tempo, global transformations)
* voice-level grouping (e.g. transposition, rhythm simplification)
* event-level language (intervals, note values)
* transformation summaries
* deterministic and stable output

The tests explicitly do not cover:

* UI layout (Gradio)
* visual styling
* XML formatting
* MusicXML layout or engraving details



Required Workflow for Contributions

1. Create a Dedicated Branch

All changes must be developed on a feature or fix branch.

Example:

  git checkout -b diff-score-key-analysis

2. Identify the Relevant Checklist Item

Each change should correspond to exactly one item in the
IKR Semantic Diff – Implementation Checklist.

Examples:

* “Detect score-level key changes”
* “Group pitch changes into transpositions”
* “Use musical language for durations”

Avoid implementing multiple checklist items in one step.

3. Write or Enable a Test First

Before changing implementation code:

* ensure a corresponding test exists under
  tests/semantic_diff/
* or add a new test that expresses the expected behavior

Tests must:

* be deterministic
* avoid snapshots of full outputs
* assert semantic meaning, not internal structures

4. Implement the Minimal Required Logic

Implementation should:

* satisfy the failing test(s)
* avoid introducing unrelated behavior
* not “fix” other tests unless explicitly intended

Do not refactor aggressively while implementing a checklist item.

5. Run the Full Test Suite

Before committing:

  pytest


or, at minimum:

  pytest tests/semantic_diff/

All tests must pass.

6. Commit with a Semantic Message

Commit messages should clearly reference the checklist intent.

Examples:

  Add score-level key change detection to semantic diff

  Improve musical language for note duration changes

Avoid vague messages like “fix diff” or “cleanup”.



Determinism Requirement

Semantic Diff output must be deterministic.

Given identical inputs:

* output text
* ordering
* grouping

must be identical across runs.

Non-deterministic behavior is considered a bug, even if rare.



Language and UX Rules

Semantic Diff output must:

* use musical terminology, not technical terms
  (e.g. “Quarter note” instead of “0.25 duration”)
* express pitch changes as intervals where possible
* describe one musical concept per line
* avoid leaking internal representations (IKR, XML, floats)

These rules are enforced by tests.



Relationship to LLM-Generated Code

LLMs may be used to generate code, but:

* generated code is subject to the same rules
* failing tests must be fixed manually or via further prompting
* “the model produced it” is not an acceptable justification

The test suite exists precisely to constrain generative behavior.



When in Doubt

If a change feels musically ambiguous:

* prefer explicit tests over implicit assumptions
* discuss the expected behavior in the test description
* keep the implementation conservative

The test suite is the single source of truth.



Summary

* The Semantic Diff tests define correctness.
* Contributions are scoped to checklist items.
* Determinism and musical language are mandatory.
* Tests are not documentation — they are specification.


Where this file belongs

📌 This section should be committed to the repository root as CONTRIBUTING.md.

That way:

* external contributors see it immediately
* LLMs working in the repo implicitly “learn the rules”
* future you doesn’t have to re-explain the architecture


======================================================================================


1. Zweck der Testsuite

Die Testsuite ist kein Selbstzweck. Sie erfüllt bei euch vier sehr konkrete Funktionen:

a) Definition von „musikalisch korrekt“

-> Die Tests sind die formale Spezifikation der IKR Semantic Diff

b) Regression Guard

-> Jede Änderung an Diff-Logik, IKR oder LLM-Output wird sofort überprüft

c) Arbeitsvertrag mit LLMs

-> Opencode / Qwen / GLM dürfen nur das verändern, was Tests erlauben

d) Objektiver Fortschrittsmesser

-> „30 % erfüllt“ → „65 % erfüllt“ ist messbar

Man kann sagen:

Die Testsuite ersetzt implizites musikalisches Wissen durch explizite Regeln.


2. Wann wird die Testsuite ausgeführt?

A. Während der Entwicklung (lokal)

Das ist der Hauptanwendungsfall.

Im Projekt-Root:

  $ pytest

oder gezielt:

  $ pytest tests/semantic_diff/

oder noch gezielter:

  $ pytest tests/semantic_diff/score_level/


➡️ Typischer Workflow:

* Neuen Branch anlegen
* Test(s) schreiben oder aktivieren
* Test schlägt fehl (rot)
* Code ändern
* Test wird grün
* Commit


B. Nach jeder inhaltlichen Änderung an:

* IKR-Strukturen
* Semantic Diff Logik
* musikalischer Sprachgenerierung
* Gruppierungslogik
* Score-Level-Analyse

➡️ Faustregel:

Wenn sich der Text des Diffs ändern könnte, Tests laufen lassen.


3. Wie liest man ein fehlgeschlagenes Testergebnis?

Beispiel:

  FAILED test_score_key_change.py::test_key_change_detected
  AssertionError: 'Key changed: C major → D major' not found in diff


Das bedeutet nicht:

  „Test kaputt“

Sondern:

  IKR Diff erfüllt die Spezifikation noch nicht

Die Testsuite sagt:

  „Du behauptest, Key Changes zu unterstützen – zeig es mir.“


4. Wie wird die Testsuite zur Checkliste?

Der zentrale Mechanismus

Wir haben:

  test_checklist_coverage.py


Dieser Test:

* listet alle IKR Semantic Diff Checklist-Punkte
* mappt sie auf konkrete Tests
* schlägt fehl, wenn:
** ein Punkt keinen Test hat
** ein Test deaktiviert ist

➡️ Ergebnis:

  pytest
  ====================
  IKR Semantic Diff Coverage: 9 / 28 checks passed
  ====================

Das ist Gold für Planung & Priorisierung.


5. Wie nutzt man die Testsuite mit Opencode konkret?

A. Für Opencode / LLMs

Du gibst Opencode immer nur ein Ziel, z. B.:

  „Mache test_score_meter_change.py grün.
  Ändere keinen anderen Test.“

Opencode:

* arbeitet
* führt Tests aus
* commitet

Wenn es „verhakt“:

* Aufgabe zu groß
* weiter aufsplitten


B. Für Entwickler/Architekt

Du nutzt die Testsuite für:

* Scope-Kontrolle
* LLM-Disziplin
* Vermeidung von Feature Drift

Beispiel:

  „Wir implementieren heute keine Style Changes – Test bleibt rot.“

Das ist eine bewusste Entscheidung, kein Bug.


6. Testsuite ≠ UI-Tests

Wichtig, um Missverständnisse zu vermeiden:

Die Testsuite prüft nicht:

* Gradio-UI
* Farben
* Collapse/Expand
* visuelle Darstellung

Sie prüft ausschließlich:

* IKR → Semantic Diff → Text

➡️ UI darf kaputtgehen, ohne dass Tests rot werden
➡️ Semantik darf nicht kaputtgehen, ohne dass Tests rot werden

Das ist genau die richtige Trennung.


7. Typischer Tagesablauf (realistisch)

Ein typischer Entwicklungszyklus:

  a) git checkout -b diff-key-analysis

  b) pytest tests/semantic_diff/score_level/test_score_key_change.py

    → rot

  c) IKR-Diff-Code anpassen

  d) pytest

    → grün

  e) git commit -m "Add score-level key change detection"

  f) nächster Checklist-Punkt


8. Wann läuft die Testsuite nicht?

Bewusst nicht bei:

* reinem UI-Refactoring
* CSS-Anpassungen
* Gradio-Layout
* README-Änderungen

Aber immer, wenn:

* Musik analysiert
* beschrieben
* zusammengefasst wird


9. Wichtigster mentale Shift

Wenn du dir eine Sache merken willst:

  Die Testsuite ist die musikalische Verfassung des Systems.
  Code, der sie verletzt, ist per Definition falsch – egal wie „plausibel“ er wirkt.
