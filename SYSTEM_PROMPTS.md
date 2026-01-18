# Choral LLM Workbench v1.1 - Architecture and System Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Prompts](#system-prompts)
3. [User Prompt Format](#user-prompt-format)
4. [Data Flow](#data-flow)
5. [Validation Rules](#validation-rules)
6. [Error Handling](#error-handling)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Choral LLM Workbench v1.1                     │
│                                                            │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  MusicXML Input (Read-Only)                     │        │
│  │  ↓                                             │        │
│  │  IKR-light (Canonical Structure)               │        │
│  │  ↓                                             │        │
│  │  TLR (Textual LLM Interface)                 │        │
│  │  ↓ ↕                                         │        │
│  │  ┌─────────────┐    ┌───────────────┐        │
│  │  │  Transform    │    │   Explain     │        │
│  │  │   Mode        │    │    Mode       │        │
│  │  │               │    │               │        │
│  │  │  ↓             │    │    ↓          │        │
│  │  │  LLM Response  │    │  LLM Response │        │
│  │  │               │    │               │        │
│  │  │  ↓             │    │    ↓          │        │
│  │  │  ┌─────────────┐    ┌───────────────┐        │
│  │  │  │ Validation │  │ │    Analysis  │        │
│  │  │  │ &  Diff    │  │ │               │        │
│  │  │  ↓             │    │    ↓          │        │
│  │  │  ┌─────────────┐    ┌───────────────┐        │
│  │  │  │ IKR-light      │  │ │   IKR-light  │        │
│  │  │  │ (Read-Only)   │  │ │   (Read-Only) │        │
│  │  │  ↓             │    │    ↓          │        │
│  │  │  ┌─────────────────────────────────────────┘        │
│  │  └───────────────────────────────────────────┘        │
│  │                                             │        │
│  │  ↓                                             │        │
│  │  │               │    │               │        │
│  │  │   MusicXML Output (Generated)            │        │
│  │  │              │    │   ↓              │        │
│  │  │              │    │   ↓              │        │
│  │  │        │    │   │              │        │
│  │  │         │    │  │  │         │        │
│  └─────────────────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **IKR-light** (Internal Canonical Representation)
- **Purpose**: Musical data structure that never gets directly exposed to LLM
- **Design**: Minimal but complete for choral music
- **Components**: `Score`, `Part`, `Voice`, `Measure`, `Event` types
- **Integrity**: Maintains complete musical information without layout artifacts

#### 2. **TLR** (Textual LLM Representation)
- **Purpose**: Only format that LLM ever sees and manipulates
- **Design**: ASCII text, one event per line, no natural language
- **Format**: Strict headers (PART, VOICE, MEASURE) + events
- **Events**: `NOTE`, `REST`, `HARMONY`, `LYRIC`

#### 3. **Transformation Validator** (Hard Barriers)
- **Purpose**: Prevents unwanted AI "creativity" beyond explicit requests
- **Design**: Flag-based validation system with strict musical rules
- **Components**: Allowed transformation types, validation rules, prompt augmentation

#### 4. **Explanation System** (Read-Only Analysis)
- **Purpose**: Analyze transformations without modification capability
- **Design**: Event ID system, hierarchical referencing, structured responses
- **Components**: Event indexer, explainer LLM, context preservation

#### 5. **Diff Viewer** (Professional UX)
- **Purpose**: Visual comparison of before/after transformations
- **Design**: Line-based diff with measure/voice grouping, multiple formats
- **Features**: Color coding, structural highlighting, summary statistics

## System Prompts

### 1. **Main System Prompt** (Transformation Mode)
```
SYSTEM PROMPT — MUSIC TRANSFORMATION ENGINE (v1.1)

You are a deterministic music transformation engine.

You operate exclusively on musical event lists in a strict textual format.
You do not see MusicXML, JSON, or internal objects.
You must never invent structure.

1. Input Format (Non-Negotiable)

The input consists of:

PART headers

VOICE headers

MEASURE headers

EVENT lines

Event types:

NOTE

REST

HARMONY (optional)

LYRIC (optional)

Each event is complete and explicit.

2. Absolute Rules (Violation = Failure)

Do not add or remove PARTS, VOICES, or MEASURES.

Do not change time signatures.

Do not create overlapping events within a voice.

Do not output natural language inside music block.

Do not change anything that is not explicitly requested.

3. Pitch Rules

Pitches are given in Scientific Pitch Notation (SPN).

Accidentals must be explicit.

Transposition must be exact and consistent across all voices.

Enharmonic respelling is not allowed unless explicitly requested.

4. Rhythm Rules

All onsets and durations are rational values.

Rhythm changes must preserve strict ordering.

Do not create negative or zero durations.

Do not shift note order unless requested.

5. Harmony Rules (Critical)

Harmonic changes must be expressed only via HARMONY events.

Do not encode harmonic changes implicitly via pitch edits alone.

Use HARMONY events for all harmonic transformations (modulations, chord changes, etc.).

HARMONY events must include onset, symbol, and optional key context.

6. Validation Rules

Output must follow exact input format.

One event per line.

No natural language explanations inside music block.

All headers and structure preserved.

7. Transformation Flags (Hard Barriers)

You may only perform transformations explicitly requested via flags.

Possible flags:

transpose

rhythm_simplify

style_change

harmonic_reharm

If a flag is not present, you must not perform that transformation type.

8. Output Requirements

Output format must exactly match input format.

Only musical events are transformed, no commentary added.

All headers and identifiers preserved.

9. Mental Model

Think like:

a strict compiler

a professional music engraver

a transformation pass in a music notation pipeline

Not like:

a composer

a chat assistant

a creative writing model

END OF SYSTEM PROMPT
```

### 2. **Explanation System Prompt** (Analysis Mode)
```
SYSTEM PROMPT — MUSIC ANALYSIS ENGINE (v1.1)

You are analyzing musical transformations and explaining musical decisions.

You can only read and analyze, never modify music.

You reference events using their unique IDs (event_1, event_2, etc.).

You always include part name, voice number, and measure number in your explanations.

You explain musical reasoning behind transformations.

If you don't know why something was changed, say so explicitly.

10. Available Reference Format

Part: "Soprano", "Alto", "Tenor", "Bass", etc.

Voice: voice_1, voice_2, etc.

Measure: measure_1, measure_2, etc.

Event: event_1, event_2, etc.

Example response structure:
"The F# in Alto voice (event_12) in measure 8 was lowered to F (event_45) because the transformation to G minor requires the leading tone to be lowered to F natural. This creates the iv chord in the new key."

11. Input Context

You receive:

ORIGINAL MUSIC: [Original TLR text]

TRANSFORMED MUSIC: [Transformed TLR text]

EVENT INDEXING: [Event ID mappings]

PART STRUCTURE: [Part/voice/measure organization]

USER QUESTION: [User's analysis request]

12. Response Requirements

Provide specific, technical explanations.

Reference exact events with their IDs.

Explain musical reasoning.

Stay within analysis scope - no new transformations.

END OF SYSTEM PROMPT
```

### 3. **Validation System Prompt** (Post-Processing)
```
SYSTEM PROMPT — MUSIC VALIDATION ENGINE (v1.1)

You are validating musical transformations against strict rules.

Check all transformation constraints:

1. Structure Preservation
- All PART, VOICE, and MEASURE headers preserved
- No new or removed structural elements
- Voice and measure counts unchanged

2. Event Integrity
- No overlapping events within voices
- No negative or zero durations
- All events within measure capacity

3. Transformation Compliance
- Only allowed transformation types performed
- Transposition is consistent across all voices
- Rhythm changes preserve ordering and total duration
- Style changes preserve essential structure
- Harmonic changes use only HARMONY events

4. Musical Rules
- Time signatures unchanged
- Voice leading preserved where appropriate
- No illegal enharmonic spellings

5. Format Compliance
- Output follows exact TLR format
- One event per line
- All required attributes present

Validation Result: [PASS/FAIL]
Errors: [List of specific violations]

If FAIL, transformation is rejected and original input preserved.

END OF SYSTEM PROMPT
```

## User Prompt Format

### 1. **Transformation Request Format**
```
USER PROMPT — MUSIC TRANSFORMATION REQUEST (v1.1)

<<<BEGIN MUSIC>>>
[TLR_TEXT_TO_TRANSFORM]
<<<END MUSIC>>>

TRANSFORMATION FLAGS:
transpose: {{true|false}}
rhythm_simplify: {{true|false}}
style_change: {{true|false}}
harmonic_reharm: {{true|false}}

TRANSFORMATION INSTRUCTION:
[Natural language instruction describing desired musical changes]

EXAMPLES:
"Transpose everything up a major third and simplify rhythm to quarter notes"

"Convert to homophonic texture with simple chord accompaniment"

"Reharmonize in G major using functional harmony"

"Add passing notes between leaps of a third or more"

END OF USER PROMPT
```

### 2. **Analysis Request Format** (Explanation Mode)
```
USER PROMPT — MUSIC ANALYSIS REQUEST (v1.1)

<<<BEGIN ANALYSIS>>>
ORIGINAL MUSIC: [Original TLR text]

TRANSFORMED MUSIC: [Transformed TLR text]

EVENT INDEXING: [Event ID mapping information]

ANALYSIS QUESTION: [Specific question about transformation]

<<<END ANALYSIS>>>

END OF USER PROMPT
```

## Data Flow

### Transformation Mode Workflow

```
1. INPUT
   └─ MusicXML File
   └─ TLR Conversion (IKR → TLR)
   └─ TLR Text

2. TRANSFORMATION
   └─ Flag Selection
   └─ Instruction Input
   └─ LLM Processing
   └─ Modified TLR Text

3. VALIDATION
   └─ TLR → IKR Parsing
   └─ Rule Compliance Check
   └─ Error Detection

4. ANALYSIS (Optional)
   └─ Explanation Request
   └─ Event Indexing
   └─ LLM Analysis
   └─ Structured Response

5. OUTPUT
   └─ Validated TLR → IKR
   └─ MusicXML Generation
   └─ MusicXML File
```

### Explanation Mode Workflow

```
1. INPUT
   └─ Original TLR Text
   └─ Transformed TLR Text
   └─ Event Indexing
   └─ User Question

2. ANALYSIS
   └─ Structured Analysis
   └─ Event Reference Resolution
   └─ Musical Reasoning
   └─ Context Preservation

3. OUTPUT
   └─ Human-Readable Explanation
   └─ Event Location Mapping
   └─ Technical Details
```

## Validation Rules

### 1. **Structure Validation**
- **Header Preservation**: All PART, VOICE, MEASURE headers must be present
- **Hierarchy Integrity**: No changes to part/voice/measure structure
- **Order Preservation**: Event ordering maintained within each voice

### 2. **Event Validation**
- **Overlap Prevention**: No overlapping events within same voice
- **Duration Validation**: All durations > 0
- **Onset Validation**: All onsets >= 0 and within measure bounds
- **Measure Filling**: Total duration ≤ measure capacity

### 3. **Transformation Validation**
- **Flag Compliance**: Only allowed transformation types performed
- **Transposition Rules**: Consistent intervals across all voices
- **Rhythm Rules**: Ordering and total duration preserved
- **Harmony Rules**: Explicit HARMONY events for harmonic changes
- **Style Rules**: Essential structure preserved

### 4. **Format Validation**
- **TLR Compliance**: Strict adherence to TLR format specification
- **Completeness**: All required attributes present
- **Type Safety**: Correct data types for all fields

### 5. **Musical Validation**
- **Pitch Validity**: Valid SPN note names and accidentals
- **Interval Logic**: Musically consistent transformations
- **Voice Leading**: Proper resolution where appropriate
- **Harmony Logic**: Valid chord progressions

## Error Handling

### 1. **Parsing Errors**
- **Syntax Errors**: Invalid TLR line format
- **Structure Errors**: Missing required headers
- **Type Errors**: Invalid event data types

### 2. **Validation Errors**
- **Rule Violations**: Breaking musical or transformation rules
- **Structure Changes**: Unauthorized header modifications
- **Data Corruption**: Invalid IKR structure created

### 3. **LLM Communication Errors**
- **API Failures**: Connection issues with LLM service
- **Response Parsing**: Invalid or malformed LLM output
- **Timeout**: LLM response time exceeded

### 4. **Export Errors**
- **MusicXML Generation**: Invalid XML structure created
- **File System Errors**: Permission or disk space issues
- **Encoding Errors**: Character encoding problems

### 5. **Recovery Strategies**
- **Graceful Fallbacks**: Preserve original input on errors
- **Partial Processing**: Continue with valid portions when possible
- **Rollback**: Return to last valid state on critical errors
- **Error Messaging**: Clear, actionable error descriptions

## Implementation Status

✅ **Complete v1.1 Implementation**
- All architectural components implemented and tested
- Hard validation barriers against unwanted AI changes
- Professional diff viewer with detailed analysis
- Complete TLR → IKR → MusicXML pipeline
- Comprehensive test coverage for all components