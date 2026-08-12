import { Injectable, Logger } from '@nestjs/common';
import { EventsRepository } from './events.repository';
import { ResourceNotFoundException } from '../shared/exceptions';

@Injectable()
export class EventsService {
  private readonly logger = new Logger(EventsService.name);

  constructor(private eventsRepository: EventsRepository) {}

  async getEventDetails(eventId: string) {
    const event = await this.eventsRepository.findById(eventId);
    if (!event) {
      throw new ResourceNotFoundException('Event', eventId);
    }
    return event;
  }
}
