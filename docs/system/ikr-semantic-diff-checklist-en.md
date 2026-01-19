# IKR Semantic Diff – Implementation Checklist

## A. General Rules (mandatory)

☐ Diff works exclusively on IKR objects
☐ No access to MusicXML in diff
☐ No textual comparison (diff, difflib, etc.)
☐ Diff is deterministic (same inputs → same output)
☐ Output is sorted (Score → Part → Voice → Measure → Event)
☐ Each diff line is musically explainable (no technical terms)

## B. Score Level (mandatory, v1)

☐ Key / Tonality
- changed (e.g. C major → D major)
- implicitly created by transposition

☐ Global Meter / Time Signature
- change of time signature
- switch between even / odd meters

☐ Global Tempo (if modeled)
- numerical change
- relative change ("slightly faster", if allowed)

☐ Style / Style Tag
- e.g. "Renaissance → Romantic"
- only report if explicitly changed

## C. Part / Voice Level (mandatory, v1)

☐ Voice Structure
- new voice added
- voice removed
- voices merged / split

☐ Instrument / Role
- e.g. "Alto → Tenor"
- accompaniment voice added

☐ Transposition
- absolute semitone number
- direction explicit ("+2 semitones")

## D. Measure Level (mandatory, v1)

☐ Bar Boundaries
- bar added / removed
- bar count changed

☐ Time Signature within the work
- change within a voice
- e.g. 3/4 → 4/4

☐ Polyrhythm
- explicitly mark when voices keep different meters

## E. Rhythm Level (mandatory, v1 – very important)

☐ Note Duration
- e.g. ♪♪ → ♩
- triplets → binary
- dotting removed / added

☐ Rhythmic Simplification
- only report if explicitly requested
- formulation: "Rhythm simplified: complex subdivision → regular pattern"

☐ Rhythmic Thickening
- e.g. ♩ → ♪♪

## F. Pitch / Melody Level (mandatory, v1)

☐ Individual Pitch
- absolute change
- relative change (interval)

☐ Melodic Contour
- only report if consciously changed
- no report for pure transposition

☐ Leaps vs. Steps
- larger leaps introduced / reduced (optionally mark)

## G. Harmony Level (mandatory, v1 – if present)

☐ Harmonic Events
- chord function changed
- new chords introduced

☐ Reharmonization
- explicitly identify
- e.g. "Harmony reharmonized: diatonic → secondary dominants"

☐ Chromatic Chords
- only report if newly added

## H. Note-Level Details (optional, v2)

☐ Articulation
☐ Dynamics
☐ Phrasing
☐ Accents
☐ Beaming

➡️ Do not diff in v1, otherwise diff becomes too technical.

## I. Negative Rules (important!)

☐ No diff report when:
- change purely created by rounding / normalization
- MusicXML export/import causes minor structural changes
- order changed without musical meaning

☐ No diff report for:
- layout
- line breaks
- voice order without meaning

## J. Output Quality (UX Criteria)

Each diff line must:
- be understandable to a choir conductor without technical knowledge
- provide musical value
- contain maximum 1 musical concept

❌ Bad:
"Duration changed from 0.5 to 1.0"

✅ Good:
"Rhythm simplified: eighth + eighth → quarter"

## K. Test Cases (mandatory for acceptance)

☐ Pure transposition → only transposition diff
☐ Rhythm simplify → only rhythm diff
☐ Style change → only style diff
☐ Combined transformation → multiple, cleanly separated diff entries
☐ Roundtrip without transformation → no diff

## Final Recommendation

This checklist should:
- be included as docs/IKR_DIFF_CHECKLIST.md in repo
- be updated with each extension of the diff system
- serve as Definition of Done for semantic changes