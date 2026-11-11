# Architecture Overview

Perturix follows strict Clean Architecture principles and SOLID design patterns. The application is composed of heavily decoupled modules bound together through Dependency Injection.

## High-Level Flow
1. **Frontend**: React SPA using Vite, TailwindCSS, and a custom Fetch API client.
2. **API Controllers (`app.api.v1`)**: Thin FastAPI routers handling HTTP lifecycle, validation, and standard response wrapping.
3. **Application Services (`AttackWorkflowService`)**: Orchestrates cross-domain logic (Upload -> Attack -> Evaluate -> Persist).
4. **AI Engine Core (`app.ai_engine`)**: Protocol-driven plugin architecture. The `PipelineExecutor` executes algorithms loaded via `AttackRegistry`. All internal operations run on agnostic `torch.Tensor` structures.
5. **Evaluation Engine (`app.evaluation`)**: Independent metric computation plugin system (SSIM, PSNR, LPIPS) comparing Clean vs Adversarial tensors.
6. **Persistence Layer (`app.history`)**: SQLAlchemy-driven SQLite data store leveraging the Repository Pattern (`ProcessingSessionRepository`). Separates database mapping from business domain models.

## Design Patterns
- **Dependency Injection**: Root `dependencies/*.py` modules wire components.
- **Repository Pattern**: Centralizes database interactions.
- **Strategy Pattern**: Applied heavily in `AttackRegistry` and `EvaluationEngine` where plugins conform to `BaseAttack` and `BaseMetric`.
- **Global Error Handling**: Custom `PerturixException` intercepted by standard Exception Middleware.
