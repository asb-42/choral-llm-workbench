import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import * as path from 'path';
import * as fs from 'fs';
import * as express from 'express';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

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

  // Serve static UI fallback if available
  const staticUiDir = path.resolve(__dirname, '..', 'frontend', 'static');
  if (fs.existsSync(staticUiDir)) {
    app.use('/ui', express.static(staticUiDir));
    app.get('/', (req, res) => {
      const idx = path.resolve(staticUiDir, 'index.html');
      if (fs.existsSync(idx)) {
        res.sendFile(idx);
      } else {
        res.status(404).send('UI not found');
      }
    });
  }

  const port = process.env.PORT || 3000;
  await app.listen(port);

  console.log(`🎵 Choral LLM Workbench Backend running on port ${port}`);
  console.log(`📚 API Documentation: http://localhost:${port}/docs`);
}

bootstrap().catch(err => {
  console.error('❌ Failed to start application:', err);
  process.exit(1);
});
