import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

// Mock Ollama CLI calls to avoid requiring a local model during smoke tests
jest.mock('child_process', () => ({
  execSync: jest.fn(() => JSON.stringify({ measure: 1, root: 'C', quality: 'major' }))
}));

describe('Harmonize Endpoints Smoke - Phase 7', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('POST /api/harmonize responds with current state', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/harmonize')
      .send({ scoreId: 'smoke7', prompts: { S: 'x', A: 'y', T: 'z', B: 'w' }, tuning: 432 });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('current');
  });

  it('POST /api/harmonize/undo responds', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/harmonize/undo')
      .send({ scoreId: 'smoke7' });
    expect(res.status).toBe(200);
  });

  it('POST /api/harmonize/redo responds', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/harmonize/redo')
      .send({ scoreId: 'smoke7' });
    expect(res.status).toBe(200);
  });

  it('POST /api/harmonize/generate-audio-per-voice responds', async () => {
    const res = await request(app.getHttpServer())
      .post('/api/harmonize/generate-audio-per-voice')
      .send({ scoreId: 'smoke7', voices: ['S','A','T','B'], tuning: 432, duration: 0.8 });
    expect(res.status).toBe(200);
    // Optional: allow either presence of perVoiceAudios or an empty array
    if (res.body && res.body.perVoiceAudios) {
      expect(Array.isArray(res.body.perVoiceAudios)).toBe(true);
    }
  });
});
