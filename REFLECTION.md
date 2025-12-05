# Reflection

## Feature Added
- Implemented the Exponent (Power) calculation across the backend models, schemas, and frontend dashboard so users can enter a base/exponent pair and see the computed result stored alongside the other BREAD operations.
- Added Playwright E2E coverage for the power workflow (successful and validation) plus unit/integration tests to make sure the calculation logic and schemas behave the same as the rest of the system.

## Issues / Challenges
- The authentication layer depended on `aioredis`, which imports `distutils.version` and declared a `TimeoutError` that conflicts on Python 3.12. To keep registration/login working inside the tests and Docker, I introduced a minimal shim under `distutils/` that exposes `StrictVersion`/`LooseVersion` and made the redis helpers handle the absence of `aioredis` gracefully.
- Running the Playwright tests required installing the Chromium browser (`python -m playwright install`) and ensuring the server fixture started cleanly despite the extra exponent UI elements.

## Testing Approach
- `python3 -m pytest` runs the entire suite (unit + integration + E2E) and now succeeds on this branch, covering the new exponent cases as well as the legacy BREAD flows.
- Playwright tests (`tests/e2e/test_power_ui.py`) log in through the UI, perform valid/invalid exponent calculations, and assert that the history table and alerts behave as expected.

## CI/CD & Docker
- The GitHub Actions workflow (`.github/workflows/test.yml`) installs dependencies, runs `python3 -m pytest`, builds an intermediate Docker image, scans it with Trivy, and only pushes to Docker Hub after tests and the scan succeed.
- Docker builds use the existing `Dockerfile` (Python 3.10 slim base) and now work with the distutils/ aioredis shims. The published image is `solaimon/module14_is601:latest` (with SHA tags) on Docker Hub.
