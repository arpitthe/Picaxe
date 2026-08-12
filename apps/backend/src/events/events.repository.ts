import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';

/**
 * Repository Pattern:
 * Keeps Prisma query logic out of the Service layer.
 * Allows easier testing and separates data access from business logic.
 */
@Injectable()
export class EventsRepository {
  constructor(private prisma: PrismaService) {}

  async findById(id: string) {
    return this.prisma.event.findUnique({
      where: { id, deletedAt: null },
      include: { organization: true },
    });
  }

  async create(data: any) {
    return this.prisma.event.create({ data });
  }

  // Other data access methods...
}
