# Stage 2b: Component Design — Prescription Data Capture System

**Completion Date:** May 9, 2026  
**Status:** ✅ Complete

---

## Executive Summary

The Prescription Data Capture system is composed of **9 core components** organized across **4 architectural layers**:
1. **Persistence Layer** — PostgreSQL-backed repositories and audit logging
2. **Business Logic Layer** — PDF extraction, validation, and deduplication
3. **Integration Layer** — Graph API mailbox access and credential management
4. **Orchestration Layer** — Job scheduling and component coordination

Every component has been designed to satisfy **at least one FR requirement** and many satisfy multiple NFR/CON requirements. No component spans layers; each owns a single clearly-bounded responsibility.

---

## Component Architecture

### Layer 1: Integration Layer

**Purpose:** Shield core business logic from external system APIs and credential management.

#### SecretsProvider
- **Responsibility:** Load mailbox and database credentials from Vault; manage credential rotation.
- **Constraints Satisfied:** CON-4 (IAM standards), CON-6 (rotation cycle)
- **Key Properties:**
  - Zero plaintext credentials in code, config, or environment files (NFR-6)
  - Programmatic credential rotation without service downtime
  - Vault client integration with TTL-based expiration tracking
  - Audit trail of credential access
- **Why Here:** Credentials are external secrets; rotation is infrastructure concern independent of business logic.

#### MailboxConnector
- **Responsibility:** Authenticate to Graph API; retrieve emails from designated mailbox with least-privilege scoping.
- **Constraints Satisfied:** CON-1 (single mailbox), CON-4 (IAM standards)
- **Key Properties:**
  - Service principal OAuth2 authentication (no user interaction)
  - Mailbox-scoped access (no access to non-designated mailboxes)
  - Read-only operations (no folder modifications per FR-12)
  - Connection status tracking and retry logic
- **Why Here:** Graph API is an external service; connection and authentication are integration concerns.

### Layer 2: Business Logic Layer

**Purpose:** Encapsulate core business rules (extraction, validation, deduplication) independent of external systems.

#### PDFExtractionEngine
- **Responsibility:** Extract all 23 prescription fields from PDFs; detect format anomalies; fail explicitly.
- **Functional Requirement:** FR-3 (extract 23 fields), FR-13 (fail on format change)
- **Quality Requirements:** NFR-3 (faithful accuracy, 100%), NFR-9 (100% detection of malformed PDFs)
- **Constraint:** CON-2 (structural consistency with minor variation tolerance)
- **Key Properties:**
  - pdfplumber-based structured table parsing (best-in-class for prescription forms)
  - Schema validation for completeness (all 23 fields required)
  - Format drift detection (fails rather than silently producing incomplete data)
  - Explicit error reporting (field extraction attempt, failure reason)
- **Why Separate:** PDF parsing is a domain-specific skill; centralizing here enables reuse across retry scenarios and format-change testing.

