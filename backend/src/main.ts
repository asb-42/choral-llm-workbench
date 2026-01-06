import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AudioModule } from './audio/audio.module';
import { AiModule } from './ai/ai.module';
import { MusicModule } from './music/music.module';

async function bootstrap() {
  const app = NestFactory.create(AppModule);
  
  // Enable CORS for Vue.js frontend
  app.enableCors({
    origin: 'http://localhost:5173', // Vue dev server
    credentials: true,
  });
  
  // Global validation pipe
  app.useGlobalPipes(new ValidationPipe());
  
  // API prefix
  app.setGlobalPrefix('api');
  
  // Swagger documentation
  const config = new DocumentBuilder()
    .setTitle('Choral LLM Workbench API')
    .setDescription('AI-powered choral music analysis with local LLM integration')
    .setVersion('1.0')
    .addTag('audio', 'Audio synthesis and processing')
    .addTag('ai', 'Ollama LLM integration')
    .addTag('music', 'MusicXML processing and analysis')
    .addTag('score', 'Score visualization and editing')
    .build();
  
  SwaggerModule.setup('docs', app, config);
  
  const port = process.env.PORT || 3000;
  await app.listen(port);
  
  console.log(`🎵 Choral LLM Workbench Backend running on port ${port}`);
  console.log(`📚 API Documentation: http://localhost:${port}/docs`);
}

bootstrap().catch(err => {
  console.error('❌ Failed to start application:', err);
  process.exit(1);
});