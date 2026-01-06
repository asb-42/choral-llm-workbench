# Architecture: Vue-based front-end with Ollama LLM

This document outlines the architecture to replace the Gradio-based UI with a Vue 3 frontend backed by a NestJS API and a Python core for music processing. Ollama is used as the default local LLM backend with a pluggable adapter to support additional backends in the future. A one-click installer (Pinokio) bootstraps the stack.

## Goals
- Local standalone tool to harmonize MusicXML files using a local LLM.
- Separate audible renderings per voice (S, A, T, B) and combined audio.
- Export manipulated scores back to MusicXML.
- Self-contained installation with minimal user interaction.

## Phase 1 Deliverables (Phase 1)
- API surface and data contracts defined for core flows: upload, harmonize, export, and model discovery.
- MVP UI outline for a Vue-based frontend that replaces Gradio, with per-voice prompts and tuning controls.
- Establish a central LLM configuration point and an adapter pattern to support Ollama and future backends.
- Install flow (Pinokio) defined to bootstrap Python, Node, and local LLM binaries with minimal user interaction.

## Phase 3 – MVP Frontend
- Vue 3 MVP replacing Gradio; default LLM mistral-7b via Ollama adapter; UI supports model switch in future versions.
- MVP interactions: Upload MusicXML, per-voice prompts, tuning, harmonize, export, and per-voice audio previews.
- Endpoints: /api/score/upload, /api/harmonize, /api/score/export, /api/llm/models.

## Phase 4 – Ollama-based Harmonization
- Ollama-backed local LLM per voice; per-voice JSON responses
- Endpoints refined: /api/llm/models present; /api/harmonize uses Ollama CLI

## Phase 5 – MVP: Undo/Redo & Per-Voice Audio (Frontend + Backend)
- In-memory undo/redo for quick MVP; per-score persistence via storage/undo_redo
- API: /api/harmonize/undo, /api/harmonize/redo, /api/harmonize/generate-audio-per-voice
- Frontend: Undo/Redo buttons; per-voice audio previews; Generate Audio per voice

## Phase 6 – Persistente Undo/Redo & MVP Per-Voice Audio
- On-disk persistence for undo/redo to survive restarts (storage/undo_redo/{scoreId}.json)
- Endpoints: /api/harmonize/undo, /api/harmonize/redo, /api/harmonize/generate-audio-per-voice (solid MVP for real usage)
- Audio: per-voice audio beacons via server-provided Data URLs; real rendering planned later
- UX: persistent history indicators; per-voice audio players; robust status messages

## API surface (high-level)
- POST /api/score/upload
- POST /api/llm/harmonize
- POST /api/llm/models
- POST /api/armonize/undo
- POST /api/armonize/redo
- POST /api/armonize/generate-audio-per-voice
- POST /api/score/export
- GET /docs

## MVP UI (Phase 6+)
- Single-page UI with per-voice prompts, per-voice audio, Undo/Redo, and export.

## Installation
- Pinokio-based installer; Ollama is a system requirement and will be checked/ensured by installer scripts.

## Migration notes
- Gradio-based UI replaced by Vue; Dummies removed; Ollama as standard backend.
