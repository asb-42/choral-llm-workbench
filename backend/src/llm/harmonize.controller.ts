import { Controller, Post, Body, Get, Query } from '@nestjs/common';
import { HarmonizeService } from './harmonize.service';

export interface HarmonizeRequest {
  scoreId: string;
  prompts: { S: string; A: string; T: string; B: string };
  tuning?: number;
}

@Controller('harmonize')
export class HarmonizeController {
  constructor(private readonly harmonizeService: HarmonizeService) {}

  @Post()
  harmonize(@Body() req: HarmonizeRequest) {
    const { scoreId, prompts, tuning } = req;
    return this.harmonizeService.harmonize(scoreId, prompts, tuning);
  }

  @Post('undo')
  undo(@Body() body: { scoreId: string }) {
    return this.harmonizeService.undo(body.scoreId);
  }

  @Post('redo')
  redo(@Body() body: { scoreId: string }) {
    return this.harmonizeService.redo(body.scoreId);
  }

  @Post('generate-audio-per-voice')
  generateAudioPerVoice(@Body() body: { scoreId: string; voices?: string[]; tuning?: number; duration?: number }) {
    const { scoreId, voices, tuning, duration } = body;
    return this.harmonizeService.generateAudioPerVoice(scoreId, voices, tuning, duration);
  }

  @Get('preview')
  preview(@Query('scoreId') scoreId: string) {
    return this.harmonizeService.preview(scoreId);
  }

  @Post('reorder-measures')
  reorderMeasures(@Body() body: { scoreId: string; order: number[] }) {
    const { scoreId, order } = body;
    return this.harmonizeService.reorderMeasures(scoreId, order);
  }
}
