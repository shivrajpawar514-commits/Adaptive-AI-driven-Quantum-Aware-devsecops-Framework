# Repository Coding Standards

This document establishes the syntax, naming, environmental, and testing standards required for the repository to maintain production-grade quality.

---

## 1. Directory & File Naming
- **Directories**: Always lowercase with hyphens (e.g. `auth-service`, `monitoring-service`).
- **Source Files**:
  - Node.js/JavaScript: CamelCase for React component files (e.g. `SecurityDashboard.jsx`), camelCase for standard JS scripts (e.g. `tokenValidator.js`).
  - Python: snake_case (e.g. `autoencoder_model.py`).
  - Ansible: snake_case for playbooks and tasks (e.g. `isolate_pod.yml`).
  - Terraform: snake_case (e.g. `network_security.tf`).

---

## 2. Variables & Functions
- **JavaScript/Node.js**:
  - Variables/Functions: camelCase (e.g. `const riskScore = calculateScore()`).
  - Constants: UPPERCASE with underscores (e.g. `const MAX_RETRY_COUNT = 3`).
- **Python**:
  - Variables/Functions: snake_case (e.g. `def compute_loss(features):`).
  - Classes: PascalCase (e.g. `class PCAFeatureEngineering:`).

---

## 3. Conventional Commit Naming
All commits must match SemVer conventional types:
`feat(module): add...`, `fix(module): resolve...`, `docs(module): update...` (see [Git-Workflow.md](file:///C:/Users/HP/.gemini/antigravity-ide/scratch/Adaptive-AI-Driven-Quantum-Aware-DevSecOps-Framework/docs/Git-Workflow.md)).

---

## 4. REST API Guidelines
- **HTTP Methods**: Use GET for queries, POST for actions/creations, PUT for updates, DELETE for removals.
- **Prefix**: All resource endpoints must use prefix `/api/v1` (e.g., `/api/v1/predict`).
- **Status Codes**:
  - `200 OK`: Successful fetch or simple task completion.
  - `201 Created`: Successful creation (user register).
  - `400 Bad Request`: Payload validation fails.
  - `401 Unauthorized`: Token missing or ECC signature invalid.
  - `403 Forbidden`: Insufficient role scopes (auditor trying to block nodes).
  - `500 Internal Server Error`: Application level crash.
- **Payload Envelopes**: All responses must return structured JSON:
  ```json
  {
    "status": "success",
    "data": {}
  }
  ```

---

## 5. Database Conventions
- **Collections**: Lowercase, singular naming (e.g. `user`, `threat_event`).
- **Foreign Keys**: Suffixed with `_id` (e.g. `threat_event_id`).
- **Indexes**: Explicitly create lookup indexes on query fields (`timestamp`, `username`) during database startup.

---

## 6. Containerization & Env Configuration
- **Docker Files**: Docker images must be based on secure, minimal bases (e.g. `node:18-alpine`, `python:3.10-slim`). Image labels should be lowercase: `framework/ai-engine:latest`.
- **Environment Variables**: Managed using `.env` files, excluded from Git. A `.env.example` file must be provided in each module detailing required tokens:
  ```env
  MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=devsecops
  PORT=5000
  JWT_SECRET=super_secret_key
  ```

---

## 7. Logging & Error Handling
- **Logs**: Do not use `console.log()` in production modules. Implement a unified JSON logger outputting `timestamp`, `level` (INFO, WARN, ERROR), `module`, and `message`.
- **Errors**: Catch all exceptions explicitly. Never expose raw stack traces to client API endpoints. Return normalized error payloads:
  ```json
  {
    "status": "error",
    "message": "Valid ECC signature required"
  }
  ```

---

## 8. Documentation & Testing
- **Docstrings**: Provide JSDoc annotations for JavaScript APIs and Sphinx/Google docstrings for Python methods.
- **Unit Tests**: Minimum 80% code coverage. Jest is utilized for JS routes testing; pytest is utilized for Python analytics code.
- **Mocks**: Database connections and network sockets must be mocked during unit test runs to ensure tests remain self-contained.
