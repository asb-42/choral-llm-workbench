import { Injectable } from '@nestjs/common';

@Injectable()
export class HarmonizeService {
  harmonize(scoreId: string, prompts: any, tuning?: number) {
    // Phase 2 MVP: return deterministic dummy results suitable for UI preview
    const results = {
      S: { measure: 1, root: 'C', quality: 'major' },
      A: { measure: 1, root: 'G', quality: 'major' },
      T: { measure: 1, root: 'E', quality: 'major' },
      B: { measure: 1, root: 'C', quality: 'major' }
    };
    return {
      scoreId,
      results,
      summary: 'Phase 2 MVP: simulated harmonization via Ollama-backed adapter'
    };
  }
}
