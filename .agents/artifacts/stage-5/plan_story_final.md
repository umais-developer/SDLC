# Stage 5: Implementation Plan
## Prescription Data Capture: Automated Intake of Prescription Reports from Email

**Project Size:** LARGE (Greenfield, 15 FRs, 10 NFRs, 6 constraints)  
**System Type:** Batch processing pipeline with REST monitoring interfaces  
**Delivery Timeframe:** 8 weeks (100 story points at 12.5 pts/week)

---

## Executive Summary

This Stage 5 Implementation Plan decomposes **13 user stories** (100 story points) across **5 epics** into **28 concrete file-level implementation tasks** with explicit dependencies and verifiable definitions of done.

**Approach:**
- **Vertical Slice 1 (VS-1, Weeks 1-3):** Foundation Intake Pipeline—complete end-to-end batch processing with scheduled runs, extraction, dedup, and audit logging. Enables 11 FRs. Demo: run scheduled intake and show persisted audit records with zero duplicates.
- **Vertical Slices 2-5 (Expansion Phase, Weeks 4-8):** Four parallel tracks—Operations Monitoring, Historical Load, Audit Queries, Data Verification.

**Quality Gates:**
- Each task includes explicit test paths and verifiable definitions of done (pytest commands)
- Dependency graph is acyclic with execution order for Phase 1 (sequential foundation) and Phase 2 (parallelizable tracks)
- All tasks reference specific file paths consistent with `components.json`
- No task estimates (PRD does not require them); all effort is implicit in dependencies

---

## 28 Implementation Tasks

### **Foundation Phase (Weeks 1-3, Vertical Slice 1)**

#### **Configuration & Dependencies (Tasks T-23 to T-27)**

**T-23 — Create runtime configuration module**
- **File:** `src/orchestration/config.py` (create)
- **Story:** STORY-1-1 (Foundation Intake Monitoring)
- **Description:** Env-driven config loader for VAULT_ADDR, DB_CONNECTION, GRAPH_TENANT_ID, DAILY_RUN_TIME, feature flags with validation
- **Depends On:** None
- **Tests:**
  - `tests/unit/test_config.py: required env var validation`
  - `tests/unit/test_config.py: defaults and type parsing`
- **Definition of Done:** `pytest tests/unit/test_config.py -q` passes and invalid environment raises actionable errors
- **Links:** FR-15, NFR-6, CON-4, GOAL-1

**T-25 — Create dependency manifest**
- **File:** `requirements.txt` (create)
- **Story:** STORY-1-1
- **Description:** Pin runtime and test dependencies (python-dotenv, azure-identity, microsoft-graph-core, pdfplumber, sqlalchemy, psycopg2-binary, apscheduler, hvac, structlog, flask)
- **Depends On:** None
- **Tests:**
  - `tests/integration/test_dependencies.py: import critical modules`
  - `tests/integration/test_dependencies.py: dependency version compatibility smoke`
- **Definition of Done:** `pytest tests/integration/test_dependencies.py -q` passes and required imports succeed in CI image
- **Links:** FR-1, FR-3, FR-4, FR-15, NFR-1, NFR-6, GOAL-1

**T-27 — Create pytest fixtures and shared mocks**
- **File:** `tests/conftest.py` (create)
- **Story:** STORY-5-1 (Data Accuracy)
- **Description:** Fixtures for mocked Vault, Graph SDK, ephemeral test DB, mock email, and sample PDF corpus (50+ malformed examples for NFR-9)
- **Depends On:** T-25
- **Tests:**
  - `tests/conftest.py: fixture bootstrap smoke via pytest collection`
  - `tests/unit/test_pdf_extraction_engine.py: fixture-backed pdf samples`
- **Definition of Done:** `pytest --collect-only -q` succeeds and fixture-dependent unit tests execute without setup failures
- **Links:** FR-3, FR-13, NFR-9, GOAL-3

**T-24 — Create structured logging setup**
- **File:** `src/orchestration/logging_setup.py` (create)
- **Story:** STORY-3-4 (Audit Trail Export)
- **Description:** Configure structlog JSON logging with run_id, date, status, email_id, record_count dimensions for operations and audit queries
- **Depends On:** T-27
- **Tests:**
  - `tests/unit/test_logging_setup.py: json logging envelope`
  - `tests/unit/test_logging_setup.py: required context fields present`
- **Definition of Done:** `pytest tests/unit/test_logging_setup.py -q` passes and logs include query dimensions used by audit endpoints
- **Links:** FR-9, FR-10, NFR-8, NFR-10, GOAL-4

#### **Core Infrastructure (Tasks T-1 to T-12)**

**T-1 — Implement SecretsProvider Vault integration**
- **File:** `src/infrastructure/secrets_provider.py` (create)
- **Story:** STORY-4-1 (Restart Safety—Email State Tracking)
- **Description:** SecretsProvider with get_mailbox_credentials(), get_database_credentials(), rotate_credentials(), is_credentials_expiring_soon()
- **Depends On:** T-23, T-27
- **Tests:**
  - `tests/unit/test_secrets_provider.py: vault auth success/failure`
  - `tests/unit/test_secrets_provider.py: credential rotation and ttl checks`
- **Definition of Done:** `pytest tests/unit/test_secrets_provider.py -q` passes and Vault credential retrieval paths are covered
- **Links:** FR-1, FR-4, NFR-6, CON-4, CON-6, GOAL-2
- **Components:** SecretsProvider

