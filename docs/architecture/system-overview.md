# System Architecture Overview — Picaxe

Picaxe is an AI-powered event media and certificate tagging system designed to identify and distribute event photos and certificates to participating students using facial recognition and NLP-based OCR matching.

## Target System Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                     │
│                     (apps/frontend)                     │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                     NestJS Backend                      │
│                      (apps/backend)                     │
└──────────────┬────────────────────────────┬─────────────┘
               │                            │
               ▼                            ▼
┌────────────────────────────┐ ┌──────────────────────────┐
│     Picaxe Face Engine     │ │    Picaxe NLP Engine     │
│    (apps/face-engine)      │ │    (apps/nlp-engine)     │
└──────────────┬─────────────┘ └──────────────────────────┘
               │
               ▼
┌────────────────────────────┐
│      Qdrant Vector DB      │
└────────────────────────────┘
```

## Modular Boundaries
1. **Frontend**: Standalone Next.js 16 user interface for students, event organizers, and administrators.
2. **Backend Gateway**: Source of truth for database entities (users, events, media metadata, tags), authentication, storage management, and authorization.
3. **Face Engine**: Independent Python FastAPI application responsible for image decoding, face detection, face quality validation, embedding creation, and Qdrant search.
4. **NLP Engine**: Independent Python FastAPI service handling document preprocessing, OCR, entity extraction (NER), text normalization, and fuzzy name matching.