#### DataValidator
- **Responsibility:** Validate extracted prescription fields before storage; enforce data integrity constraints.
- **Functional Requirement:** FR-3 (field validation)
- **Quality Requirement:** NFR-3 (100% accuracy, faithful reflection)
- **Key Properties:**
  - Type validation for all 23 fields
  - Composite key validation (prescription# + dispensing_date must be non-null)
  - Required field presence checking
  - Error classification (temporary vs. permanent failures)
- **Why Separate:** Validation rules are business policy; separating enables easy policy updates without changing extraction logic.

#### EmailNewIdentifier
- **Responsibility:** Identify new unprocessed emails; distinguish from previously processed emails.
- **Functional Requirements:** FR-2 (identify new emails), FR-11 (restart safety at email granularity)
- **Quality Requirements:** NFR-4 (100% deduplication across reruns), NFR-5 (restart <1 min without manual cleanup)
- **Key Properties:**
  - In-memory cache of processed email IDs (populated from audit table on start)
  - Fast lookup: O(1) duplicate check for each email
  - Consults PrescriptionRepository audit table for history
  - Supports resumption point query
- **Why Separate:** Email deduplication is distinct from prescription deduplication; may be reused for other email intake scenarios.

### Layer 3: Persistence Layer

**Purpose:** Exclusive PostgreSQL access; enforce ACID guarantees and audit trails.

#### PrescriptionRepository
- **Responsibility:** Store/update prescription records; deduplicate by composite key; maintain source-email audit link.
- **Functional Requirements:** FR-4 (store in DB), FR-5 (deduplicate), FR-6 (update records)
- **Quality Requirements:** NFR-3 (accuracy), NFR-4 (100% deduplication), NFR-8 (audit trail linking records to emails)
- **Constraints:** CON-3 (composite key), CON-5 (least-privilege DB access)
- **Key Properties:**
  - SQLAlchemy ORM with PostgreSQL
  - Native composite unique constraint: (prescription_number, dispensing_date)
  - UPSERT logic: insert if new, update if existing (ensures no duplicates)
  - Audit reference: every stored record includes source email_id
  - Bulk operations for batch efficiency
- **Why Here:** Database access is privileged; centralizing in Repository ensures least-privilege enforcement and data consistency.

#### AuditLogger
- **Responsibility:** Record run outcomes and email processing details in audit tables; queryable for compliance.
- **Functional Requirements:** FR-9 (run records), FR-10 (email records), FR-14 (retention)
- **Quality Requirements:** NFR-8 (audit trail, queryable within 5 minutes), NFR-10 (explicit failure classification)
- **Key Properties:**
  - Run audit table: start time, end time, email count, record count, status, metrics, run_id
  - Email audit table: email_id, subject, received_date, record_count, outcome, error_details, run_id
  - Structured JSON logging via structlog
  - Query interface: filter by date, sender, status, email_id, record_count (5+ dimensions)
  - Retention configuration per organizational policy
- **Why Here:** Audit logging is a persistence concern; maintains audit tables and provides query interface.

#### JobStateManager
- **Responsibility:** Track processing state at email granularity; enable safe restart from interruption.
- **Functional Requirements:** FR-7 (historical load with resumption), FR-8 (daily run resumption), FR-11 (email-level state)
- **Quality Requirements:** NFR-5 (restart <1 min, zero duplicates across 20+ restart tests)
- **Key Properties:**
  - State persisted to audit table after each email (processed_email_tracking table)
  - On restart: queries audit table for first unprocessed email
  - Run mode tracking (historical vs. daily)
  - Start date tracking for historical load
- **Why Here:** State management is a persistence concern; persisting to audit table enables recovery after service interruption.

### Layer 4: Orchestration Layer

**Purpose:** Coordinate component interactions, manage job lifecycle, and implement application workflows.

#### IntakeOrchestrator
- **Responsibility:** Main job runner; coordinate all components; execute historical load or daily run mode.
- **Functional Requirements:** All FR-1 through FR-15 (orchestrator invokes all components)
- **Quality Requirements:** NFR-1 (daily runs complete on schedule), NFR-2 (every email accounted for)
- **Key Properties:**
  - Two run modes: historical_load and daily_intake
  - Dependency injection of all business logic and persistence components
  - Data flow orchestration:
    1. MailboxConnector retrieves emails
    2. EmailNewIdentifier filters to new emails
    3. PDFExtractionEngine extracts fields
    4. DataValidator validates
    5. PrescriptionRepository stores/updates/deduplicates
    6. AuditLogger records outcomes
    7. JobStateManager marks email as processed
  - Error handling: classify failures, record in audit trail, continue processing other emails
  - On interruption: JobStateManager.get_resumption_point() returns first unprocessed email; next run resumes there
- **Why Here:** Orchestration is business workflow; belongs in dedicated orchestrator not scattered across components.

#### APSchedulerJobRunner
- **Responsibility:** Schedule daily job; execute on schedule; manage persistent job store and retries.
- **Functional Requirements:** FR-8 (daily schedule), FR-15 (unattended operation)
- **Quality Requirements:** NFR-1 (99% on-schedule completion)
- **Key Properties:**
  - APScheduler with persistent job store (survives service restart)
  - Daily trigger at business-agreed time (e.g., 18:00 UTC)
  - Retry logic for transient failures (no operator action needed)
  - ThreadPoolExecutor for background execution
  - Scheduled job registry
- **Why Here:** Job scheduling is infrastructure; separate from business logic to enable testing without scheduler dependency.

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ APSchedulerJobRunner: Daily Trigger at 18:00 UTC                             │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ IntakeOrchestrator.run_daily_intake()                                        │
│ - Initialize JobStateManager with run_mode='daily'                           │
│ - Query JobStateManager.get_resumption_point() (null on first run)          │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
    ┌──────────────────┐           ┌──────────────────┐
    │ SecretsProvider  │           │ MailboxConnector │
    │ get_mailbox_     │────────>  │ connect()        │
    │ credentials()    │           │ retrieve_emails()│
    └──────────────────┘           │ (since last run) │
                                   └────────┬─────────┘
                                            │
                                   [List: 5 new emails]
                                            │
                                            ▼
                              ┌──────────────────────────────┐
                              │ EmailNewIdentifier           │
                              │ identify_new_emails()        │
                              │ (filter to unprocessed)      │
                              │ [Filter: 5 emails → 4 new]   │
                              └──────────┬───────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
         FOR EACH NEW EMAIL:              ▼                    │
                    │        ┌────────────────────────┐        │
                    │        │ PDFExtractionEngine    │        │
                    │        │ extract_fields()       │        │
                    │        │ validate_pdf_format()  │        │
                    │        │ [Extract: 23 fields]   │        │
                    │        └────────────┬───────────┘        │
                    │                     │                    │
                    │                     ▼                    │
                    │        ┌────────────────────────┐        │
                    │        │ DataValidator          │        │
                    │        │ validate_fields()      │        │
                    │        │ [Validate: OK]         │        │
                    │        └────────────┬───────────┘        │
                    │                     │                    │
                    │                     ▼                    │
                    │        ┌────────────────────────────┐    │
                    │        │ PrescriptionRepository     │    │
                    │        │ store_or_update()          │    │
                    │        │ - Find existing by (Rx#,   │    │
                    │        │   dispensing_date)         │    │
                    │        │ - If found: UPDATE         │    │
                    │        │ - If not: INSERT           │    │
                    │        │ - Record email_id ref      │    │
                    │        │ [Store: 1 record]          │    │
                    │        └────────────┬───────────────┘    │
                    │                     │                    │
                    │                     ▼                    │
                    │        ┌────────────────────────────┐    │
                    │        │ AuditLogger                │    │
                    │        │ record_email_processed()   │    │
                    │        │ [Log: success]             │    │
                    │        └────────────┬───────────────┘    │
                    │                     │                    │
                    │                     ▼                    │
                    │        ┌────────────────────────────┐    │
                    │        │ JobStateManager            │    │
                    │        │ mark_email_as_processed()  │    │
                    │        │ [Persist: email_id to DB]  │    │
                    │        └────────────┬───────────────┘    │
                    │                     │                    │
                    └─────────────────────┼────────────────────┘
                                          │
                                    (repeat for emails 2-4)
                                          │
                                          ▼
                              ┌──────────────────────────┐
                              │ AuditLogger              │
                              │ finalize_run_record()    │
                              │ [Record: status=Success, │
                              │  emails=4, records=3,    │
                              │  start_time, end_time]   │
                              └──────────────────────────┘

ON INTERRUPTION (e.g., after email 2 of 4):
  1. Service stops mid-processing
  2. Next scheduled run (or manual trigger):
     - JobStateManager.get_resumption_point() → email_id_3
     - MailboxConnector skips first 2 emails (already tracked)
     - EmailNewIdentifier skips first 2 emails (in cache)
     - Processing resumes at email 3
  3. No duplicates; no manual cleanup required
```

---

## Component Dependency Graph

```
                    ┌─────────────────────────────┐
                    │ APSchedulerJobRunner        │
                    │ (Orchestration Layer)       │
                    └────────────────┬────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────┐
                    │ IntakeOrchestrator          │
                    │ (Orchestration Layer)       │
                    └────────────────┬────────────┘
                                     │
          ┌──────────────┬───────────┼───────────┬───────────┐
          │              │           │           │           │
          ▼              ▼           ▼           ▼           ▼
    ┌────────────┐  ┌─────────────────────────────────────────┐
    │SecretsProvider  │   MailboxConnector   PDFExtractionEngine
    │(Integration)    │   (Integration)      (Business Logic)
    └────────────┘    └──────┬────────────────────────┬─────────┐
                              │                        │         │
    ┌──────────────────┐      │                        │         │
    │EmailNewIdentifier│<─────┘                        │         │
    │(Business Logic)  │                               ▼         │
    └────────┬─────────┘                    ┌──────────────────┐ │
             │                              │DataValidator     │ │
             │                              │(Business Logic)  │ │
             │                              └────────┬─────────┘ │
             │                                       │           │
             │      ┌────────────────────────────────┘           │
             │      │                                            │
             │      ▼                                            ▼
             │  ┌─────────────────────────────────────────────────────┐
             └─>│      PrescriptionRepository                         │
                │      (Persistence Layer)                           │
                │      - Deduplication by (Rx#, dispensing_date)     │
                │      - UPSERT logic                                 │
                │      - Audit reference to source email             │
                └─────────┬───────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐
    │AuditLogger │ │JobStateManager  (Persistence)
    │(Persistence)   (Persistence)   [processed_
    │[runs table]     [state in       email_
    │[email_         audit table]     tracking]
    │processing_table]
    └────────────┘ └────────────┘ └────────────────┘

DEPENDENCY LEVELS:
- Level 0: SecretsProvider (no dependencies)
- Level 1: MailboxConnector (depends on SecretsProvider)
- Level 1: PDFExtractionEngine, DataValidator (no dependencies)
- Level 2: EmailNewIdentifier (depends on PrescriptionRepository)
- Level 2: PrescriptionRepository, AuditLogger, JobStateManager (no dependencies from business logic)
- Level 3: IntakeOrchestrator (depends on all Level 1-2 components)
- Level 4: APSchedulerJobRunner (depends on IntakeOrchestrator)

CIRCULAR DEPENDENCIES: None
```

---

## Design Principles Applied

### 1. Single Responsibility Principle
Each component owns one clearly-bounded responsibility:
- **SecretsProvider:** Credential management only
- **MailboxConnector:** Graph API integration only
- **PDFExtractionEngine:** PDF parsing only
- **DataValidator:** Validation rules only
- **PrescriptionRepository:** Prescription storage and deduplication
- **AuditLogger:** Audit trail recording
- **JobStateManager:** State tracking for interruption safety
- **IntakeOrchestrator:** Component coordination
- **APSchedulerJobRunner:** Job scheduling

### 2. Layered Architecture
- **Integration Layer:** Isolates external APIs and credentials
- **Business Logic Layer:** Encapsulates domain rules independent of persistence
- **Persistence Layer:** Exclusive PostgreSQL access with audit trails
- **Orchestration Layer:** Coordinates workflows and job lifecycle

### 3. Explicit Error Handling
Every component classifies failures:
- **Transient:** Retryable (network timeout, temporary database unavailability)
- **Permanent:** Non-retryable (invalid PDF format, data integrity violation)
- **Partial:** Some data extracted successfully, some fields missing (NFR-10)

### 4. Audit Trail Completeness
Every processing step recorded:
- **Run level:** Start/end time, email count, record count, status
- **Email level:** Email ID, subject, received date, extraction outcome, errors
- **Prescription level:** Source email ID reference (enables traceability per NFR-8)

### 5. Restart Safety by Design
All state persisted to database:
- **Email-level tracking:** processed_email_tracking table records every email processed
- **Run context:** JobStateManager queries audit table on restart to find resumption point
- **Zero manual intervention:** Restart within seconds without human cleanup

---

## Key Design Decisions Justified Against Requirements

| Component | FR Links | NFR Links | CON Links | Design Rationale |
|-----------|----------|-----------|-----------|------------------|
| **SecretsProvider** | — | NFR-6 | CON-4, CON-6 | Centralizes credential lifecycle; prevents plaintext storage; enables rotation without service interruption |
| **MailboxConnector** | FR-1, FR-12 | NFR-2, NFR-7 | CON-1, CON-4 | Graph SDK ensures least-privilege mailbox scoping; OAuth2 service principal eliminates user interaction |
| **EmailNewIdentifier** | FR-2, FR-11 | NFR-4, NFR-5 | — | O(1) duplicate detection; supports restart from interruption point |
| **PDFExtractionEngine** | FR-3, FR-13 | NFR-3, NFR-9 | CON-2 | pdfplumber best-in-class for tabular data; explicit format failure detection prevents silent data loss |
| **DataValidator** | FR-3 | NFR-3 | — | Enforces data integrity before database write; blocks incomplete records |
| **PrescriptionRepository** | FR-4, FR-5, FR-6 | NFR-3, NFR-4, NFR-8 | CON-3, CON-5 | Native PostgreSQL composite unique constraint ensures 100% deduplication; UPSERT logic handles updates |
| **AuditLogger** | FR-9, FR-10, FR-14 | NFR-8, NFR-10 | — | Structured JSON logging enables Compliance queries by 5+ dimensions; explicit failure classification |
| **JobStateManager** | FR-7, FR-8, FR-11 | NFR-5 | — | Email-level state persistence enables restart <1 min; prevents duplicates across interruptions |
| **IntakeOrchestrator** | FR-1–FR-15 | NFR-1, NFR-2 | — | Coordinates all components; implements both run modes; ensures every email accounted for |
| **APSchedulerJobRunner** | FR-8, FR-15 | NFR-1 | — | Persistent job store survives service restart; retry logic handles transient failures without operator action |

---

## PostgreSQL Schema Outline

```sql
-- Prescriptions: store extracted records with composite unique key
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    prescription_number VARCHAR(50) NOT NULL,
    dispensing_date DATE NOT NULL,
    patient_name VARCHAR(100),
    drug_name VARCHAR(100),
    -- ... (21 more fields per 23-field specification)
    source_email_id VARCHAR(255) NOT NULL,  -- Reference to source email
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (prescription_number, dispensing_date)
);

-- Run Audit Records: track job execution outcomes
CREATE TABLE run_audit (
    run_id VARCHAR(36) PRIMARY KEY,
    run_mode VARCHAR(20),  -- 'historical' or 'daily'
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    emails_examined INT,
    emails_processed INT,
    records_stored INT,
    status VARCHAR(20),  -- 'Success', 'Partial', 'Failed'
    error_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Processing Records: audit trail of email extraction outcomes
CREATE TABLE email_processing_audit (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) REFERENCES run_audit(run_id),
    email_id VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    received_date TIMESTAMP,
    record_count INT,
    outcome VARCHAR(20),  -- 'success', 'partial', 'failed'
    error_details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Processed Email Tracking: for restart safety
CREATE TABLE processed_email_tracking (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) REFERENCES run_audit(run_id),
    email_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (run_id, email_id)
);

-- Indexes for common queries
CREATE INDEX idx_prescriptions_composite ON prescriptions(prescription_number, dispensing_date);
CREATE INDEX idx_prescriptions_source_email ON prescriptions(source_email_id);
CREATE INDEX idx_email_processing_run_id ON email_processing_audit(run_id);
CREATE INDEX idx_email_processing_date ON email_processing_audit(created_at);
CREATE INDEX idx_processed_email_tracking ON processed_email_tracking(run_id);
```

---

## Test Strategy Summary

### Unit Tests
- **PDFExtractionEngine:** 50+ test PDFs (well-formed + malformed), verify 23 fields extracted correctly, verify format anomalies detected
- **DataValidator:** Verify required field presence, type validation, composite key validation
- **EmailNewIdentifier:** Mock repository, verify processed email cache populated correctly, O(1) duplicate detection
- **PrescriptionRepository:** Mock SQLAlchemy, verify UPSERT logic, verify deduplication by composite key

### Integration Tests
- **E2E Historical Load:** Load 100+ historical emails from 3-month cutoff, verify all processed, zero duplicates
- **E2E Daily Run:** Schedule daily run, verify completes within service window, produces audit record
- **E2E Interruption:** Interrupt run at email #50 of 100, restart, verify resumes at #51 without duplicates (20+ restart scenarios)
- **E2E Format Failure:** Test with 50 malformed PDFs, verify 100% detection and failure recording
- **E2E Deduplication:** Load 100 duplicate prescriptions (same Rx# and dispensing_date), verify 1 stored record

### Compliance/Browser Tests
- **Audit Query Performance:** Retrieve records for 30-day date range in <5 minutes (NFR-8)
- **Traceability:** Trace stored record back to source email within 2 seconds (NFR-8)
- **Failure Classification:** Verify failures classified correctly (transient/permanent) in audit trail (NFR-10)

---

## Risk Mitigation

| Risk | Component | Mitigation |
|------|-----------|-----------|
| PDF format variation | PDFExtractionEngine, DataValidator | Detect format anomalies, fail explicitly, alert Operations (FR-13, NFR-9) |
| Network interruption | APSchedulerJobRunner, JobStateManager | Retry transient failures; persistent job store; restart from state (FR-11, NFR-5) |
| Duplicate emails | EmailNewIdentifier, PrescriptionRepository | In-memory cache + database dedup by composite key (FR-5, NFR-4) |
| Credential exposure | SecretsProvider | Never store plaintext; rotate via Vault every 90 days (NFR-6, CON-6) |
| Partial run completion | AuditLogger, IntakeOrchestrator | Record partial outcomes explicitly; enable resume at email granularity (FR-9, NFR-10) |
| Audit log growth | AuditLogger | Retention policy per organizational standards; cold storage archive (FR-14) |

---

## Next Steps

1. **Stage 3 (UX Design):** Map user flows for Operations monitoring, Compliance audit queries, and failure alerting.
2. **Stage 4 (Epics & Stories):** Break components into user stories with acceptance criteria per component interface.
3. **Stage 5 (Implementation Plan):** Sequence component builds with dependency order (Layer 1 → Layer 2 → Layer 3 → Layer 4); identify parallel work opportunities.
4. **Stage 6 (Implementation):** Develop each component with unit + integration tests per test strategy; verify build passes and all tests pass before completion.
5. **Stage 7 (Code Review):** Audit against architecture contracts; verify every component implements its public interface as specified.
6. **Stage 8 (UAT):** Execute test plan covering historical load, daily run, interruption recovery, format failures, and compliance queries.
7. **Stage 9 (Deployment):** Configure GitHub Pages deployment and finalize DevOps pipeline.

---

## Appendix: Component Interface Summary

| Component | Public Methods |
|-----------|-----------------|
| **SecretsProvider** | `get_mailbox_credentials()`, `get_database_credentials()`, `rotate_credentials(type)`, `is_credentials_expiring_soon()` |
| **MailboxConnector** | `connect()`, `disconnect()`, `retrieve_emails(start, end)`, `is_connected()` |
| **EmailNewIdentifier** | `identify_new_emails(emails)`, `mark_email_processed(id, run_id)`, `get_last_processed_email_id()`, `is_email_already_processed(id)` |
| **PDFExtractionEngine** | `extract_fields(pdf_bytes)`, `validate_pdf_format(pdf_bytes)`, `get_supported_field_names()`, `detect_format_change(fields)` |
| **DataValidator** | `validate_prescription_fields(fields)`, `is_field_present(name, value)`, `validate_composite_key(rx#, date)`, `get_validation_errors()` |
| **PrescriptionRepository** | `store_or_update(prescription)`, `find_by_composite_key(rx#, date)`, `get_all_prescriptions()`, `get_records_from_email(email_id)`, `bulk_upsert(prescriptions)` |
| **AuditLogger** | `create_run_record(context)`, `record_email_processed(...)`, `finalize_run_record(run_id, status, metrics)`, `query_email_processing_records(filter)` |
| **JobStateManager** | `initialize_run_state(mode, start_date)`, `get_resumption_point()`, `mark_email_as_processed(id)`, `finalize_run_state(status)`, `is_resumable_state_available()` |
| **IntakeOrchestrator** | `run_historical_load(start_date)`, `run_daily_intake()`, `execute_intake_job(mode, start_date)`, `get_last_run_result()`, `get_job_status()` |
| **APSchedulerJobRunner** | `start_scheduler()`, `stop_scheduler()`, `schedule_daily_run(hour, minute)`, `reschedule_historical_load(date)`, `trigger_manual_run()` |

---

**Document Version:** 1.0  
**Last Updated:** May 9, 2026  
**Status:** Ready for Stage 3 (UX Design)
