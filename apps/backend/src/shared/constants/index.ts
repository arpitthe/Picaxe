export const ROLES = {
  STUDENT: 'STUDENT',
  ORGANIZATION: 'ORGANIZATION',
  ADMIN: 'ADMIN',
  SUPER_ADMIN: 'SUPER_ADMIN',
} as const;

export const AUTH = {
  ROLES_KEY: 'roles',
  CURRENT_USER_KEY: 'user',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 24,
  MAX_LIMIT: 100,
} as const;

export const PROCESSING = {
  MAX_RETRIES: 3,
  CONFIDENCE_AUTO_CONFIRM: 0.95,  // above this: auto-confirm
  CONFIDENCE_REVIEW:        0.80,  // between this and above: pending review
  CONFIDENCE_REJECT:        0.80,  // below this: auto-reject
} as const;

export const STORAGE = {
  MAX_FILE_SIZE_BYTES: 52_428_800, // 50 MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/heic', 'image/webp'],
  ALLOWED_CERT_TYPES:  ['image/jpeg', 'image/png', 'application/pdf'],
} as const;

export const AUDIT_ACTIONS = {
  // Auth
  USER_REGISTERED:     'USER_REGISTERED',
  USER_LOGGED_IN:      'USER_LOGGED_IN',
  USER_LOGGED_OUT:     'USER_LOGGED_OUT',
  // Admin
  OVERRIDE_MATCH:      'OVERRIDE_MATCH',
  DELETE_PROFILE:      'DELETE_PROFILE',
  // Org
  EVENT_CREATED:       'EVENT_CREATED',
  EVENT_UPDATED:       'EVENT_UPDATED',
  EVENT_ARCHIVED:      'EVENT_ARCHIVED',
  BATCH_UPLOAD:        'BATCH_UPLOAD',
  BATCH_COMPLETE:      'BATCH_COMPLETE',
  TAG_REVIEWED:        'TAG_REVIEWED',
  // System
  WORKER_SCALE:        'WORKER_SCALE',
  EMBEDDING_CREATED:   'EMBEDDING_CREATED',
  EMBEDDING_REPLACED:  'EMBEDDING_REPLACED',
} as const;
