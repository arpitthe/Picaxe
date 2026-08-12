import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

/**
 * Global HTTP exception filter.
 * Normalises all errors — both NestJS HttpExceptions and unexpected errors —
 * into a consistent response envelope:
 *
 * {
 *   success: false,
 *   statusCode: number,
 *   error: string,
 *   message: string,
 *   path: string,
 *   timestamp: string,
 * }
 */
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx      = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request  = ctx.getRequest<Request>();

    let status  = HttpStatus.INTERNAL_SERVER_ERROR;
    let error   = 'INTERNAL_SERVER_ERROR';
    let message = 'An unexpected error occurred';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const body = exception.getResponse() as Record<string, unknown>;
      error   = (body.error as string) ?? 'HTTP_ERROR';
      message = (body.message as string) ?? exception.message;
    } else if (exception instanceof Error) {
      this.logger.error(`Unhandled exception: ${exception.message}`, exception.stack);
    }

    response.status(status).json({
      success:    false,
      statusCode: status,
      error,
      message,
      path:       request.url,
      timestamp:  new Date().toISOString(),
    });
  }
}
