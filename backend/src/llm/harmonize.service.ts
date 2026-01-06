import { Injectable } from '@nestjs/common';
import { execSync } from 'child_process';

@Injectable()
export class HarmonizeService {
  // Optional: allow configuring a default model; can be expanded via config
  private defaultModel: string = 'mistral-7b';

  harmonize(scoreId: string, prompts: any, tuning?: number) {
    const voices = ['S', 'A', 'T', 'B'];
    const results: any = {};

    for (const voice of voices) {
      try {
        const prompt = prompts?.[voice] ?? '';
        // Build a JSON payload for Ollama
        const input = JSON.stringify({ prompt, voice, scoreId });
        // Call the local LLM (Ollama) via CLI; expects JSON on stdout
        const model = this.defaultModel;
        const stdout = execSync(`ollama eval ${model} --json '${input}'`, {
          encoding: 'utf8',
          stdio: 'pipe',
        });
        const data = JSON.parse(stdout.trim());
        // Normalize to internal shape: { measure, root, quality }
        if (data && typeof data.measure !== 'undefined') {
          results[voice] = {
            measure: data.measure,
            root: data.root || 'C',
            quality: data.quality || 'major'
          };
        } else {
          // Fallback
          results[voice] = { measure: 1, root: data?.root ?? 'C', quality: data?.quality ?? 'major' };
        }
      } catch (err) {
        // If LLM call fails, fallback to a safe default for continuity
        results[voice] = { measure: 1, root: 'C', quality: 'major' };
      }
    }

    return {
      scoreId,
      results,
      summary: 'Ollama-based harmonization (Phase 4 rollout)'
    };
  }
}
