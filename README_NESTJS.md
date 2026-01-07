# Choral LLM Workbench - NestJS + Vue.js Architecture

## 🎯 Project Overview
Professional choral music analysis application with local LLM integration, real-time audio synthesis, and modern web architecture.

## 🏗️ Architecture

### Backend (NestJS)
- **Framework**: NestJS with TypeScript
- **AI Integration**: Local Ollama for music analysis
- **Audio Processing**: Web Audio API + Tone.js
- **MusicXML Parsing**: xml2js with TypeScript support
- **Real-time Features**: WebSockets for live updates
- **API**: RESTful + WebSocket endpoints

### Frontend (Vue.js 3)
- **Framework**: Vue.js 3 + Composition API
- **UI Library**: Element Plus
- **Audio**: Tone.js + Web Audio API
- **State Management**: Pinia
- **Build Tool**: Vite
- **TypeScript**: Full TypeScript support

### Deployment
- **Desktop App**: Pinokio one-click installer
- **PWA Ready**: Progressive Web App support
- **Local First**: No cloud dependencies
- **Cross Platform**: Windows, macOS, Linux

## 🚀 Quick Start

### Prerequisites
```bash
# Node.js (>=18.0.0)
node --version

# Pinokio (for one-click installer)
curl -L https://github.com/pinokio/pinokio/releases/latest/download/pinokio-install.sh | sh

# Ollama (for local LLM)
ollama --version
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd choral-llm-workbench

# Install dependencies
npm install

# Install Pinokio (one-click setup)
npm run install:desktop

# Start development servers
npm run dev          # Start both backend and frontend
npm run dev:backend    # Backend only
npm run dev:frontend   # Frontend only
```

## 🎵 Features

### Core Functionality
- ✅ **Local LLM Integration** - Ollama for music analysis
- ✅ **Real-time Audio Synthesis** - Web Audio API
- ✅ **MusicXML Processing** - Complete parsing and visualization
- ✅ **Voice Separation** - Individual track processing
- ✅ **Configurable Tuning** - 432/440/443 Hz support
- ✅ **Interactive Score** - Real-time cursor and editing
- ✅ **Professional Audio** - Real instruments and effects

### Advanced Features
- 🔄 **Harmonization** - AI-powered voice generation
- 🎼 **Score Editing** - Interactive notation editing
- 🎛️ **Instrument Selection** - Multiple instrument sets
- 🎧 **Audio Effects** - Reverb, chorus, EQ
- 📊 **Analysis Tools** - Chord progression analysis
- 📱 **PWA Support** - Mobile and desktop usage

## 📁 Project Structure

```
choral-llm-workbench/
├── backend/                 # NestJS backend
│   ├── src/
│   │   ├── app/          # Application modules
│   │   ├── audio/        # Audio synthesis service
│   │   ├── ai/           # Ollama integration
│   │   ├── music/        # MusicXML processing
│   │   └── api/          # API controllers
│   ├── test/             # Backend tests
│   └── package.json
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── composables/ # Vue composables
│   │   ├── views/       # Page components
│   │   ├── stores/      # Pinia stores
│   │   └── assets/      # Static assets
│   ├── public/          # Static files
│   ├── package.json
│   └── vite.config.ts
├── docs/                 # Documentation
├── installer/            # Pinokio installer
├── dist/                # Build output
└── package.json          # Root package.json
```

## 🔧 Development

### Backend Development
```bash
cd backend
npm run start          # Production server
npm run start:dev       # Development with hot reload
npm run test           # Run tests
npm run test:watch     # Watch mode
npm run lint            # ESLint
npm run typecheck        # TypeScript checking
```

### Frontend Development
```bash
cd frontend
npm run dev            # Development server
npm run build          # Production build
npm run preview        # Preview production build
npm run test           # Run tests
npm run lint            # ESLint
```

### Full Stack Development
```bash
npm run dev              # Start both backend and frontend
npm run build            # Build both for production
npm run test            # Run all tests
npm run lint            # Lint all code
```

## 🎨 UI Components

### Score Viewer
- Interactive music notation display
- Real-time cursor with audio sync
- Zoom and pan capabilities
- Click-to-play functionality
- Measure selection and highlighting

### Audio Controls
- Individual voice controls (S, A, T, B)
- Master volume and pan
- Tuning selection (432/440/443 Hz)
- Tempo and playback speed control

### AI Integration
- Ollama model selection
- Harmonization suggestions
- Style recommendations
- Real-time analysis feedback

## 🔊 Audio Engine

### Synthesis Engine
- **Web Audio API** - Real-time processing
- **Tone.js** - Professional synthesis
- **Sample Libraries** - Multiple instrument sets
- **Effects Processing** - Reverb, chorus, delay

### Music Processing
- **MusicXML Parser** - Complete standard support
- **MIDI Conversion** - Bidirectional conversion
- **Audio Export** - WAV, MP3, OGG formats
- **Streaming** - Real-time audio generation

## 🤖 AI Integration

### Ollama Setup
```typescript
// Backend AI Service
@Injectable()
export class OllamaService {
  private readonly ollamaUrl = 'http://localhost:11434';
  async generateHarmony(score: ScoreData): Promise<HarmonyResult> {
    const response = await fetch(`${this.ollamaUrl}/api/generate`, { method: 'POST', body: JSON.stringify({ model: 'llama3.1', prompt: this.buildHarmonyPrompt(score), stream: false }) });
    return response.json();
  }
}
```

### Available Models
- **llama3.1** - General purpose music analysis
```