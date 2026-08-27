# DevSecOps SOAR Framework API Reference

This document describes the API endpoints exposed by the framework microservices.

---

## 1. REST Endpoints

### `GET, HEAD` /openapi.json
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `GET, HEAD` /docs
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `GET, HEAD` /docs/oauth2-redirect
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `GET, HEAD` /redoc
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `GET` /health
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `POST` /automation/execute
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `POST` /automation/optimize
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `GET` /automation/history
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)

### `POST` /automation/rollback
- **Description**: No description provided.
- **Status Codes**: 200 (Success), 404 (Not Found), 500 (Internal Error)



---

## 2. Response Schema Inclusions

All optimization endpoints return the following standard metadata parameters:
- `optimizerMetadata`: Contains `name`, `version`, `type`, and `deterministic` flags.
- `scoreBreakdown`: Tracks raw parameters contributions (`severity`, `urs`, `recovery`, `policy`, `confidence`, `disruptionPenalty`, `executionPenalty`, `finalScore`).
- `selectedBecause`: Rationale explanation strings.
