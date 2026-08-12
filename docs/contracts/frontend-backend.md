# API Contract: Frontend ↔ Backend

This document defines the REST API contract between the Next.js Frontend (`apps/frontend`) and the NestJS Backend Gateway (`apps/backend`).

## Base URL
- **Local Development**: `http://localhost:3001`
- **Production**: `https://api.picaxe.com`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Registers a new user (Student or Organization).

- **Request Body**:
  ```json
  {
    "email": "student@university.edu",
    "password": "SecurePassword123!",
    "displayName": "John Doe",
    "role": "STUDENT"
  }
  ```
- **Response Body (`201 Created`)**:
  ```json
  {
    "id": "usr_94829103",
    "displayName": "John Doe",
    "email": "student@university.edu",
    "role": "STUDENT",
    "accessToken": "eyJhbGciOiJIUzI1Ni...",
    "refreshToken": "eyJhbGciOiJIUzI1Ni..."
  }
  ```

---

### `POST /auth/login`
Authenticates a user and returns JWT credentials.

- **Request Body**:
  ```json
  {
    "email": "student@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response Body (`200 OK`)**:
  ```json
  {
    "accessToken": "eyJhbGciOiJIUzI1Ni...",
    "refreshToken": "eyJhbGciOiJIUzI1Ni...",
    "user": {
      "id": "usr_94829103",
      "displayName": "John Doe",
      "role": "STUDENT"
    }
  }
  ```

---

## 2. Event Endpoints

### `GET /events`
Retrieves public or accessible events for the current student/organization.

- **Headers**: `Authorization: Bearer <accessToken>`
- **Response Body (`200 OK`)**:
  ```json
  [
    {
      "id": "evt_12345",
      "title": "Hackathon 2026",
      "description": "Annual tech hackathon",
      "startDate": "2026-08-15T09:00:00Z",
      "status": "ACTIVE",
      "visibility": "PUBLIC"
    }
  ]
  ```

---

## 3. Error Standard

All error responses adhere to the RFC 7807 standard format:

```json
{
  "statusCode": 400,
  "message": ["email must be a valid email address"],
  "error": "Bad Request",
  "timestamp": "2026-08-12T23:00:00.000Z",
  "path": "/auth/register"
}
```
