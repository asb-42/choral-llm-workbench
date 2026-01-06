import { Module } from '@nestjs/common';
import { AudioModule } from './audio/audio.module';
import { AiModule } from './ai/ai.module';
import { MusicModule } from './music/music.module';
import { LlmModule } from './llm/llm.module';

@Module({
  imports: [AudioModule, AiModule, MusicModule, LlmModule],
  controllers: [],
  providers: [],
})
export class AppModule {}
