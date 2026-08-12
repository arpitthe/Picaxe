import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration';
import { DatabaseModule } from './database/database.module';
import { AuthModule } from './auth/auth.module';
import { EventsModule } from './events/events.module';

@Module({
  imports: [
    // Configuration initialized globally
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    // Global database module
    DatabaseModule,
    
    // Feature Modules
    AuthModule,
    EventsModule,
    
    // Future Feature Modules:
    // UsersModule,
    // StudentsModule,
    // OrganizationsModule,
    // MediaModule,
    
    // Future Integration Modules:
    // StorageModule,
    // AiPipelineModule,
    // NotificationsModule,
  ],
})
export class AppModule {}
