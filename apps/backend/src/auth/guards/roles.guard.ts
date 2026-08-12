import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AUTH } from '../../shared/constants';
import { ForbiddenResourceException } from '../../shared/exceptions';
import { AuthenticatedUser } from '../../shared/types';

/**
 * RolesGuard — enforces RBAC via the @Roles() decorator.
 * Throws ForbiddenResourceException if the user's role isn't allowed.
 * Must be used after JwtAuthGuard.
 */
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(AUTH.ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles || requiredRoles.length === 0) {
      return true; // No roles restricted
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user as AuthenticatedUser;

    if (!user) {
      throw new ForbiddenResourceException('User not authenticated');
    }

    if (!requiredRoles.includes(user.role)) {
      throw new ForbiddenResourceException(`Requires one of roles: ${requiredRoles.join(', ')}`);
    }

    return true;
  }
}
