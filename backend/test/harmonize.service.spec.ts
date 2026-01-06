import { Test, TestingModule } from '@nestjs/testing';
import { HarmonizeService } from '../src/llm/harmonize.service';

// Mock execSync to avoid needing a real Ollama installation during tests
jest.mock('child_process', () => ({
  execSync: jest.fn(() => JSON.stringify({ measure: 1, root: 'C', quality: 'major' }))
}));

describe('HarmonizeService Phase 6', () => {
  let service: HarmonizeService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [HarmonizeService],
    }).compile();

    service = module.get<HarmonizeService>(HarmonizeService);
  });

  it('harmonize creates current state and persists', async () => {
    const scoreId = 'test1';
    const prompts = { S: 'promptS', A: 'promptA', T: 'promptT', B: 'promptB' };
    const res = await service.harmonize(scoreId, prompts, 432);
    expect(res).toHaveProperty('current');
    expect(res.current).toHaveProperty('results');

    // Storage file should exist after harmonize
    const fs = require('fs');
    const path = require('path');
    const stateFile = path.resolve('storage', 'undo_redo', `${scoreId}.json`);
    expect(fs.existsSync(stateFile)).toBe(true);
  });

  it('undo and redo transitions', async () => {
    const scoreId = 'test2';
    const p1 = { S: 'p1', A: 'p1', T: 'p1', B: 'p1' };
    const p2 = { S: 'p2', A: 'p2', T: 'p2', B: 'p2' };
    await service.harmonize(scoreId, p1, 432);
    await service.harmonize(scoreId, p2, 432);
    const up = await service.undo(scoreId);
    expect(up).toBeTruthy();
    const re = await service.redo(scoreId);
    expect(re).toBeTruthy();
  });

  it('generate audio per voice returns 4 entries', () => {
    const out = service.generateAudioPerVoice('test3', ['S','A','T','B'], 432, 0.8);
    expect(out).toHaveProperty('perVoiceAudios');
    expect(out.perVoiceAudios.length).toBe(4);
  });
});
