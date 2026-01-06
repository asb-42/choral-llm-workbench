import { Module } from '@nestjs/common';
import { HarmonizeController } from './harmonize.controller';
import { HarmonizeService } from './harmonize.service';

@Module({
  controllers: [ HarmonizeController ],
  providers: [ HarmonizeService ],
  exports: [ HarmonizeService ],
})
export class HarmonizeModule {}
