# Metis — Sprint Task Tracker

---

## Phase 1: PostgreSQL + JWT Auth
> **Note**: Active backend is `server/` (not `backend/`). `run_server.py` runs `server.app:app`.
- [x] 1.1 Create SQLAlchemy ORM models (`server/database/models.py`)
- [x] 1.2 Create async DB connection factory + config (`server/database/connection.py`, `server/config.py`)
- [x] 1.3 Set up Alembic migrations (`server/database/migrations/`) — using `init_db()` for now
- [x] 1.4 Replace Firebase auth with JWT (`server/auth.py`)
- [x] 1.5 Create user repository (`server/repositories/user_repository.py`)
- [x] 1.6 Create job repository (`server/repositories/job_repository.py`)
- [x] 1.7 Create result repository (`server/repositories/result_repository.py`)
- [x] 1.8 Rewrite `server/app.py` — remove Firebase, wire JWT + SQLAlchemy + new endpoints
- [x] 1.9 Remove/archive old `backend/` directory and `server/storage.py`
- [x] 1.10 Update `requirements.txt` — add SQLAlchemy/JWT, remove Firebase
- [x] 1.11 Update `run_server.py` for new setup
- [x] 1.12 Verify: backend starts, register/login/upload/history all work

---

## Phase 2: Fine-Tuned PII Detection Model
- [x] 2.1 Create Colab notebook for DeBERTa fine-tuning (`ml/notebooks/train_pii_ner.ipynb`)
- [x] 2.2 Build synthetic PII data generator (`ml/training/generate_synthetic_pii.py`)
- [x] 2.3 Train model on Colab (T4 GPU), export to `ml/models/pii-deberta-v3/`
- [x] 2.4 Update NER detector to load fine-tuned model (`detectors/ner_detector.py`)
- [x] 2.5 Build ensemble detector — regex + NER merge (`detectors/ensemble_detector.py`)
- [x] 2.6 Create model evaluation benchmark (`ml/training/evaluate_model.py`)
- [x] 2.7 Verify: run benchmark, record F1 scores for resume

---

## Phase 3: Docker Compose Containerization
- [x] 3.1 Create `Dockerfile.backend` (multi-stage, with Tesseract)
- [x] 3.2 Create `Dockerfile.frontend` (multi-stage, nginx serve)
- [x] 3.3 Create `docker-compose.yml` (5 services: db, redis, backend, worker, frontend)
- [x] 3.4 Create `nginx.conf` (reverse proxy)
- [x] 3.5 Create `.env.example` (all env vars documented)
- [/] 3.6 Verify: `docker compose up --build` brings everything up cleanly

---

## Phase 4: API Latency Optimization
- [x] 4.1 Create latency benchmark script (`benchmarks/latency_benchmark.py`)
- [x] 4.2 Run BEFORE benchmark, save `benchmarks/before.json`
- [x] 4.3 Implement Redis caching layer (`backend/cache.py`)
- [x] 4.4 Implement Celery async workers (`backend/tasks.py`)
- [x] 4.5 Implement WebSocket real-time updates (`backend/websocket.py`)
- [x] 4.6 Modify `POST /process` to return 202 + async job
- [x] 4.7 Run AFTER benchmark, save `benchmarks/after.json`
- [x] 4.8 Generate comparison report with % improvement

---

## Phase 5: Comprehensive Testing
- [ ] 5.1 Set up pytest framework (`tests/conftest.py`, fixtures)
- [ ] 5.2 Write unit tests (extractors, masking, auth, models)
- [ ] 5.3 Write integration tests (API flow, pipeline, database)
- [ ] 5.4 Write accuracy tests (PII detection P/R/F1, extraction fidelity)
- [ ] 5.5 Write performance tests (latency assertions, concurrency)
- [ ] 5.6 Verify: `pytest --cov` passes with 95%+ coverage

---

## Phase 6: YOLO Logo Detection
- [ ] 6.1 Create Colab notebook for YOLOv8 fine-tuning (`ml/notebooks/train_logo_detector.ipynb`)
- [ ] 6.2 Train on Colab, export ONNX model
- [ ] 6.3 Update `detectors/logo_redactor.py` with YOLO inference path
- [ ] 6.4 Verify: logo detection works on test images with confidence scores

---

## Phase 7: Frontend Overhaul
- [ ] 7.1 Set up React Router v6, AuthContext, ProtectedRoute
- [ ] 7.2 Build Login + Register pages with JWT flow
- [ ] 7.3 Build Dashboard page (stats cards, recent activity)
- [ ] 7.4 Build Upload page (drag-drop, progress bar, WebSocket status)
- [ ] 7.5 Build History page (paginated table, filters, sorting)
- [ ] 7.6 Build Result page (side-by-side original vs masked viewer)
- [ ] 7.7 Build Analytics page (PII distribution charts, processing times)
- [ ] 7.8 Design polish (dark mode, glassmorphism, animations, responsive)
- [ ] 7.9 Verify: full user flow works end-to-end through UI