**T-2 — Implement MailboxConnector Graph integration**
- **File:** `src/integrations/mailbox_connector.py` (create)
- **Story:** STORY-2-1 (Historical Load Capability)
- **Description:** MailboxConnector with connect(), disconnect(), retrieve_emails(start_date, end_date), is_connected() using Graph SDK
- **Depends On:** T-1
- **Tests:**
  - `tests/unit/test_mailbox_connector.py: connect/disconnect lifecycle`
  - `tests/unit/test_mailbox_connector.py: bounded date range retrieval`
- **Definition of Done:** `pytest tests/unit/test_mailbox_connector.py -q` passes with Graph SDK mocked and mailbox scope enforced
- **Links:** FR-1, FR-12, NFR-2, CON-1, CON-4, GOAL-1
- **Components:** MailboxConnector

**T-3 — Implement EmailNewIdentifier dedup tracking**
- **File:** `src/business_logic/email_new_identifier.py` (create)
- **Story:** STORY-4-1 (Restart Safety—Email State Tracking)
- **Description:** EmailNewIdentifier with identify_new_emails(), mark_email_processed(), is_email_already_processed() for processed-email filtering
- **Depends On:** T-27
- **Tests:**
  - `tests/unit/test_email_new_identifier.py: identify new vs processed ids`
  - `tests/unit/test_email_new_identifier.py: mark and lookup processed emails`
- **Definition of Done:** `pytest tests/unit/test_email_new_identifier.py -q` passes including duplicate email filtering cases
- **Links:** FR-2, FR-11, NFR-4, NFR-5, GOAL-3
- **Components:** EmailNewIdentifier

**T-7 — Implement PDFExtractionEngine core extraction**
- **File:** `src/business_logic/pdf_extraction_engine.py` (create)
- **Story:** STORY-5-1 (Data Accuracy—Format Anomalies)
- **Description:** PDFExtractionEngine with extract_fields(), validate_pdf_format(), detect_format_change() for 23-field extraction with anomaly hooks
- **Depends On:** T-27
- **Tests:**
  - `tests/unit/test_pdf_extraction_engine.py: extract 23 fields from canonical PDFs`
  - `tests/unit/test_pdf_extraction_engine.py: malformed format detection`
- **Definition of Done:** `pytest tests/unit/test_pdf_extraction_engine.py -q` passes including malformed PDF detection cases
- **Links:** FR-3, FR-13, NFR-3, NFR-9, CON-2, GOAL-3
- **Components:** PDFExtractionEngine

**T-8 — Implement DataValidator field and key validation**
- **File:** `src/business_logic/data_validator.py` (create)
- **Story:** STORY-5-2 (Data Accuracy—Captured Records)
- **Description:** DataValidator with validate_prescription_fields(), is_field_present(), validate_composite_key() for completeness checks
- **Depends On:** T-27
- **Tests:**
  - `tests/unit/test_data_validator.py: required 23-field validation`
  - `tests/unit/test_data_validator.py: composite key validity checks`
- **Definition of Done:** `pytest tests/unit/test_data_validator.py -q` passes and all required field checks are asserted
- **Links:** FR-3, NFR-3, GOAL-2
- **Components:** DataValidator

**T-9 — Create PostgreSQL schema for prescriptions and audits**
- **File:** `src/persistence/schema.sql` (create)
- **Story:** STORY-4-1 (Restart Safety—Email State Tracking)
- **Description:** Create tables—prescriptions (with composite unique key on prescription_number + dispensing_date), run_audit, email_audit, processed_emails with indexes and constraints
- **Depends On:** T-27
- **Tests:**
  - `tests/integration/test_schema.py: schema migrations apply cleanly`
  - `tests/integration/test_schema.py: unique and fk constraints enforced`
- **Definition of Done:** `pytest tests/integration/test_schema.py -q` passes and composite key constraint prevents duplicate inserts
- **Links:** FR-4, FR-5, FR-10, FR-14, NFR-4, NFR-8, CON-3, CON-5, GOAL-4
- **Components:** PrescriptionRepository, AuditLogger, JobStateManager

**T-28 — Create integration test helper toolkit**
- **File:** `tests/integration/helpers.py` (create)
- **Story:** STORY-2-3 (Historical Load—Safe Restart)
- **Description:** DB setup/teardown, Graph response simulation, mail payload builders, run interruption simulation helpers
- **Depends On:** T-27, T-9
- **Tests:**
  - `tests/integration/helpers.py: helper unit smoke`
  - `tests/integration/test_restart_safety.py: helper-driven interruption simulation`
- **Definition of Done:** `pytest tests/integration/test_restart_safety.py -q` runs using helpers and reproduces interruption/resume deterministically
- **Links:** FR-7, FR-11, NFR-5, GOAL-3
- **Components:** IntakeOrchestrator, JobStateManager, PrescriptionRepository

**T-4 — Implement AuditLogger foundation CRUD**
- **File:** `src/persistence/audit_logger.py` (create)
- **Story:** STORY-3-1 (Audit Trail—Query Interface)
- **Description:** AuditLogger with create_run_record(), record_email_processed(), finalize_run_record(), query_run_records(), query_email_records() for audit querying and compliance
- **Depends On:** T-9, T-28, T-24
- **Tests:**
  - `tests/unit/test_audit_logger.py: run record create/finalize`
  - `tests/unit/test_audit_logger.py: query by date/status/sender`
- **Definition of Done:** `pytest tests/unit/test_audit_logger.py -q` passes and queryable audit fields are asserted
- **Links:** FR-9, FR-10, FR-14, NFR-8, NFR-10, GOAL-4
- **Components:** AuditLogger

