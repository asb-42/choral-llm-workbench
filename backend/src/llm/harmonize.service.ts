import { Injectable } from '@nestjs/common';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class HarmonizeService {
  // Default model for local LLM (Ollama)
  private defaultModel: string = 'mistral-7b';

  // In-memory undo/redo state per score
  private undoStacks: Map<string, any[]> = new Map();
  private redoStacks: Map<string, any[]> = new Map();
  private currentStates: Map<string, any> = new Map();

  // Storage paths for Phase 6/7
  private storageDir: string = path.resolve(process.cwd(), 'storage');

  harmonize(scoreId: string, prompts: any, tuning?: number) {
    // Push current state to undo stack if exists
    const current = this.currentStates.get(scoreId);
    if (current) {
      const arr = this.undoStacks.get(scoreId) ?? [];
      arr.push(current);
      this.undoStacks.set(scoreId, arr);
    }
    // Clear redo stack on new action
    this.redoStacks.set(scoreId, []);

    const voices = ['S', 'A', 'T', 'B'];
    const results: any = {};

    for (const voice of voices) {
      try {
        const prompt = prompts?.[voice] ?? '';
        const input = JSON.stringify({ prompt, voice, scoreId });
        const model = this.defaultModel;
        const stdout = execSync(`ollama eval ${model} --json '${input}'`, {
          encoding: 'utf8',
          stdio: 'pipe',
        });
        const data = JSON.parse(stdout.trim());
        if (data && typeof data.measure !== 'undefined') {
          results[voice] = {
            measure: data.measure,
            root: data.root || 'C',
            quality: data.quality || 'major'
          };
        } else {
          results[voice] = { measure: 1, root: data?.root ?? 'C', quality: data?.quality ?? 'major' };
        }
      } catch (err) {
        // Fallback safely
        results[voice] = { measure: 1, root: 'C', quality: 'major' };
      }
    }

    const newCurrent = { scoreId, results, summary: 'Ollama-based harmonization (Phase 4 rollout)' };
    this.currentStates.set(scoreId, newCurrent);

    // Persist a simple MusicXML file path for Phase 7 server-side audio (best-effort)
    const scoresDir = path.resolve(this.storageDir, 'scores');
    if (!fs.existsSync(scoresDir)) {
      fs.mkdirSync(scoresDir, { recursive: true });
    }
    // Note: actual MusicXML content should be written by the upload pathway; create a placeholder file reference if needed
    const placeholder = path.join(scoresDir, `${scoreId}.musicxml`);
    if (!fs.existsSync(placeholder)) {
      // If an actual file isn't there yet, create an empty placeholder to avoid missing file errors
      fs.writeFileSync(placeholder, '<score></score>', 'utf8');
    }

    this.saveState(this.loadState(scoreId) /* ensure directory exists but we use existing logic below */);
    return newCurrent;
  }

  // Undo last harmonization for a score
  undo(scoreId: string) {
    const state = this.loadState(scoreId);
    const history = state.history ?? [];
    if (history.length > 0 && state.current) {
      const prev = history.pop();
      const redoStack = state.future ?? [];
      redoStack.push(state.current);
      state.history = history;
      state.current = prev;
      state.future = redoStack;
      this.saveState(state);
      return { scoreId, current: state.current, history: state.history, future: state.future };
    }
    return { scoreId, current: state.current, history: state.history, future: state.future };
  }

  // Redo last undone harmonization for a score
  redo(scoreId: string) {
    const state = this.loadState(scoreId);
    const future = state.future ?? [];
    if (future.length > 0) {
      const next = future.pop();
      const history = state.history ?? [];
      if (state.current) history.push(state.current);
      state.history = history;
      state.current = next;
      state.future = future;
      this.saveState(state);
      return { scoreId, current: state.current, history: state.history, future: state.future };
    }
    return { scoreId, current: state.current, history: state.history, future: state.future };
  }

  // Generate per-voice audio (server-side, Phase 7 MVP)
  generateAudioPerVoice(scoreId: string, voices: string[] = ['S','A','T','B'], tuning?: number, duration?: number) {
    const scriptPath = path.resolve(process.cwd(), 'scripts', 'render_voice_audio.py');
    const scorePath = path.resolve(process.cwd(), 'storage', 'scores', `${scoreId}.musicxml`);
    const outdir = path.resolve(process.cwd(), 'storage', 'voices', scoreId);
    // Ensure outdir exists
    if (!fs.existsSync(outdir)) {
      fs.mkdirSync(outdir, { recursive: true });
    }
    const cmd = `python3 "${scriptPath}" --score-path "${scorePath}" --voices "${voices.join(',')}" --tuning ${tuning ?? 432} --duration ${duration ?? 0.8} --soundfont ~/.fluidsynth/default_sound_font.sf2 --outdir "${outdir}"`;
    try {
      const stdout = execSync(cmd, { encoding: 'utf8' });
      const data = JSON.parse(stdout.trim());
      return data;
    } catch (err) {
      return { perVoiceAudios: [] };
    }
  }

  // Helper: load and save state (simplified for coexistence with previous in-memory approach)
  private loadState(scoreId: string) {
    const file = path.resolve(this.storageDir, 'undo_redo', `${scoreId}.json`);
    if (fs.existsSync(file)) {
      try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return { scoreId, history: [], current: null, future: [] }; }
    }
    return { scoreId, history: [], current: null, future: [] };
  }

  private saveState(state: any) {
    const file = path.resolve(this.storageDir, 'undo_redo', `${state.scoreId}.json`);
    const dir = path.dirname(file);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(file, JSON.stringify(state, null, 2), 'utf8');
  }
}
