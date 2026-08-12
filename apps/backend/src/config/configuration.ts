export default () => ({
  port: parseInt(process.env.PORT ?? '3001', 10),
  nodeEnv: process.env.NODE_ENV ?? 'development',
  database: {
    url: process.env.DATABASE_URL,
  },
  jwt: {
    secret: process.env.JWT_SECRET ?? 'change-me-in-production',
    accessTokenTtl: process.env.JWT_ACCESS_TTL ?? '15m',
    refreshTokenTtl: process.env.JWT_REFRESH_TTL ?? '7d',
  },
  storage: {
    provider: process.env.STORAGE_PROVIDER ?? 'r2', // 'r2' | 's3'
    endpoint: process.env.STORAGE_ENDPOINT,
    bucket: process.env.STORAGE_BUCKET,
    accessKeyId: process.env.STORAGE_ACCESS_KEY_ID,
    secretAccessKey: process.env.STORAGE_SECRET_ACCESS_KEY,
    publicBaseUrl: process.env.STORAGE_PUBLIC_BASE_URL,
  },
  qdrant: {
    url: process.env.QDRANT_URL ?? 'http://localhost:6333',
    collection: process.env.QDRANT_COLLECTION ?? 'face_embeddings',
  },
  aiService: {
    url: process.env.AI_SERVICE_URL ?? 'http://localhost:8000',
    timeout: parseInt(process.env.AI_SERVICE_TIMEOUT ?? '30000', 10),
  },
  redis: {
    url: process.env.REDIS_URL ?? 'redis://localhost:6379',
  },
});