**T-5 — Implement PrescriptionRepository upsert and dedup**
- **File:** `src/persistence/prescription_repository.py` (create)
- **Story:** STORY-4-3 (Restart Safety—Zero Duplicates)
- **Description:** PrescriptionRepository with store_or_update(), find_by_composite_key(), get_all_prescriptions(), bulk_upsert() with composite-key dedup semantics
- **Depends On:** T-9, T-28
- **Tests:**
  - `tests/unit/test_prescription_repository.py: insert/update/upsert paths`
  - `tests/unit/test_prescription_repository.py: composite-key duplicate suppression`
- **Definition of Done:** `pytest tests/unit/test_prescription_repository.py -q` passes and duplicate reprocessing keeps one record per composite key
- **Links:** FR-4, FR-5, FR-6, NFR-3, NFR-4, CON-3, CON-5, GOAL-3
- **Components:** PrescriptionRepository

**T-6 — Implement JobStateManager state lifecycle**
- **File:** `src/business_logic/job_state_manager.py` (create)
- **Story:** STORY-4-1 (Restart Safety—Email State Tracking)
- **Description:** JobStateManager with initialize_run_state(), get_resumption_point(), mark_email_as_processed(), finalize_run_state() for persistent state and restart checkpoints
- **Depends On:** T-5
- **Tests:**
  - `tests/unit/test_job_state_manager.py: state init/finalize`
  - `tests/unit/test_job_state_manager.py: resumption point recovery`
- **Definition of Done:** `pytest tests/unit/test_job_state_manager.py -q` passes and restart checkpoints are persisted per email
- **Links:** FR-7, FR-8, FR-11, NFR-5, GOAL-3
- **Components:** JobStateManager

**T-10 — Implement IntakeOrchestrator foundation flows**
- **File:** `src/orchestration/intake_orchestrator.py` (create)
- **Story:** STORY-1-1 (Daily Intake Operations Monitoring)
- **Description:** IntakeOrchestrator with run_historical_load(), run_daily_intake(), execute_intake_job() coordinating mailbox retrieval, extraction, validation, persistence, audit logging
- **Depends On:** T-1, T-2, T-3, T-4, T-5, T-6, T-7, T-8
- **Tests:**
  - `tests/integration/test_intake_orchestrator.py: end-to-end orchestration happy path`
  - `tests/integration/test_intake_orchestrator.py: run status and metrics persistence`
- **Definition of Done:** `pytest tests/integration/test_intake_orchestrator.py -q` passes with mocked Graph and test Postgres
- **Links:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-13, FR-15, NFR-1, NFR-2, GOAL-1, GOAL-3, GOAL-4
- **Components:** IntakeOrchestrator

**T-11 — Implement APSchedulerJobRunner scheduling**
- **File:** `src/orchestration/apscheduler_job_runner.py` (create)
- **Story:** STORY-1-1 (Daily Intake Operations Monitoring)
- **Description:** APSchedulerJobRunner with start_scheduler(), stop_scheduler(), schedule_daily_run(), get_scheduled_jobs() with persistent scheduler config
- **Depends On:** T-10
- **Tests:**
  - `tests/integration/test_apscheduler_job_runner.py: daily schedule registration`
  - `tests/integration/test_apscheduler_job_runner.py: scheduler restart persistence`
- **Definition of Done:** `pytest tests/integration/test_apscheduler_job_runner.py -q` passes with scheduler lifecycle assertions
- **Links:** FR-7, FR-8, FR-15, NFR-1, GOAL-1
- **Components:** APSchedulerJobRunner

**T-12 — Create application entrypoint and graceful shutdown**
- **File:** `src/orchestration/application_entry.py` (create)
- **Story:** STORY-1-1 (Daily Intake Operations Monitoring)
- **Description:** Wire configuration, scheduler startup, signal handlers (SIGTERM), graceful shutdown behavior for unattended runtime
- **Depends On:** T-11
- **Tests:**
  - `tests/e2e/test_main_startup.py: boot and scheduler start`
  - `tests/e2e/test_main_startup.py: SIGTERM graceful shutdown`
- **Definition of Done:** `pytest tests/e2e/test_main_startup.py -q` passes and process exits cleanly on signal
- **Links:** FR-15, NFR-1, GOAL-1
- **Components:** APSchedulerJobRunner, IntakeOrchestrator

**T-26 — Create GitHub Actions CI workflow**
- **File:** `.github/workflows/ci.yml` (create)
- **Story:** STORY-1-2 (Daily Intake Operations—Failure Alerting)
- **Description:** CI job for unit, integration, e2e test execution with coverage and static checks for merge gating
- **Depends On:** T-25
- **Tests:**
  - `.github/workflows/ci.yml: workflow syntax and job graph`
  - `tests/integration/test_dependencies.py: executed in CI pipeline`
- **Definition of Done:** `python -m yaml .github/workflows/ci.yml` succeeds and CI runs `pytest` suites without workflow errors
- **Links:** FR-15, NFR-1, GOAL-1
- **Components:** APSchedulerJobRunner, IntakeOrchestrator

### **Expansion Phase (Weeks 4-8, Vertical Slices 2-5)**

#### **Track A — Operations Monitoring & Recovery (Tasks T-13, T-14, T-17)**

**T-13 — Add monitoring dashboard routes and retry endpoint**
- **File:** `src/orchestration/dashboard_routes.py` (create)
- **Story:** STORY-1-4 (Daily Intake—Retry Transient Failures)
- **Description:** API endpoints GET /runs (list with filters), GET /runs/{id} (detail), POST /runs/{id}/retry for operations monitoring and targeted retry
- **Depends On:** T-12, T-4, T-10
- **Tests:**
  - `tests/integration/test_dashboard_routes.py: run list/detail filters`
  - `tests/integration/test_dashboard_routes.py: transient retry endpoint behavior`
