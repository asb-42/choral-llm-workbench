# Choral Music Workbench

**Semantic choral music transformation and analysis system** built on MusicXML, TLR, and LLM technology.  
Designed for professional choir conductors, arrangers, composers, and music educators.

This tool provides complete end-to-end music transformation workflow with semantic analysis:

## 🎯 Core Features

### 1. Music Transformation Pipeline
- **Upload & Parse**: Load MusicXML files and convert to TLR (Textual LLM Representation)
- **AI-Powered Transformations**: Transpose, rhythm simplification, style changes, harmonic reharmonization
- **Semantic Analysis**: Deep musical diff analysis showing exactly what changed between original and transformed scores
- **Export Capability**: Convert transformed music back to MusicXML for download

### 2. Transformation Types
- **Transpose**: Change pitch by specified intervals while preserving harmonic structure
- **Rhythm Simplification**: Reduce complexity while maintaining musical essence  
- **Style Adaptation**: Apply stylistic changes (e.g., classical → contemporary)
- **Harmonic Reharmonization**: Generate new harmonic progressions while preserving melodic lines

### 3. Semantic Diff System
- **Note-Level Analysis**: Track individual pitch, duration, and rhythm changes
- **Structure Comparison**: Measure, voice, and part-level transformations
- **Visual Feedback**: Color-coded HTML interface showing all musical modifications
- **Explainable Changes**: Each transformation is traceable and musically justified

### 4. Professional Workflow Features
- **TLR Format**: Human-readable text representation for AI processing
- **Validation Layer**: Ensure musical correctness and structural integrity
- **Roundtrip Compatibility**: Maintain MusicXML fidelity throughout the pipeline
- **CPU-Optimized**: Fast inference using optimized models (qwen2:1.5b default)

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.11+ 
- **RAM**: 4GB+ minimum, 8GB+ recommended
- **Ollama**: Local LLM server (recommended)

### Installation
```bash
# Clone repository
git clone <repository_url>
cd choral-llm-workbench

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install dependencies  
pip install -r requirements.txt

# Set up Ollama (recommended)
ollama pull qwen2:1.5b  # Fast CPU model
ollama serve
```

### Launch Application
```bash
# Start the web interface
python app.py

# Open browser: http://localhost:7861
```

## 📖 System Architecture

### Core Components
- **app.py**: Main application and Gradio web interface
- **ikr_light.py**: Internal musical knowledge representation
- **tlr_converter.py**: MusicXML ↔ TLR conversion
- **semantic_diff_analyzer.py**: Musical change analysis engine
- **ollama_llm.py**: LLM interface for transformations
- **musicxml_exporter.py**: Export functionality

### Data Flow
1. **Input**: MusicXML file upload
2. **Parse**: Convert to IKR (musical objects)
3. **Transform**: LLM processes TLR with constraints
4. **Validate**: Ensure musical correctness
5. **Analyze**: Generate semantic diff between scores
6. **Display**: Present changes in intuitive web interface
7. **Export**: Transform back to MusicXML for download

## 🔧 Configuration

### Model Configuration
```python
# Default fast CPU model
DEFAULT_MODEL = "qwen2:1.5b"

# Timeout settings (seconds)
LLM_TIMEOUT = 180
```

### Supported Models
- **qwen2:1.5b**: Fast CPU inference (default)
- **mistral:latest**: Higher quality, slower CPU inference  
- **llama3:latest**: Advanced reasoning capabilities

## 📊 Performance Notes

### CPU Performance
- **qwen2:1.5b**: ~20-30 seconds for simple transformations
- **Larger models**: 2-5 minutes, may timeout on slower systems

### Memory Usage
- **Base application**: ~200MB RAM
- **LLM inference**: +1-4GB depending on model size

## 🧪 Testing

### Test Scripts
```bash
# Test complete pipeline
python tests/test_fixed_pipeline.py

# Debug specific components
python tests/debug_semantic_diff.py
python tests/debug_export.py
```

### Validation
- Roundtrip MusicXML conversion
- Musical structure preservation  
- TLR format compliance
- Semantic diff accuracy

## 📁 Directory Structure

```
choral-llm-workbench/
├── app.py                          # Main application
├── ikr_light.py                     # Musical representation
├── tlr_converter.py                 # Format conversion
├── semantic_diff_analyzer.py         # Change analysis
├── semantic_diff_ui.py              # UI for diffs
├── ollama_llm.py                   # LLM interface
├── musicxml_exporter.py             # Export functionality
├── transformation_validator.py         # Transformation rules
├── tlr_parser.py                    # TLR parsing
├── tests/                           # Test suite
├── requirements.txt                  # Dependencies
└── README.md                        # This file
```

## 🎯 Use Cases

### For Choir Conductors
- Transpose pieces for different vocal ranges
- Simplify rhythms for amateur singers
- Generate alternative harmonizations

### For Music Educators  
- Create teaching examples with different difficulty levels
- Demonstrate musical transformations
- Analyze structural changes

### For Composers & Arrangers
- Rapid prototyping of variations
- Style transfer applications
- Harmonic exploration tools

## 🔍 Recent Updates (v2.2+)

### ✅ Fixed Issues
- **LLM Timeout**: Switched to fast qwen2:1.5b model for CPU inference
- **Semantic Diff Display**: Fixed score tracking and UI rendering
- **Export Functionality**: Resolved TLR parsing and file export issues
- **Measure Validation**: Improved boundary checking for note durations

### 🚀 Performance Improvements
- Reduced transformation time from 600s+ to 20-30s
- Improved semantic diff accuracy and completeness
- Enhanced error handling and user feedback
- Optimized memory usage for large scores

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request with description

## 📜 License

MIT License - see LICENSE file for details.

---

**Note**: This system is actively developed. For the latest features and documentation, check the repository regularly.
