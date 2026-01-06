import { Module } from '@nestjs/common';
import { Controller, Get, Post, Body, UploadedFile, UseInterceptors } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiTags, ApiResponse, ApiOperation } from '@nestjs/swagger';
import { AudioService } from './audio/audio.service';
import { AiService } from '../ai/ai.service';
import { MusicService } from '../music/music.service';
import { ScoreData, AudioGenerationRequest } from './dto/score.dto';

@ApiTags('score')
@Controller('score')
@UseInterceptors(FileInterceptor('file'))
export class ScoreController {
  constructor(
    private readonly audioService: AudioService,
    private readonly aiService: AiService,
    private readonly musicService: MusicService,
  ) {}

  @Get()
  @ApiResponse({ status: 200, description: 'Get all scores' })
  @ApiOperation({ summary: 'Get all processed scores' })
  async getScores() {
    return this.musicService.getAllScores();
  }

  @Post('upload')
  @ApiOperation({ summary: 'Upload and process MusicXML file' })
  async uploadScore(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new Error('No file uploaded');
    }
    
    const scoreData = await this.musicService.parseMusicXML(file.buffer);
    
    return {
      success: true,
      scoreId: scoreData.id,
      partCount: scoreData.parts.length,
      measureCount: scoreData.measures,
      scoreInfo: scoreData.info
    };
  }

  @Post('analyze')
  @ApiOperation({ summary: 'Analyze score structure and harmony' })
  async analyzeScore(@Body() body: { scoreId: string }) {
    const scoreData = await this.musicService.getScoreById(body.scoreId);
    const analysis = await this.aiService.analyzeScore(scoreData);
    
    return {
      success: true,
      analysis
    };
  }

  @Post('generate-audio')
  @ApiOperation({ summary: 'Generate audio from score' })
  async generateAudio(@Body() request: AudioGenerationRequest) {
    const scoreData = await this.musicService.getScoreById(request.scoreId);
    
    const audioBuffers = await this.audioService.generateVoiceAudio({
      scoreData,
      voices: request.voices,
      tuning: request.tuning || 440,
      duration: request.duration || 15,
      instrument: request.instrument || 'piano'
    });
    
    return {
      success: true,
      audioBuffers,
      metadata: {
        sampleRate: 22050,
        channels: 'stereo',
        duration: request.duration || 15,
        tuning: request.tuning || 440
      }
    };
  }

  @Post('harmonize')
  @ApiOperation({ summary: 'Generate harmony using Ollama' })
  async harmonize(@Body() body: { scoreId: string; voicePart: string; style?: string }) {
    const scoreData = await this.musicService.getScoreById(body.scoreId);
    const harmony = await this.aiService.generateHarmony(scoreData, {
      voicePart: body.voicePart,
      style: body.style || 'classical'
    });
    
    return {
      success: true,
      harmony,
      metadata: {
        model: 'llama3.1',
        promptTokens: harmony.promptTokens,
        generationTime: harmony.generationTime
      }
    };
  }

  @Post('export')
  @ApiOperation({ summary: 'Export processed score' })
  async exportScore(@Body() body: { scoreId: string; format: 'xml' | 'midi' | 'wav' }) {
    const scoreData = await this.musicService.getScoreById(body.scoreId);
    const exportedData = await this.musicService.exportScore(scoreData, body.format);
    
    return {
      success: true,
      data: exportedData,
      filename: `score_export_${Date.now()}.${body.format}`
    };
  }
}