- **Definition of Done:** `pytest tests/integration/test_dashboard_routes.py -q` passes for list/detail/retry route contracts
- **Links:** FR-8, FR-9, FR-10, FR-15, NFR-10, GOAL-1, GOAL-3
- **Components:** AuditLogger, IntakeOrchestrator, APSchedulerJobRunner

**T-14 — Implement failure alert dispatcher**
- **File:** `src/orchestration/alert_dispatcher.py` (create)
- **Story:** STORY-1-3 (Daily Intake—Display Failure Details)
- **Description:** PARTIAL/FAILED alert dispatch with transient/permanent failure classification and operator-ready message templates
- **Depends On:** T-13, T-4
- **Tests:**
  - `tests/unit/test_alert_dispatcher.py: PARTIAL and FAILED alert triggering`
  - `tests/unit/test_alert_dispatcher.py: transient/permanent classification`
- **Definition of Done:** `pytest tests/unit/test_alert_dispatcher.py -q` passes and alert payload fields match run metrics schema
- **Links:** FR-9, FR-10, NFR-10, GOAL-1, GOAL-4
- **Components:** AuditLogger, IntakeOrchestrator

**T-17 — Implement restart-safe resume behavior**
- **File:** `src/orchestration/intake_orchestrator.py` (modify)
- **Story:** STORY-4-2 (Restart Safety—Recover from Interruption)
- **Description:** Add interruption handling that records checkpoint state and resumes from first unprocessed email without duplicate writes
- **Depends On:** T-15, T-6, T-5, T-14
- **Tests:**
  - `tests/integration/test_restart_safety.py: interrupt at midpoint and resume`
  - `tests/integration/test_restart_safety.py: final dataset has zero duplicates`
- **Definition of Done:** `pytest tests/integration/test_restart_safety.py -q` passes with interruption/resume and zero-duplicate assertions
- **Links:** FR-7, FR-11, FR-15, NFR-4, NFR-5, GOAL-3
- **Components:** JobStateManager, PrescriptionRepository, AuditLogger, IntakeOrchestrator

#### **Track B — Historical Load & Progress (Tasks T-15, T-16)**

**T-15 — Add historical load controls to orchestrator**
- **File:** `src/orchestration/intake_orchestrator.py` (modify)
- **Story:** STORY-2-1 (Historical Load Capability—Trigger)
- **Description:** Extend run_historical_load(start_date) to estimate candidate email count, initialize historical mode state, write start markers to audit
- **Depends On:** T-12, T-10, T-4
- **Tests:**
  - `tests/integration/test_historical_load.py: start date bounded retrieval`
  - `tests/integration/test_historical_load.py: historical run metadata in audit`
- **Definition of Done:** `pytest tests/integration/test_historical_load.py -q` passes for one-time load setup and auditing
- **Links:** FR-7, FR-9, NFR-2, GOAL-2, GOAL-3
- **Components:** IntakeOrchestrator, AuditLogger, APSchedulerJobRunner

**T-16 — Implement real-time progress API**
- **File:** `src/orchestration/progress_api.py` (create)
- **Story:** STORY-2-2 (Historical Load—Real-time Progress Display)
- **Description:** GET /run/{id}/progress endpoint returning processed, total, elapsed, ETA based on orchestrator and audit state
- **Depends On:** T-13, T-15
- **Tests:**
  - `tests/integration/test_progress_api.py: progress shape and monotonic updates`
  - `tests/integration/test_progress_api.py: eta calculation sanity bounds`
- **Definition of Done:** `pytest tests/integration/test_progress_api.py -q` passes and endpoint reflects in-flight historical runs
- **Links:** FR-7, FR-9, NFR-1, GOAL-1
- **Components:** APSchedulerJobRunner, IntakeOrchestrator, AuditLogger

#### **Track C — Audit Trail Queries & Export (Tasks T-18, T-19)**

**T-18 — Implement audit query and drill-down routes**
- **File:** `src/orchestration/audit_routes.py` (create)
- **Story:** STORY-3-2 (Audit Trail—Email-level Drill-down)
- **Description:** GET /audit/runs filters, GET /audit/runs/{id}/emails drill-down, GET /audit/emails/{id} detail payload with traceability
- **Depends On:** T-13, T-4, T-12
- **Tests:**
  - `tests/integration/test_audit_routes.py: run-level filtering`
  - `tests/integration/test_audit_routes.py: email drill-down and detail`
- **Definition of Done:** `pytest tests/integration/test_audit_routes.py -q` passes for query and drill-down endpoints
- **Links:** FR-10, FR-14, NFR-8, GOAL-4
- **Components:** AuditLogger

**T-19 — Implement CSV export service for audit records**
- **File:** `src/orchestration/export_service.py` (create)
- **Story:** STORY-3-3 (Audit Trail—PDF Traceability) / STORY-3-4 (CSV Export)
- **Description:** CSV export for audit query result sets and background queue path for large exports
- **Depends On:** T-18
- **Tests:**
  - `tests/integration/test_csv_export.py: csv column order and formatting`
  - `tests/integration/test_csv_export.py: large export queuing behavior`
- **Definition of Done:** `pytest tests/integration/test_csv_export.py -q` passes and exported file format matches compliance template
- **Links:** FR-14, NFR-8, GOAL-4
- **Components:** AuditLogger

#### **Track D — Data Accuracy & Verification (Tasks T-20, T-21, T-22)**

