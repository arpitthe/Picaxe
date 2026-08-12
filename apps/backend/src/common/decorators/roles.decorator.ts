import { SetMetadata } from '@nestjs/common';
import { AUTH } from '../../shared/constants';

/**
 * @Roles(...roles) decorator — marks a route as accessible only by specified roles.
 * Consumed by RolesGuard.
 *
 * Usage:
 *   @Roles('ADMIN', 'ORGANIZATION')
 *   @UseGuards(JwtAuthGuard, RolesGuard)
 *   @Post('events')
 *   createEvent() { ... }
 */
export const Roles = (...roles: string[]) => SetMetadata(AUTH.ROLES_KEY, roles);
