import { HttpException, HttpStatus } from '@nestjs/common';

/** 404 — Resource not found */
export class ResourceNotFoundException extends HttpException {
  constructor(resource: string, id?: string) {
    super(
      { error: 'NOT_FOUND', message: id ? `${resource} with id "${id}" not found` : `${resource} not found` },
      HttpStatus.NOT_FOUND,
    );
  }
}

/** 409 — Resource already exists */
export class ResourceConflictException extends HttpException {
  constructor(message: string) {
    super({ error: 'CONFLICT', message }, HttpStatus.CONFLICT);
  }
}

/** 403 — Authenticated but unauthorized */
export class ForbiddenResourceException extends HttpException {
  constructor(message = 'You do not have permission to perform this action') {
    super({ error: 'FORBIDDEN', message }, HttpStatus.FORBIDDEN);
  }
}

/** 422 — Business logic validation failure */
export class BusinessValidationException extends HttpException {
  constructor(message: string) {
    super({ error: 'BUSINESS_VALIDATION', message }, HttpStatus.UNPROCESSABLE_ENTITY);
  }
}

/** 503 — AI / external service unavailable */
export class AiServiceUnavailableException extends HttpException {
  constructor(detail?: string) {
    super(
      { error: 'AI_SERVICE_UNAVAILABLE', message: detail ?? 'AI service is currently unavailable' },
      HttpStatus.SERVICE_UNAVAILABLE,
    );
  }
}