**T-20 — Harden PDF format anomaly handling**
- **File:** `src/business_logic/pdf_extraction_engine.py` (modify)
- **Story:** STORY-5-1 (Data Accuracy—Detect Format Anomalies)
- **Description:** Enforce explicit failure on schema mismatch before extraction and emit structured anomaly details to audit logger hooks
- **Depends On:** T-7, T-4, T-12
- **Tests:**
  - `tests/integration/test_format_detection.py: malformed PDF suite detection (50+ PDFs)`
  - `tests/integration/test_format_detection.py: explicit failure reason propagation`
- **Definition of Done:** `pytest tests/integration/test_format_detection.py -q` passes with malformed PDFs all classified as explicit failures (100% detection per NFR-9)
- **Links:** FR-13, FR-3, NFR-9, NFR-3, CON-2, GOAL-3
- **Components:** PDFExtractionEngine, AuditLogger

**T-21 — Implement captured records query routes**
- **File:** `src/orchestration/records_routes.py` (create)
- **Story:** STORY-5-2 (Data Accuracy—View Captured Records)
- **Description:** GET /records and GET /records/{id} with date/prescriber filters and 23-field detail plus source traceability metadata
- **Depends On:** T-13, T-5, T-12
- **Tests:**
  - `tests/integration/test_records_routes.py: records list filters`
  - `tests/integration/test_records_routes.py: record detail includes source linkage`
- **Definition of Done:** `pytest tests/integration/test_records_routes.py -q` passes and detail payload includes all 23 fields with source references
- **Links:** FR-3, FR-10, NFR-3, NFR-8, GOAL-2, GOAL-4
- **Components:** PrescriptionRepository, AuditLogger

**T-22 — Implement verification audit trail service**
- **File:** `src/orchestration/verification_service.py` (create)
- **Story:** STORY-5-3 (Data Accuracy—Verification Sign-off)
- **Description:** Verification comment capture with operator_id, timestamp, verification status, retrieval hooks for compliance audit
- **Depends On:** T-21, T-4
- **Tests:**
  - `tests/integration/test_verification_service.py: comment recording`
  - `tests/integration/test_verification_service.py: verification records queryability`
- **Definition of Done:** `pytest tests/integration/test_verification_service.py -q` passes and verification records are retrievable by audit filters
- **Links:** FR-10, NFR-8, GOAL-4
- **Components:** AuditLogger

---

## Execution Order with Phase-Based Parallelization

### **Phase 1: Foundation (Weeks 1-3, Sequential)**

```
Layer 0 (no deps):
  [T-23] config.py ────┐
  [T-25] requirements  │

Layer 1 (deps on T-25):
  [T-27] conftest.py───┬─────────┐
                       │         │
                  [T-3] email    [T-7] pdf
                 id tracking    extraction
                       │         │
                  [T-8] validator┘
                       │
                  [T-1] secrets
                       │
                  [T-2] mailbox
                   (config)

Layer 2 (core services):
  [T-9] schema  [T-24] logging
     │              │
     └──────┬───────┘
            │
      [T-28] helpers
            │
     [T-4] audit logger

Layer 3 (persistence):
  [T-5] prescription repo
          │
    [T-6] job state mgr
          │
    [T-10] orchestrator ◄─── deps: T-1..T-8
            │
    [T-11] scheduler
            │
    [T-12] entrypoint
            │
    [T-26] CI workflow
```

**Execution Groups (sequential within group, parallelizable across groups):**

| Week | Group | Tasks | Goal |
|------|-------|-------|------|
| 1 | Group 1 | T-23, T-25 | Config and dependencies ready |
| 1 | Group 2 | T-27, T-3, T-7, T-8 | Test fixtures and 3 core libs (dedup, PDF, validator) |
| 1-2 | Group 3 | T-1, T-9, T-24 | Secrets, schema, logging setup |
| 2 | Group 4 | T-2, T-28 | Mailbox and test helpers |
| 2 | Group 5 | T-4, T-5 | Audit and prescription persistence |
| 2-3 | Group 6 | T-6, T-10, T-26 | State manager, orchestrator, CI |
| 3 | Group 7 | T-11 | Scheduler |
| 3 | Group 8 | T-12 | Application entrypoint |
| 3 | **Foundation Complete** | **VS-1 Ready** | **End-to-end batch pipeline working** |

### **Phase 2: Expansion (Weeks 4-8, Parallel Tracks)**

Once Foundation (Phase 1) is complete, execute 4 parallel tracks:

| Week | Track A | Track B | Track C | Track D |
|------|---------|---------|---------|---------|
| 4 | T-13 (dashboard) | T-15 (hist load) | T-18 (audit query) | T-20 (PDF hardening) |
| 5 | T-14 (alerts) | T-16 (progress) | T-19 (CSV export) | T-21 (records routes) |
| 6 | T-17 (restart) | ✅ Track B done | ✅ Track C done | T-22 (verification) |
| 7-8 | ✅ Track A done | — | — | ✅ Track D done |

---

## Vertical Slices for Incremental Delivery

### **Vertical Slice 1 (VS-1): Foundation Intake Pipeline**
**Phase:** Weeks 1-3  
**Stories:** STORY-4-1, STORY-1-1, STORY-5-1, STORY-3-1  
**Tasks:** T-23, T-25, T-27, T-1, T-2, T-3, T-7, T-8, T-9, T-28, T-4, T-5, T-6, T-24, T-10, T-11, T-12, T-26  
**Enables FRs:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-8, FR-9, FR-10, FR-11, FR-13, FR-15 (11 of 15)  

**Demo:** 
1. Run daily scheduled intake
2. Show run metrics (processed count, status, elapsed time)
3. Query audit trail for completed run
4. Verify 100 prescriptions stored without duplicates
5. Inspect captured record with all 23 fields

