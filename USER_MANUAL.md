# User Manual - Choral LLM Workbench v1.1

## Table of Contents

1. [Quick Start](#quick-start) - Immediate setup and first transformation
2. [Core Workflow](#core-workflow) - Understanding the transformation process
3. [Transformation Modes](#transformation-modes) - Available transformation types
4. [Notation Systems](#notation-systems) - SPN vs Helmholtz
5. [Analysis Mode](#analysis-mode) - Detailed musical analysis
6. [Diff Viewer](#diff-viewer) - Change comparison
7. [Professional Features](#professional-features) - Advanced capabilities
8. [Troubleshooting](#troubleshooting) - Common issues and solutions

## Quick Start

### System Requirements
- **Python**: 3.11+ with type hints
- **RAM**: 8GB+ recommended for LLM operations
- **Browser**: Modern web browser with HTML5 support
- **Local LLM**: Ollama or compatible service (optional for testing)

### Initial Setup

#### 1. Create and Activate Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Start Local LLM (Recommended)
```bash
ollama serve
```

#### 3. Launch Application
```bash
python app.py
```
Open browser to `http://localhost:7860`

#### 4. First Upload
1. Click "Upload MusicXML"
2. Select a choral score file (.xml, .musicxml)
3. Wait for "Successfully parsed MusicXML file" status

## Core Workflow

### 1. Upload and Parse
1. **Load MusicXML**: Upload your choral score
2. **Automatic Parsing**: System converts to internal IKR format
3. **TLR Display**: Textual representation appears in main area
4. **Validation**: Musical rules applied automatically

### 2. Configure Transformation
1. **Select Flags**: Choose from available transformation types
2. **Provide Instruction**: Give clear musical instruction
3. **Review Constraints**: System validates against rules

#### 3. Transform and Validate
1. **LLM Processing**: AI applies requested transformations
2. **Rule Checking**: System validates against hard barriers
3. **Success Confirmation**: Valid transformation appears as TLR

### 4. Analyze Results
1. **Switch Mode**: Click "Explanation Mode" for analysis
2. **Ask Questions**: Targeted questions about specific changes
3. **Get Answers**: Technical explanations with event references

### 5. Export Results
1. **Choose Format**: MusicXML for professional notation
2. **Download File**: Results saved locally for use in notation software
3. **Archive Versions**: Keep different transformation variants

## Transformation Modes

### Transpose Mode
**Purpose**: Change pitch while preserving musical intervals

**Flags**: `transpose: true`

**Examples**:
- `"Transpose everything up a perfect fifth"`
- `"Transpose down a major third"`
- `"Transpose up a minor third to G major"`

**Rules**:
- Consistent interval across all voices
- Preserve rhythm and structure
- No modal changes unless specifically requested

### Rhythm Simplify Mode
**Purpose**: Simplify rhythmic patterns for readability

**Flags**: `rhythm_simplify: true`

**Examples**:
- `"Simplify rhythm to straight quarters"`
- `"Convert dotted rhythms to straight"`
- `"Make all rhythms equal durations"`

**Rules**:
- Preserve total measure duration
- Preserve note order
- May combine adjacent notes

### Style Change Mode
**Purpose**: Modify musical style while keeping structure

**Flags**: `style_change: true`

**Examples**:
- `"Convert to baroque style"`
- `"Apply classical style voice leading"`
- `"Simplify textures to homophonic"`

**Rules**:
- Preserve voice and measure structure
- May add ornamentation
- Keep harmony accessible

### Harmonic Reharm Mode
**Purpose**: Change harmony while preserving melody

**Flags**: `harmonic_reharm: true`

**Examples**:
- `"Reharmonize in G major"`
- `"Apply functional harmony with dominant preparation"`
- `"Add passing tones between leaps"`

**Rules**:
- Preserve melody notes exactly
- Use explicit HARMONY events
- Maintain voice leading principles

### Combination Strategies

#### Multiple Flags
- `"Transpose + Rhythm Simplify"`: Change pitch and simplify rhythm
- `"Transpose + Harmonic Reharm"`: Transpose and reharmonize
- `"Style Change + Rhythm Simplify"`: Style simplify with rhythm
- `"All Four"`: Maximum transformation control

## Notation Systems

### Scientific Pitch Notation (SPN)
**Format**: C4, D4, E4, F4, etc.

**Use Case**: Modern music software, academic analysis
**Features**:
- Standard in digital music applications
- Precise pitch specification
- Compatible with LLM understanding

### Helmholtz Notation
**Format**: c', c, d, e, f, g, a, b, etc.

**Use Case**: Traditional music publishing, classical scores
**Features**:
- Historical music compatibility
- Vocal range notation
- Professional publishing standards

### Switching
- **UI**: Radio buttons for instant switching
- **Application**: Automatic conversion between systems
- **Preservation**: No data loss during switch

### Examples

#### SPN Display
```
NOTE t=0 dur=1/4 pitch=C4
NOTE t=1/4 dur=1/4 pitch=D4
```

#### Helmholtz Display
```
NOTE t=0 dur=1/4 pitch=c (quarter)
NOTE t=1/4 dur=1/4 pitch=d (quarter)
```

### Voice Range Differences

| Note | SPN | Helmholtz |
|------|------|-----------|
| C4   | C4   | c'        |
| C5   | C5   | c''       |
| B3   | B3   | b,         |
| D4   | D4   | d          |
| F#4   | F#4   | fis'       |
| G4   | G4   | g          |
| A♭4 | A♭4  | a' is'     |
| B♭4 | B♭4  | b'         |
| C5   | C5   | c''       |

## Analysis Mode

### Purpose
Detailed analysis of musical transformations without modification capability

### When to Use
- After complex transformations
- When LLM decisions need explanation
- For educational purposes
- To understand musical reasoning
- For quality assurance

### Working Process

1. **Switch Mode**: Click "Explanation Mode"
2. **Review Changes**: Diff viewer shows all modifications
3. **Ask Questions**: Targeted technical questions
4. **Get Answers**: Structured musical explanations

### Example Questions

#### Technical Questions
```
"Why was the F# in Alto voice measure 12 lowered?"
"What harmonic progression occurs in measures 8-12?"
"Explain the voice leading in the soprano part"
```

#### Contextual Questions
```
"Compare the bass line in measures 1-4 with the new harmonization"
"Analyze the contrapuntal motion in the tenor part"
"Show me the relationship between soprano and bass in the modulation"
```

### Response Structure
- **Event Reference**: "event_12 (Alto, measure 12)"
- **Musical Reasoning**: Technical explanation with terminology
- **Context Inclusion**: Surrounding musical context
- **Clarity**: Professional, technical terminology

## Diff Viewer

### Purpose
Professional comparison tool for detailed change analysis

### Activation
- **Automatic**: Appears after successful transformation
- **Manual**: "Refresh Diff View" button
- **Focused**: Measure-specific analysis available

### Display Options

#### 1. Terminal View
- **Line Numbers**: Each line numbered for reference
- **Color Coding**: Visual distinction of change types
- **Structure Grouping**: Organized by measure and voice
- **Summary Statistics**: Event change counts

#### 2. HTML View
- **Interactive**: Hover effects for detailed inspection
- **Printable**: Professional documentation format
- **Responsive**: Works on all devices

#### 3. Plain Text
- **Unix Compatible**: Standard diff format
- **Email Friendly**: Clear text comparison
- **Archive Format**: Version control friendly

### Color Coding
- **Red**: Removed content (lines starting with `-`)
- **Green**: Added content (lines starting with `+`)
- **Yellow**: Modified content (lines with `±`)
- **Blue**: Measure headers
- **Magenta**: Voice headers

### Example Output

```
=== TLR DIFF VIEW ====

🔵 MEASURE 1
  🟣 VOICE 1
🔴- NOTE t=0 dur=1/4 pitch=C4
🟢+ NOTE t=0 dur=1/4 pitch=E4
    NOTE t=1/4 dur=1/4 pitch=D4

🔵 MEASURE 2
  🟣 VOICE 1
    NOTE t=0 dur=1/2 pitch=F4
    NOTE t=1/2 dur=1/2 pitch=G4

=== SUMMARY ===
Added: 1 events | Changed: 1 events
```

### Analysis Benefits

- **Precision**: Locate exact changes at measure/voice level
- **Verification**: Confirm intended transformations occurred
- **Documentation**: Create clear change records
- **Education**: Step-by-step transformation tracking
- **Quality Assurance**: Verify musical integrity

## Professional Features

### Choir Director Workflow
1. **Score Analysis**: Upload and analyze existing harmony
2. **Range Assessment**: Check vocal comfort zones
3. **Transformation Planning**: Select appropriate flags
4. **Iterative Refinement**: Apply multiple transformations step-by-step
5. **Documentation**: Keep record of all editorial decisions

### Arranger Toolkit
1. **Reharmonization Options**: Multiple harmonic approaches
2. **Style Variants**: Baroque, Classical, Modern, Contemporary
3. **Texture Transformation**: SATB → SSAATTB, homophonic, polyphonic
4. **Key Modulation**: Circle of fifths, relative modulations
5. **Voice Distribution**: Rebalance vocal sections

### Musicologist Research
1. **Historical Analysis**: Study transformation techniques
2. **Comparative Analysis**: Multiple edition comparison
3. **Style Evolution**: Track compositional changes over time
4. **Harmonic Language**: Analyze chord progressions and modulation

### Quality Assurance
1. **Roundtrip Testing**: Verify data integrity through complete pipeline
2. **Validation Testing**: Ensure all musical rules are followed
3. **Error Recovery**: Graceful handling of invalid inputs
4. **Performance Testing**: Test with various scores and LLM models

### Educational Applications
1. **Teaching Examples**: Demonstrate musical concepts clearly
2. **Student Analysis**: Show transformation impact
3. **Assignment Creation**: Generate exercises with known solutions
4. **Answer Keys**: Provide reference for student work

## Troubleshooting

### Common Issues

#### Upload Problems
- **Invalid Format**: Ensure file is valid MusicXML
- **Large Files**: Consider processing time for complex scores
- **Encoding Issues**: Check file encoding (should be UTF-8)

#### LLM Connection
- **Service Status**: Check Ollama is running: `ollama ps`
- **Model Availability**: Verify model is downloaded: `ollama list`
- **Network Issues**: Check firewall and port blocking

#### Validation Errors
- **Rule Violations**: Check transformation flags and instructions
- **Musical Invalidity**: Verify note ranges and durations
- **Structure Changes**: Ensure headers are preserved

#### Export Problems
- **Permission Errors**: Check write permissions in output directory
- **File Size**: Check available disk space
- **XML Validation**: Ensure output can be re-parsed

#### Performance Issues
- **Large Scores**: Process in chunks if memory issues occur
- **Slow LLM**: Use faster models or reduce context
- **Browser Issues**: Try different browser or clear cache

### Debug Mode
- **Enable Logging**: Use verbose mode for detailed error information
- **Test with Simple**: Start with basic scores first
- **Check Logs**: Review application logs for clues
- **Isolate Issues**: Test components separately

### Getting Help

- **Documentation**: Review this manual thoroughly
- **Community**: Check GitHub Issues and Discussions
- **Examples**: Try provided example files first
- **Forums**: Ask questions in relevant music communities

---

**Choral LLM Workbench v1.1** - Professional musical transformation tool for modern choir directors and arrangers.