import { Controller, Get } from '@nestjs/common';

@Controller('llm')
export class LlmController {
  @Get('models')
  getModels() {
    // Minimal static catalog; in Phase 3 this can call Ollama CLI to list models
    return {
      models: [
        { name: 'ollama-default', provider: 'ollama', model: 'default' },
        { name: 'mistral-7b', provider: 'ollama', model: 'mistral-7b' }
      ]
    };
  }
}