**Verifiable Outcomes:**
- ✅ All unit tests pass: `pytest tests/unit/ -q`
- ✅ All integration tests pass: `pytest tests/integration/ -q`
- ✅ CI workflow executes successfully
- ✅ Schedule persists across restart
- ✅ Duplicate suppression: reprocessing same email keeps 1 record

---

### **Vertical Slice 2: Operations Monitoring and Recovery**
**Phase:** Weeks 4-6  
**Stories:** STORY-1-2, STORY-1-3, STORY-1-4, STORY-2-3, STORY-4-2  
**Tasks:** T-13, T-14, T-17  
**Enables FRs:** FR-8, FR-9, FR-10, FR-11, FR-15 (5 FRs)  

**Demo:** 
1. Trigger a run that will fail partway through
2. Show PARTIAL alert in dashboard
3. View failure detail (which emails succeeded, which failed)
4. Click retry button to reprocess transient failures
5. Stop process mid-run and restart—verify resume point is exact, 0 duplicates in final dataset

**Verifiable Outcomes:**
- ✅ Dashboard shows runs with status filtering
- ✅ Alerts classify transient vs permanent failures
- ✅ One-click retry resumes from interruption checkpoint
- ✅ Final dataset after resume has no duplicates (integration test)

---

### **Vertical Slice 3: Historical Load Progress**
**Phase:** Weeks 4-6  
**Stories:** STORY-2-1, STORY-2-2  
**Tasks:** T-15, T-16  
**Enables FRs:** FR-7, FR-9 (2 FRs)  

**Demo:** 
1. Trigger historical load from 6 months ago
2. Check progress endpoint every 5 seconds
3. Show real-time processed count, total estimate, ETA
4. Wait for completion
5. Verify all 100+ emails from historical period are now in audit and prescription tables

**Verifiable Outcomes:**
- ✅ `GET /run/{id}/progress` reflects accurate metrics during run
- ✅ ETA calculation is within ±20% of actual completion
- ✅ Historical metadata persisted in audit trail

---

### **Vertical Slice 4: Compliance Audit Query and Export**
**Phase:** Weeks 4-6  
**Stories:** STORY-3-1, STORY-3-2, STORY-3-3, STORY-3-4  
**Tasks:** T-18, T-19  
**Enables FRs:** FR-10, FR-14 (2 FRs)  

**Demo:** 
1. Filter runs by date range and status (COMPLETED, PARTIAL)
2. Select one run and drill down to email-level detail
3. View each email's start time, success/fail status, record count
4. Click on one email to see full audit record
5. Export filtered audit set to CSV
6. Verify CSV format matches compliance requirement (all fields, proper delimiters)

**Verifiable Outcomes:**
- ✅ Query filtering works across date, status, sender dimensions
- ✅ Drill-down shows email-level detail with timestamps
- ✅ CSV export includes all audit dimensions with correct formatting
- ✅ Large export (10k+ rows) queued asynchronously without blocking

---

### **Vertical Slice 5: Data Accuracy Verification**
**Phase:** Weeks 7-8  
**Stories:** STORY-5-1, STORY-5-2, STORY-5-3  
**Tasks:** T-20, T-21, T-22  
**Enables FRs:** FR-3, FR-10, FR-13 (3 FRs)  

**Demo:** 
1. Upload a malformed PDF (missing tables, wrong schema)
2. Run intake—verify explicit failure in audit (not silent skip)
3. Query `/records` filtered by date
4. View captured record detail including all 23 fields + source PDF linkage
5. Add verification comment with operator ID and sign-off status
6. Query verification records to confirm audit trail shows operator and timestamp

**Verifiable Outcomes:**
- ✅ Malformed PDF detection 100% (all 50+ test cases fail as expected)
- ✅ Captured records queryable by date/prescriber with source traceability
- ✅ Verification comments stored and queryable per audit filters

---

## Requirements Traceability

### **Functional Requirements Coverage**

| FR | Story | Task | Status |
|----|-------|------|--------|
| FR-1 | STORY-4-1, STORY-1-1, STORY-2-1 | T-1, T-2, T-10 | ✅ In Phase 1 |
| FR-2 | STORY-4-1 | T-3, T-10 | ✅ In Phase 1 |
| FR-3 | STORY-5-1, STORY-5-2, STORY-5-3 | T-7, T-8, T-20, T-21 | ✅ Phases 1 & 2 |
| FR-4 | STORY-4-1, STORY-4-3 | T-1, T-5, T-9, T-10 | ✅ In Phase 1 |
| FR-5 | STORY-4-3 | T-5, T-9, T-10 | ✅ In Phase 1 |
| FR-6 | STORY-4-3 | T-5, T-10 | ✅ In Phase 1 |
| FR-7 | STORY-2-1, STORY-2-2, STORY-2-3 | T-15, T-16, T-17 | ✅ In Phase 2 |
| FR-8 | STORY-1-1, STORY-1-4 | T-10, T-11, T-12, T-13, T-17 | ✅ Phases 1 & 2 |
| FR-9 | STORY-1-1, STORY-1-2, STORY-1-4 | T-13, T-14, T-15, T-16 | ✅ Phases 1 & 2 |
| FR-10 | STORY-3-1, STORY-3-2, STORY-3-4, STORY-5-2, STORY-5-3 | T-4, T-18, T-19, T-21, T-22 | ✅ Phases 1 & 2 |
| FR-11 | STORY-4-1, STORY-4-2 | T-3, T-6, T-17 | ✅ Phases 1 & 2 |
| FR-12 | STORY-2-1 | T-2, T-10 | ✅ In Phase 1 |
| FR-13 | STORY-5-1 | T-7, T-20 | ✅ Phases 1 & 2 |
| FR-14 | STORY-3-4 | T-4, T-18, T-19 | ✅ Phases 1 & 2 |
| FR-15 | STORY-1-1, STORY-1-4, STORY-2-1, STORY-2-2 | T-10, T-11, T-12, T-13, T-23, T-25, T-26 | ✅ Phases 1 & 2 |

