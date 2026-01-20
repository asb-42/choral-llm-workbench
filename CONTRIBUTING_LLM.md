CONTRIBUTING_LLM.md — Instructions for LLM Agents

Role and Scope

* You are acting as a code contributor to this repository.

* Your task is not to invent new features or improve perceived quality.
* Your task is to make specific tests pass according to an existing specification.


Single-Objective Rule

You must work on exactly one objective at a time.

An objective is usually:

* making one failing test pass, or
* implementing one clearly defined checklist item.

Do not:

* implement multiple features at once
* refactor unrelated code
* “clean up” code unless explicitly instructed


Tests Define Correctness

The test suite under tests/semantic_diff/ is the formal specification.

If a test fails:

* the implementation is incorrect

If a test passes:

* the implementation is acceptable, even if it looks simple

You must not weaken, remove, or bypass tests.


Determinism Is Mandatory

Your changes must produce deterministic output.

Given the same inputs:

* output text
* ordering
* grouping

must be identical across runs.

Randomness, unordered iteration, or heuristic variation is not allowed.


Musical Semantics over Technical Detail

All user-visible output must use musical language.

Forbidden in Semantic Diff output:

* floats
* internal identifiers
* XML terminology
* data structure names

Preferred:

* note values (Quarter, Half, Eighth)
* intervals (+2 semitones, octave)
* musical concepts (transposition, meter change)


One Concept per Line

Each line of Semantic Diff output must describe exactly one musical change.

Do not combine:

* pitch + rhythm
* multiple notes
* multiple transformations

If grouping is required, do it explicitly and intentionally.


Minimal Change Principle

When implementing a fix:

* change as little code as possible
* do not reformat unrelated files
* do not reorder logic without necessity

Large diffs are a warning sign.


No Assumptions beyond Tests

Do not assume:

* undocumented musical rules
* hidden requirements
* future features

If something is not covered by tests or instructions:

leave it unchanged


Commit Discipline

When committing:

* commit only changes related to the current objective
* use a clear, semantic commit message

Example:

  Detect score-level key changes in semantic diff


Failure Handling

If you cannot complete the task because:

* context is insufficient
* behavior is ambiguous
* multiple interpretations exist

Stop and report the uncertainty instead of guessing.


Summary for LLMs

* Tests are the authority.
* One objective at a time.
* Musical meaning > technical cleverness.
* Deterministic, minimal, explicit.


--

To Opencode & other coding agents:

* “Follow CONTRIBUTING_LLM.md strictly.
* Objective: make test_score_key_change.py pass.
* Do not modify unrelated tests.”

