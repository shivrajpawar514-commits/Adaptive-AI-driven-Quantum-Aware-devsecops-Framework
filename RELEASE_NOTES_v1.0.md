# Release Notes v1.0.0

## Features
- **Deterministic Prioritization Engine**: Rule-based scoring with configurable weights.
- **Baseline Benchmarking Module**: Includes FIFO, Severity, URS, and Recovery prioritization comparison runners.
- **Matplotlib Plot Plotters**: Automatically exports PNG and SVG comparison curves.
- **Explainability breakdowns**: Exposes scoring component details inside API contracts.

## Known Limitations
- **Docker Verification**: **PENDING** due to local daemon unavailability.
- **Database Telemetry**: MongoDB queries are validated via mock fallbacks when offline.
