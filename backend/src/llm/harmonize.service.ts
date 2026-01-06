import { Injectable } from '@nestjs/common';
import { execSync } from 'child_process';

@Injectable()
export class HarmonizeService {
  // Default model for local LLM (Ollama)
  private defaultModel: string = 'mistral-7b';

  // In-memory undo/redo state per score
  private undoStacks: Map<string, any[]> = new Map();
  private redoStacks: Map<string, any[]> = new Map();
  private currentStates: Map<string, any> = new Map();

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

    const newState = { scoreId, results, summary: 'Ollama-based harmonization (Phase 4 rollout)' };
    this.currentStates.set(scoreId, newState);
    return newState;
  }

  // Undo last harmonization for a score
  undo(scoreId: string) {
    const undoStack = this.undoStacks.get(scoreId) ?? [];
    const current = this.currentStates.get(scoreId);
    if (undoStack.length > 0 && current) {
      const prev = undoStack.pop();
      // store back the remaining undo stack
      this.undoStacks.set(scoreId, undoStack);
      // push current to redo stack
      const redoStack = this.redoStacks.get(scoreId) ?? [];
      redoStack.push(current);
      this.redoStacks.set(scoreId, redoStack);
      // set previous state as current
      this.currentStates.set(scoreId, prev);
      return prev;
    }
    return current ?? { scoreId, results: {}, summary: 'Nothing to undo' };
  }

  // Redo last undone harmonization for a score
  redo(scoreId: string) {
    const redoStack = this.redoStacks.get(scoreId) ?? [];
    const current = this.currentStates.get(scoreId);
    if (redoStack.length > 0) {
      const next = redoStack.pop();
      this.redoStacks.set(scoreId, redoStack);
      const undoStack = this.undoStacks.get(scoreId) ?? [];
      if (current) undoStack.push(current);
      this.undoStacks.set(scoreId, undoStack);
      this.currentStates.set(scoreId, next);
      return next;
    }
    return current ?? { scoreId, results: {}, summary: 'Nothing to redo' };
  }

  // Generate per-voice audio beeps (simple client-side-friendly audio)
  generateAudioPerVoice(scoreId: string, voices: string[] = ['S', 'A', 'T', 'B'], tuning?: number, duration?: number) {
    const perVoiceAudios: Array<{ voice: string; label: string; src: string }> = [];
    const voiceNames: Record<string, string> = { S: 'Soprano', A: 'Alto', T: 'Tenor', B: 'Bass' };
    const baseFreq: Record<string, number> = { S: 523.25, A: 440.0, T: 329.63, B: 261.63 };

    for (const v of voices) {
      const freq = baseFreq[v] ?? 440;
      const dur = duration ?? 0.8;
      const src = this.createBeepWavDataUrl(freq, dur);
      perVoiceAudios.push({ voice: v, label: voiceNames[v] ?? v, src });
    }

    return { scoreId, perVoiceAudios };
  }

  // Helper: generate a small WAV data URL with a sine beep
  private createBeepWavDataUrl(freq: number, durationSec: number, sampleRate = 44100): string {
    const samples = Math.floor(durationSec * sampleRate);
    const data = Buffer.alloc(samples * 2);
    const maxAmplitude = 32760;
    for (let i = 0; i < samples; i++) {
      const t = i / sampleRate;
      const sample = Math.round(maxAmplitude * Math.sin(2 * Math.PI * freq * t));
      data.writeInt16LE(sample, i * 2);
    }
    const dataBytes = data.length;
    const wavHeader = Buffer.alloc(44);
    wavHeader.write('RIFF', 0);
    wavHeader.writeUInt32LE(36 + dataBytes, 4);
    wavHeader.write('WAVE', 8);
    wavHeader.write('fmt ', 12);
    wavHeader.writeUInt32LE(16, 16);
    wavHeader.writeUInt16LE(1, 20); // PCM
    wavHeader.writeUInt16LE(1, 22); // channels
    wavHeader.writeUInt32LE(sampleRate, 24);
    wavHeader.writeUInt32LE(sampleRate * 2 * 1, 28); // byteRate
    wavHeader.writeUInt16LE(2, 32); // blockAlign
    wavHeader.writeUInt16LE(16, 34); // bitsPerSample
    wavHeader.write("data", 36);
    wavHeader.writeUInt32LE(dataBytes, 40);
    const wavBuffer = Buffer.concat([wavHeader, data]);
    return 'data:audio/wav;base64,' + wavBuffer.toString('base64');
  }
}
