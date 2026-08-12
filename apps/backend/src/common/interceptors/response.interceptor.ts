import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiResponse } from '../../shared/types';

/**
 * Global response interceptor.
 * Wraps every successful controller return value in the standard
 * ApiResponse envelope:
 *
 * {
 *   success: true,
 *   data: T,
 *   timestamp: string,
 * }
 *
 * Responses that are already an ApiResponse (detected via the `success` key)
 * are passed through unchanged to avoid double-wrapping.
 */
@Injectable()
export class ResponseInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(_ctx: ExecutionContext, next: CallHandler<T>): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map(data => {
        // Avoid double-wrapping
        if (data && typeof data === 'object' && 'success' in data) {
          return data as unknown as ApiResponse<T>;
        }
        return {
          success:   true,
          data,
          timestamp: new Date().toISOString(),
        };
      }),
    );
  }
}
