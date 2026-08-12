# Workstream Ownership & Responsibilities

This document defines team member ownership across the four core workstreams in Picaxe.

---

## 🎨 1. FRONTEND
- **Owner**: Sarthak Mittal
- **Directory**: [`apps/frontend`](file:///c:/Coding/picaxe/apps/frontend)
- **Tech Stack**: Next.js 16, React 19, Tailwind CSS, Framer Motion, Lucide Icons
- **Responsibilities**:
  - UI design and user experience for Students, Organizations, and Admins.
  - Page routes, responsive layouts, photo galleries, upload workflows.
  - Integration with backend REST API.

---

## ⚙️ 2. BACKEND GATEWAY
- **Owner**: Kirthi Vasan
- **Directory**: [`apps/backend`](file:///c:/Coding/picaxe/apps/backend)
- **Tech Stack**: NestJS, TypeScript, Prisma ORM, PostgreSQL, JWT Authentication
- **Responsibilities**:
  - User authentication, authorization, role-based guards.
  - Database schemas & migrations (PostgreSQL via Prisma).
  - Object storage abstraction (Cloudflare R2 / AWS S3 pre-signed URLs).
  - API orchestration between Frontend, Face Engine, and NLP Engine.

---

## 👤 3. PICAXE FACE ENGINE
- **Owner**: Arpit Singh
- **Directory**: [`apps/face-engine`](file:///c:/Coding/picaxe/apps/face-engine)
- **Tech Stack**: Python 3.11, FastAPI, OpenCV, InsightFace / ArcFace, Qdrant
- **Responsibilities**:
  - Face detection & image quality validation.
  - Face embedding generation (512-dim vector).
  - Qdrant similarity matching and indexing.

---

## 📜 4. PICAXE NLP ENGINE
- **Owner**: Daksh Choudhery
- **Directory**: [`apps/nlp-engine`](file:///c:/Coding/picaxe/apps/nlp-engine)
- **Tech Stack**: Python 3.11, FastAPI, OCR (Tesseract / EasyOCR), NLP (spaCy / RapidFuzz)
- **Responsibilities**:
  - Certificate image & PDF preprocessing.
  - Text extraction (OCR) and text cleanup.
  - Named entity extraction (student names) and fuzzy candidate matching.

---

## 📄 5. DOCUMENTATION & PROJECT MANAGEMENT
- **Owner**: Team Member 1
- **Directory**: [`docs/`](file:///c:/Coding/picaxe/docs)
- **Responsibilities**:
  - API contract governance and documentation updates.
  - System architecture standards and workstream alignment.
