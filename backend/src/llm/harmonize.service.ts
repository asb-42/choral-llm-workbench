import { Injectable } from '@nestjs/common';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class HarmonizeService {
  private defaultModel: string = 'mistral-7b';
  private storageDir: string = path.resolve(process.cwd(), 'storage');

  // In-memory undo/redo state per score (Phase 5/6) plus persistent on-disk for Phase 7+
  private undoStacks: Map<string, any[]> = new Map();
  private redoStacks: Map<string, any[]> = new Map();
  private currentStates: Map<string, any> = new Map();

  constructor() {
    // Ensure storage dirs exist for onboarding
    const dirs = [this.storageDir, path.resolve(this.storageDir, 'undo_redo'), path.resolve(this.storageDir, 'scores'), path.resolve(this.storageDir, 'voices')];
    dirs.forEach(d => { if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true }); });
  }

  // Harmonize for a score (Phase 7 MVP)
  harmonize(scoreId: string, prompts: any, tuning?: number) {
    // Push current state to undo list
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
        const stdout = execSync(`ollama eval ${this.defaultModel} --json '${input}'`, {
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
        results[voice] = { measure: 1, root: 'C', quality: 'major' };
      }
    }

    // Compute a simple default measure order from the results
    const maxMeasure = Object.values(results).reduce((m, v) => Math.max(m, v?.measure ?? 0), 0);
    const order = maxMeasure > 0 ? Array.from({ length: maxMeasure }, (_, i) => i + 1) : [1];

    const newCurrent = { scoreId, results, order, summary: 'Ollama-based harmonization (Phase 7 MVP)' };
    this.currentStates.set(scoreId, newCurrent);

    // Persist to disk for Phase 7: scores placeholder (actual MusicXML updates happen on file upload in storage/scores)
    const scoresDir = path.resolve(this.storageDir, 'scores');
    if (!fs.existsSync(scoresDir)) fs.mkdirSync(scoresDir, { recursive: true });
    const placeholder = path.join(scoresDir, `${scoreId}.musicxml`);
    if (!fs.existsSync(placeholder)) {
      fs.writeFileSync(placeholder, '<score></score>', 'utf8');
    }

    // Persist full state to undo_redo json for resiliency
    const state = { scoreId, history: [], current: newCurrent, future: [] };
    const undoPath = path.resolve(this.storageDir, 'undo_redo', `${scoreId}.json`);
    fs.writeFileSync(undoPath, JSON.stringify(state, null, 2), 'utf8');

    return { scoreId, current: newCurrent, history: state.history, future: state.future };
  }

  // Undo last harmonization
  undo(scoreId: string) {
    const state = this.loadState(scoreId);
    const history = state.history ?? [];
    if (history.length > 0 && state.current) {
      const prev = history.pop();
      const future = state.future ?? [];
      future.push(state.current);
      state.history = history;
      state.current = prev;
      state.future = future;
      this.saveState(state);
      return { scoreId, current: state.current, history: state.history, future: state.future };
    }
    return { scoreId, current: state.current, history: state.history, future: state.future };
  }

  // Redo last undone
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

  // Generate per-voice audio (Phase 7 MVP) using script
  generateAudioPerVoice(scoreId: string, voices: string[] = ['S','A','T','B'], tuning?: number, duration?: number) {
    const scriptPath = path.resolve(process.cwd(), 'scripts', 'render_voice_audio.py');
    const scorePath = path.resolve(process.cwd(), 'storage', 'scores', `${scoreId}.musicxml`);
    const outdir = path.resolve(process.cwd(), 'storage', 'voices', scoreId);
    if (!fs.existsSync(outdir)) fs.mkdirSync(outdir, { recursive: true });
    const cmd = `python3 "${scriptPath}" --score-path "${scorePath}" --voices "${voices.join(',')}" --tuning ${tuning ?? 432} --duration ${duration ?? 0.8} --soundfont ~/.fluidsynth/default_sound_font.sf2 --outdir "${outdir}"`;
    try {
      const stdout = execSync(cmd, { encoding: 'utf8' });
      const data = JSON.parse(stdout.trim());
      return data;
    } catch (err) {
      return { perVoiceAudios: [] };
    }
  }

  // Preview current score order (live score preview)
  preview(scoreId: string) {
    const state = this.loadState(scoreId);
    const current = state.current ?? { scoreId, results: {}, order: [], summary: '' };
    return {
      scoreId: scoreId,
      order: current.order ?? [],
      measures: (current.order ?? []).length,
      current: current
    };
  }

  // Reorder measures (Drag-and-Drop)
  reorderMeasures(scoreId: string, newOrder: number[]) {
    const state = this.loadState(scoreId);
    const current = state.current ?? { scoreId, results: {}, order: newOrder, summary: 'Reordered' };
    current.order = newOrder;
    state.current = current;
    // Persist
    this.saveState(state);
    return { scoreId, current, history: state.history, future: state.future };
  }

  // Helpers: persistent load/save
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
