# 🪓 Picaxe Monorepo

> **AI-Powered Event Media & Certificate Distribution Engine**

Picaxe is an intelligent media platform designed for events, hackathons, and organizations. It automatically indexes event photos and certificates using facial recognition and NLP-based OCR name matching, instantly delivering relevant media directly to participating students.

---

## 🏗️ Repository Architecture

The repository is organized into four decoupled workstreams under `apps/` alongside infrastructure and contract documentation:

```text
picaxe/
├── apps/
│   ├── frontend/            # Next.js 16 Web Application (Sarthak Mittal)
│   ├── backend/             # NestJS API Gateway & Prisma ORM (Kirthi Vasan)
│   ├── face-engine/         # Python FastAPI Computer Vision Service (Arpit Singh)
│   └── nlp-engine/          # Python FastAPI Certificate OCR Service (Daksh Choudhery)
│
├── infrastructure/          # Docker & Compose Configurations
├── docs/                    # Architecture, Contracts & AI Specifications
│   ├── contracts/           # OpenAPI / REST Inter-service Specifications
│   ├── architecture/        # System Topology & Design Diagrams
│   ├── ai/                  # CV & NLP Specs
│   └── project/             # Workstream Ownership Guidelines
│
├── package.json             # Root Monorepo Scripts
└── README.md                # Project Overview & Quickstart Guide
```

---

## 👥 Workstream Ownership

| Application | Technology Stack | Lead Owner | Directory |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js 16, React 19, Tailwind CSS | Sarthak Mittal | [`apps/frontend`](file:///c:/Coding/picaxe/apps/frontend) |
| **Backend Gateway** | NestJS, TypeScript, Prisma, PostgreSQL | Kirthi Vasan | [`apps/backend`](file:///c:/Coding/picaxe/apps/backend) |
| **Face Engine** | Python 3.11, FastAPI, OpenCV, Qdrant | Arpit Singh | [`apps/face-engine`](file:///c:/Coding/picaxe/apps/face-engine) |
| **NLP Engine** | Python 3.11, FastAPI, OCR, NLP | Daksh Choudhery | [`apps/nlp-engine`](file:///c:/Coding/picaxe/apps/nlp-engine) |
| **Docs & Governance**| Architecture & API Contracts | Team Member 1 | [`docs/`](file:///c:/Coding/picaxe/docs) |

---

## 🔌 Architectural Boundaries

```text
Frontend (Next.js)
       │
       ▼
Backend Gateway (NestJS)
  ├── PostgreSQL (Entities & Metadata)
  ├── Cloudflare R2 / AWS S3 (Object Storage)
  │
  ├──► Face Engine (FastAPI) ──► Qdrant Vector DB
  │
  └──► NLP Engine (FastAPI)  ──► OCR & NER Pipeline
```

- **Frontend** communicates solely with the **Backend Gateway** over REST APIs.
- **Backend Gateway** is the single source of truth for users, events, roles, access permissions, and media metadata.
- **Face Engine** handles face detection, embedding creation (512-dim vectors), and vector searching on Qdrant.
- **NLP Engine** handles document OCR, text extraction, student name parsing, and fuzzy candidate matching.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Node.js**: `v20.x` or later
- **Python**: `3.11.x` or later
- **Docker**: For running PostgreSQL, Redis, and Qdrant locally

### 2. Environment Configuration
Each service contains a dedicated `.env.example` file. Copy these templates into your local environment:

```powershell
cp apps/frontend/.env.example apps/frontend/.env.local
cp apps/backend/.env.example apps/backend/.env
cp apps/face-engine/.env.example apps/face-engine/.env
cp apps/nlp-engine/.env.example apps/nlp-engine/.env
```

### 3. Local Infrastructure (Docker)
Start PostgreSQL, Redis, and Qdrant:

```powershell
docker-compose up -d
```

### 4. Database Setup (Prisma)
From the root directory, push the database schema to your local PostgreSQL or Supabase instance:

```powershell
cd apps/backend
npx prisma db push
npx prisma generate
```

### 5. Running the Applications

- **Start Frontend**:
  ```powershell
  npm run dev:frontend
  ```
  App runs at `http://localhost:3000`

- **Start Backend Gateway**:
  ```powershell
  npm run dev:backend
  ```
  API runs at `http://localhost:3001`

- **Start Face Engine**:
  ```powershell
  cd apps/face-engine
  uvicorn app.main:app --reload --port 8000
  ```
  API runs at `http://localhost:8000`

- **Start NLP Engine**:
  ```powershell
  cd apps/nlp-engine
  uvicorn app.main:app --reload --port 8001
  ```
  API runs at `http://localhost:8001`

---

## 🧪 Testing & Verification

- **Backend Unit Tests**:
  ```powershell
  npm run test:backend
  ```

- **Frontend Production Build**:
  ```powershell
  npm run build:frontend
  ```

- **Backend Production Build**:
  ```powershell
  npm run build:backend
  ```

---

## 📑 API Contracts & Documentation
Detailed inter-service contracts and design specs are documented under [`docs/`](file:///c:/Coding/picaxe/docs):
- [Frontend ↔ Backend Contract](file:///c:/Coding/picaxe/docs/contracts/frontend-backend.md)
- [Backend ↔ Face Engine Contract](file:///c:/Coding/picaxe/docs/contracts/backend-face-engine.md)
- [Backend ↔ NLP Engine Contract](file:///c:/Coding/picaxe/docs/contracts/backend-nlp-engine.md)
- [Workstream Ownership](file:///c:/Coding/picaxe/docs/project/workstreams.md)
