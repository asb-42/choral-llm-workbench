import { Controller, Post, Body } from '@nestjs/common';
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
}
