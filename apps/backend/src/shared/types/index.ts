// Shared API response envelope
export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

// Pagination wrapper
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// Pagination query params
export interface PaginationParams {
  page?: number;
  limit?: number;
}

// The JWT access token payload
export interface JwtPayload {
  sub: string;   // userId
  role: string;
  iat?: number;
  exp?: number;
}

// Represents the authenticated user attached to req.user by JwtAuthGuard
export interface AuthenticatedUser {
  userId: string;
  role: string;
}
