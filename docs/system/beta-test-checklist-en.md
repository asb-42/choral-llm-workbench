# BETA-TEST-CHECKLISTE — CHORAL MUSIC TRANSFORMATION ENGINE (v1.1)

## Objective of the Beta

Validation that the system:

- works musically correctly,
- is trustworthy for professional choir conductors/arrangers,
- transforms deterministically and explainably.

## 1. Test Material (Mandatory)

### 1.1 Repertoire Mix

Minimum of:

- 1× Renaissance (e.g., Palestrina, Lassus)
- 1× Baroque (e.g., Bach chorale)
- 1× Romantic (e.g., Mendelssohn)
- 1× Contemporary (20th/21st century, but tonal)
- 1× with accompaniment instrument (organ/piano)

### 1.2 Technical Diversity

At least one work with:

- irregular meter (5/8, 7/8)
- pickup measure
- divided voices (S1/S2)
- continuous lyrics
- fermatas or long sustained notes

## 2. Baseline Tests (without Transformation)

### 2.1 Roundtrip Test

**Action:**
MusicXML → System → MusicXML (without LLM transformation)

**Expectation:**

- No note changes
- No rhythm changes
- Voice count identical
- Measure structure identical

**Abort criterion:**
A single musical deviation.

### 2.2 Display Consistency

**Action:**
Comparison:

- Original notation
- SPN display
- Helmholtz display

**Expectation:**

- Pitch identity
- Octave positions correct
- No enharmonic surprises

## 3. Transposition Tests

### 3.1 Global

**Action:**
Transposition of all voices ±2, ±3, ±5 semitones

**Check:**

- All voices transposed identically
- Ambitus reasonable (no extreme errors)
- No rhythm changes

### 3.2 Voice-specific (negative)

**Action:**
Attempt to transpose only individual voices (not allowed)

**Expectation:**
System refuses or ignores request.

## 4. Rhythmic Transformations

### 4.1 Simplification

**Action:**
`rhythm_simplify = true`

**Check:**

- Measure lengths exactly preserved
- Note sequence unchanged
- No voice overlaps
- Polyphony remains understandable

### 4.2 Polyrhythm

**Action:**
Simplification with simultaneously different voice rhythms

**Expectation:**

- Voices remain independent
- No rhythmic "leveling"

## 5. Harmonic Transformations

### 5.1 Explicit Harmony Change

**Action:**
`harmonic_reharm = true`

**Check:**

- Harmony changes exclusively via HARMONY events
- Pitch changes harmonically explainable
- No hidden modulations

### 5.2 Negative Test

**Action:**
Request harmony change, but `harmonic_reharm = false`

**Expectation:**
No harmony change.

## 6. Stylistic Transformations

### 6.1 Style Fidelity

**Action:**
`style_change = true`
e.g., "romantic homophonic"

**Check:**

- Voice count unchanged
- Meter unchanged
- No "compositional gags"
- Result plausible for choir conductors

### 6.2 Boundaries

**Action:**
Style change + additional not allowed wishes

**Expectation:**
System ignores or refuses disallowed changes.

## 7. Explanatory Dialogue

### 7.1 Traceability

**Action:**
Questions like:

- "Why was the G# changed to G in measure 12, alto?"
- "What harmony is present here?"

**Expectation:**

Answer references:

- Part
- Voice
- Measure

No vague statements, no creative justification

## 8. Diff Analysis (UX Test)

**Action:**
Before/after comparison (TLR)

**Check:**

- Changes clearly visible
- Changes locatable at measure/voice level
- No "hidden" modifications

## 9. Robustness & Error Tolerance

### 9.1 Invalid LLM Output

**Action:**
Provoked rule violation (e.g., negative duration)

**Expectation:**

- Transformation is discarded
- Original remains preserved
- Clear error message

### 9.2 Large Works

**Action:**
Multi-page choral piece (>300 measures)

**Check:**

- Performance acceptable
- No crashes
- No context loss

## 10. Acceptance Criteria (Go / No-Go)

**GO if:**

- No single musical error
- Choir conductors understand all changes
- Trust in repeatability

**NO-GO if:**

- Unrequested changes
- Unexplainable harmony
- Unstable repetition results

## 11. Final Question for Beta Testers (decisive)

"Would you use this tool in a real rehearsal or arranging situation?"

Everything under a clear "Yes" is no release.