### **Non-Functional Requirements Coverage**

| NFR | Tasks | Evidence |
|-----|-------|----------|
| NFR-1: 99% availability | T-11, T-12, T-26 | Persistent scheduler with restart, CI testing all changes |
| NFR-2: Support 10+ year backfills | T-2, T-10, T-15 | Graph API date-bounded retrieval, test 6+ month historical |
| NFR-3: No data loss | T-7, T-8, T-9, T-10, T-21 | Validation before persist, 23-field checks, queryable audit |
| NFR-4: Restart safety | T-3, T-6, T-17, T-28 | Email state tracking, checkpoint per email, resumption tests |
| NFR-5: Interrupt resilience | T-6, T-9, T-28 | Persistent checkpoints, schema constraints, simulated interrupts |
| NFR-6: Zero plaintext credentials | T-1, T-23, T-25 | Vault integration, env-var config (no .env files) |
| NFR-8: Queryable audit trail | T-4, T-18, T-19, T-21, T-22, T-24 | Structured JSON logs, audit tables with multi-dimensional queries, CSV export |
| NFR-9: 100% malformed PDF detection | T-7, T-20, T-27 | 50+ malformed test PDFs, integration tests with `test_format_detection.py` |
| NFR-10: Actionable failure messages | T-4, T-13, T-14, T-24 | Alert dispatcher classifies failures, JSON logs include dimensions |

### **Constraint Coverage**

| CON | Tasks | Evidence |
|-----|-------|----------|
| CON-1: Mailbox-scoped OAuth | T-2 | Graph SDK scoped to single mailbox via service principal |
| CON-2: pdfplumber ≥0.9.0 | T-7, T-20, T-25 | PDF extraction using pdfplumber, malformed detection test |
| CON-3: PostgreSQL composite key | T-9, T-5 | Schema defines unique(prescription_number, dispensing_date) |
| CON-4: Vault + env vars only | T-1, T-23, T-25 | No hardcoded credentials, 90-day rotation built in |
| CON-5: ACID transactions | T-5, T-9, T-17 | SQLAlchemy transactions, upsert atomicity tested |
| CON-6: 90-day credential rotation | T-1 | `rotate_credentials()` method with TTL checks |

---

## Task Dependencies Graph

```
T-23 ──────────────┐
                   ├─────────────┬────────────────────────────────┐
T-25 ──┬───────────┘             │                                │
       │                         │                                │
       ├─────┬──────┬────────────┤                                │
       │     │      │            │                                │
      T-27  │      T-3      T-7  │  T-24                          │
       │    │      │         │   │   │                            │
       │    │      └─────┬───┴───┤   │                            │
       │    │            │       │   │                            │
       │   T-1      T-8  │       │   │                            │
       │    │        │   │       │   │                            │
       └────┼─T-2────┼───┼───────┼───┘                            │
            │        │   │       │                                │
            │        │   │     T-9 ───────────┬────┬──────────┐   │
            │        │   │       │            │    │          │   │
            │        │   │       │          T-28   │          │   │
            │        │   │       │            │    │    T-4   │   │
            │        │   │    T-5            │    │    │      │   │
            │        │   │       │            │    │    ├─────┘   │
            └────────┼───┴───────┼────────────┤    │    │         │
                     │           │            │    │    │         │
            T-6 ◄────┴───────────┘            │    │    │         │
             │                                │    │    │         │
            T-10 ◄──────────────────────────────┘    │    │         │
             │                                       │    │         │
            T-11                                     │    │         │
             │                                       │    │         │
            T-12 ───────────────────┬────────────────┼────┴─────┐   │
             │                      │                │          │   │
       T-15,T-18,T-20,T-21 ────────┤                │          │   │
             │                      │                │          │   │
            T-13 ◄──────────────────┴────────────────┴──────────┘   │
             │                                                       │
       T-14,T-16,T-19,T-22 ───────────────────────────────────────T-26
             │
            T-17
```

---

## Test Strategy

### **Unit Tests (Fast, <1s per test)**
- T-1: SecretsProvider vault auth/rotation
- T-2: MailboxConnector connect/retrieve
- T-3: EmailNewIdentifier dedup logic
- T-7: PDFExtractionEngine field extraction + malformed detection (50+ PDFs)
- T-8: DataValidator field completeness
- T-24: Logging setup JSON structure

**Total Unit Tests:** 10+ test files, ~50 total tests

### **Integration Tests (5-30s per test)**
- T-4: AuditLogger CRUD and queries
- T-5: PrescriptionRepository upsert/dedup
- T-6: JobStateManager state lifecycle
- T-9: Schema migration and constraints
- T-10: IntakeOrchestrator end-to-end happy path
- T-11: APSchedulerJobRunner schedule registration
- T-12: Application startup and signal handling
- T-13: Dashboard routes and retry
- T-14: Alert dispatcher classification
- T-15: Historical load with date bounds
- T-16: Progress API monotonic updates
- T-17: Restart safety with interruption sim
- T-18: Audit query and drill-down
- T-19: CSV export formatting
- T-20: Format detection malformed suite
- T-21: Records routes with filtering
- T-22: Verification audit trail
- T-25: Dependency import checks
- T-26: CI workflow syntax

**Total Integration Tests:** 15+ test files, ~60 tests

