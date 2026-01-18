# MUSIC TRANSFORMATION ENGINE — v2 ROADMAP

**Audience**: Engineering team, product owner, future AI assistants  
**Status**: v1.1 completed, beta-tested with real choral repertoire  
**Primary Users**: Professional choir conductors and arrangers  
**Core Principle**: Deterministic musical correctness + controlled LLM creativity

## 0. Context Recap (Authoritative)

### What Exists (v1.1)

- MusicXML is input/output only, never an internal working format
- Internal model: IKR-light
- Parts, voices, measures, explicit musical events
- LLM interaction via TLR (Textual LLM Representation)
  - One event per line
  - Deterministic, reversible, validated
- LLM (via Ollama) is strictly gated by:
  - System Prompt (compiler-like behavior)
  - User Prompt with explicit transformation flags
- Supported transformations:
  - Transposition
  - Rhythm simplification
  - Style change (bounded)
  - Harmonic reharmonization (explicit HARMONY events)
- Gradio UI with:
  - Upload MusicXML
  - View TLR
  - LLM dialog
  - Download MusicXML
  - Diff view
- Target repertoire: choral music, possibly with accompaniment, no orchestral scores

### Non-Goals (Still)

- No direct MusicXML editing
- No free-form composition
- No layout/engraving optimization
- No audio generation

## 1. v2 Strategic Objective

Move from
"musically correct transformation engine"
to
"musically intelligent assistant for professional choral work"

This requires:
- stronger musical constraints
- richer analytical context
- more predictable stylistic behavior
- continued explainability

## 2. v2 Architecture Principles (Non-Negotiable)

- IKR remains the single source of musical truth
- TLR remains the only LLM interface
- LLM never enforces rules; it proposes changes
- All musical legality is enforced outside the LLM
- Every non-trivial change must be explainable post hoc

## 3. Milestone Overview

| Milestone | Focus | Risk Level |
|-----------|-------|------------|
| v2.1 | Voice-leading & range constraints | Medium |
| v2.2 | Explicit harmonic analysis layer | Medium |
| v2.3 | Style profiles & presets | Medium |
| v2.4 | Ambitus-aware transposition | Low |
| v2.5 | Large-score scalability | Medium |
| v2.6 | Professional UX refinements | Low |

## 4. v2.1 — Voice Leading & Vocal Constraints

### Goal

Prevent musically unacceptable results for real singers.

### Features

- Per-voice ambitus constraints
  - e.g. Soprano: C4–A5
- Optional tessitura preferences
- Voice-crossing detection
- Leap-size constraints (configurable)

### Technical Tasks

- Extend IKR:
  - Add voice_constraints metadata
- Add validation pass:
  - Reject illegal LLM outputs
- Add explanation hooks:
  - "Change rejected due to Alto range violation"

### Definition of Done

- No generated output exceeds defined voice ranges
- Clear error messages for rejected transformations

## 5. v2.2 — Harmonic Analysis Layer (Explicit)

### Goal

Separate what the harmony is from how notes realize it.

### Features

- Optional automatic harmonic analysis:
  - Roman numerals
  - Key context per segment
- Harmony stored as first-class IKR objects
- LLM may:
  - Modify harmony symbols
  - But must respect analysis structure

### Technical Tasks

- Extend IKR:
  - HarmonySegment
- TLR extension:
  - Explicit harmonic regions
- Validator:
  - Check consistency between harmony and pitches

### Definition of Done

- Harmonic changes are always explicit, inspectable, and reversible

## 6. v2.3 — Style Profiles & Presets

### Goal

Replace vague "style change" with bounded, reproducible stylistic behavior.

### Features

- Named style profiles:
  - "Renaissance polyphonic"
  - "Bach chorale"
  - "Romantic homophonic"
- Each profile defines:
  - Allowed harmonic vocabulary
  - Preferred textures
  - Rhythm density limits

### Technical Tasks

- Style profile schema (YAML/JSON)
- Prompt augmentation based on profile
- Validation rules per style

### Definition of Done

- Same input + same style profile ⇒ same structural outcome
- Style changes are musically plausible to professionals

## 7. v2.4 — Ambitus-Aware Transposition

### Goal

Make transposition musically usable, not just mathematically correct.

### Features

- Automatic transposition limit detection
- Warnings instead of silent failure
- Optional octave displacement rules

### Technical Tasks

- Preflight analysis on IKR
- Constraint-aware transposition logic
- UI feedback ("Best achievable transposition: +2 semitones")

### Definition of Done

- No unusable transpositions for choirs

## 8. v2.5 — Large-Score Scalability

### Goal

Support full-length works without context collapse.

### Features

- Score chunking at phrase/section boundaries
- Deterministic reassembly
- Consistent harmony and style across chunks

### Technical Tasks

- Chunking algorithm based on IKR
- Context propagation between chunks
- Regression tests for long works

### Definition of Done

- Works >1000 measures process reliably

## 9. v2.6 — Professional UX Refinements

### Goal

Reduce cognitive load for expert users.

### Features

- Measure/voice-level navigation
- Selective transformation scope:
  - "Apply only to measures 12–24"
- Transformation preview / dry run

### Technical Tasks

- UI state management
- Partial IKR → TLR pipelines
- Scoped validation

### Definition of Done

- Users feel "in control", not "at the mercy of the AI"

## 10. Explicit Non-Goals for v2

- Automatic composition from scratch
- Audio synthesis
- Graphical engraving optimization
- Real-time performance tools

## 11. Success Metric for v2

A professional choir conductor can:
- trust the output without fear of hidden errors
- understand why changes happened
- reuse the tool in real rehearsal preparation

If that is not true, v2 is not complete.

## 12. Future v3 Teasers (Out of Scope)

- Counterpoint rule engines
- Pedagogical feedback mode
- Comparative style analysis
- Assisted reduction (full score → choir score)

---

**End of v2 Roadmap**

If you want, the next logical artifacts would be:
- a v2 IKR schema draft
- a style profile specification
- or a risk register identifying the hardest musical problems first