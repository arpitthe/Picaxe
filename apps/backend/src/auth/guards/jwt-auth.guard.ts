import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

/**
 * JwtAuthGuard — attaches the validated user payload to req.user.
 * Apply globally in main.ts, or per-route with @UseGuards(JwtAuthGuard).
 * Throws 401 if the token is missing, expired, or invalid.
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