### **End-to-End Tests (30-120s per test)**
- T-12: Main startup, scheduler start, SIGTERM shutdown
- T-26: CI pipeline execution

**Total E2E Tests:** 2+ test files, ~6 tests

**Total Test Coverage:** ~116 tests, 0% skip rate, run time <3 min (unit+integration in CI)

---

## Definitions of Done

All 28 tasks use verifiable, executable definitions of done:

```
✅ Unit tests: pytest tests/unit/test_<component>.py -q passes
✅ Integration tests: pytest tests/integration/test_<feature>.py -q passes
✅ E2E tests: pytest tests/e2e/test_<feature>.py -q passes
✅ File paths match components.json structure
✅ New files present in src/, tests/, .github/
✅ CI workflow passes on main branch
✅ No pylint warnings for new code (baseline: 0 errors)
```

---

## Effort & Timeline

| Phase | Weeks | Tasks | SPT Effort | Team |
|-------|-------|-------|------------|------|
| **Phase 1: Foundation** | 1-3 | T-1 through T-12, T-26 | ~70 pts | 1-2 eng |
| **Phase 2a: Monitoring** | 4-6 | T-13, T-14, T-17 | ~15 pts | 1 eng (parallel) |
| **Phase 2b: Hist Load** | 4-6 | T-15, T-16 | ~12 pts | 1 eng (parallel) |
| **Phase 2c: Audit** | 4-6 | T-18, T-19 | ~8 pts | 1 eng (parallel) |
| **Phase 2d: Accuracy** | 7-8 | T-20, T-21, T-22 | ~10 pts | 1 eng (parallel) |
| **UAT & Deploy** | 9+ | — | — | — |

**Total Story Points:** 100 (from Stage 4 estimation)  
**Team Capacity:** 12.5 pts/week (Phase 1: 2 eng at 6.25 pts each; Phase 2: 4 eng in parallel)  
**Timeline:** 8 weeks (Weeks 1-3 Foundation, Weeks 4-8 Expansion)

---

## Next Steps: Stage 6 Implementation

Once Phase 1 (VS-1, Vertical Slice 1) reaches gate approval:

1. **Stage 6: Code Generation** — Generate production source code from tasks.json and components.json with full test coverage
2. **Stage 7: Code Review** — Audit implementation against architecture contracts
3. **Stage 8: UAT** — Execute user acceptance testing per Stage 3 flows
4. **Stage 9: Deployment** — Configure for GitHub Pages (static deployment verification)

---

## Appendix A: File Manifest

| File | Task | Type | LOC Est |
|------|------|------|---------|
| `src/infrastructure/secrets_provider.py` | T-1 | create | 150 |
| `src/integrations/mailbox_connector.py` | T-2 | create | 200 |
| `src/business_logic/email_new_identifier.py` | T-3 | create | 100 |
| `src/persistence/audit_logger.py` | T-4 | create | 250 |
| `src/persistence/prescription_repository.py` | T-5 | create | 200 |
| `src/business_logic/job_state_manager.py` | T-6 | create | 150 |
| `src/business_logic/pdf_extraction_engine.py` | T-7 | create | 250 |
| `src/business_logic/data_validator.py` | T-8 | create | 150 |
| `src/persistence/schema.sql` | T-9 | create | 100 |
| `src/orchestration/intake_orchestrator.py` | T-10 | create | 300 |
| `src/orchestration/apscheduler_job_runner.py` | T-11 | create | 150 |
| `src/orchestration/application_entry.py` | T-12 | create | 100 |
| `src/orchestration/dashboard_routes.py` | T-13 | create | 200 |
| `src/orchestration/alert_dispatcher.py` | T-14 | create | 150 |
| `src/orchestration/intake_orchestrator.py` | T-15 | modify | +100 |
| `src/orchestration/progress_api.py` | T-16 | create | 100 |
| `src/orchestration/intake_orchestrator.py` | T-17 | modify | +150 |
| `src/orchestration/audit_routes.py` | T-18 | create | 150 |
| `src/orchestration/export_service.py` | T-19 | create | 120 |
| `src/business_logic/pdf_extraction_engine.py` | T-20 | modify | +100 |
| `src/orchestration/records_routes.py` | T-21 | create | 120 |
| `src/orchestration/verification_service.py` | T-22 | create | 100 |
| `src/orchestration/config.py` | T-23 | create | 80 |
| `src/orchestration/logging_setup.py` | T-24 | create | 80 |
| `requirements.txt` | T-25 | create | 50 |
| `.github/workflows/ci.yml` | T-26 | create | 60 |
| `tests/conftest.py` | T-27 | create | 200 |
| `tests/integration/helpers.py` | T-28 | create | 200 |
| **Total** | — | — | **~3,800 LOC** |
| **Test Files** | All | create | **~4,000 LOC** |
| **Total (incl tests)** | — | — | **~7,800 LOC** |

---

## Appendix B: Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Graph API rate limiting | T-2: Use Graph SDK with built-in throttling; T-15: Bounded historical queries |
| PDF parsing edge cases | T-7, T-20, T-27: 50+ malformed test suite; explicit failure on schema mismatch |
| Database lock contention | T-5: SQLAlchemy connection pooling; T-9: Composite key index |
| Scheduler persistence failure | T-11: APScheduler SQLAlchemy job store; T-17: Interruption simulation tests |
| Duplicate ingestion during restart | T-6, T-17, T-28: State checkpoint per email; zero-duplicate assertion |
| Credential rotation during run | T-1: TTL checks before use; T-23: Env-driven reload on 90-day cycle |

---

**Version:** 1.0  
**Date Generated:** May 9, 2026  
**Status:** Ready for Stage 6 (Code Generation)
