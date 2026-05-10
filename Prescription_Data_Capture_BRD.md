# Business Requirements Document

## Prescription Data Capture

### Automated Intake of Prescription Reports from Email

**Pharmacy Rx Inc.**
**Document Version 1.0**
*Prepared from reverse engineering of the RxPipeline solution*

---

## 1. Executive Summary

Pharmacy Rx Inc. receives a steady stream of prescription activity reports as PDF attachments to emails arriving at a dedicated business mailbox. Today, getting that information out of those PDFs and into a place where it can be reported on, audited, or analyzed depends on manual handling and ad-hoc spreadsheet work. This is slow, error-prone, and does not scale as volume grows.

This document describes the business requirements for an automated intake capability that replaces the manual process. Once in place, prescription information arriving by email will be picked up on a daily schedule, the data inside the PDF reports will be captured, and the records will be stored in a single, governed location where the business can rely on them. The capability supports a one-time historical catch-up of past emails as well as ongoing daily operation, and it will not double-count records if the same email is seen more than once.

The intent of this document is to describe what the business needs and why, in language suitable for sponsors, operations leaders, compliance reviewers, and other non-technical stakeholders. It deliberately avoids prescribing how the solution must be built.

---

## 2. Business Context and Problem Statement

### 2.1 Current Situation

Pharmacy Rx Inc. operates a shared business mailbox that receives prescription reports as PDF attachments. Each report contains tabular prescription data, including patient, drug, prescriber, and fulfillment information. The volume of these emails is sufficient that handling them by hand is no longer practical, and the contents of the reports are needed downstream for reporting, oversight, and operational decision-making.

Today, getting the data out of these PDFs into a usable form requires a person to open each attachment, copy the table content into a spreadsheet, clean it up, and reconcile it with prior data. References to a legacy combined spreadsheet exist within the organization, indicating that this manual aggregation has been the working practice for some time.

### 2.2 Why This Matters

The manual process has three structural problems:

- **It does not scale.** As prescription volume grows, the time required to extract data grows linearly, and so does the cost in staff hours.
- **It is error-prone.** Manual transcription introduces the kinds of mistakes that are hardest to catch later: misread numbers, missed rows, inconsistent formatting between operators, and lost emails.
- **It is not auditable.** The business cannot easily prove which emails were processed, when, by whom, or whether anything was missed. That is a problem for internal control and for any regulatory or partner inquiry that asks how a particular prescription record arrived in the system.

### 2.3 Business Opportunity

Automating this intake addresses all three problems at once. Automation captures every report consistently, applies the same data-handling rules every time, runs on a predictable schedule without staff intervention, and leaves a complete record of what was done. It also frees the staff currently performing manual extraction to focus on higher-value work, and it makes the prescription dataset reliably available to other parts of the business that need it for reporting, finance, compliance, and analytics.

---

## 3. Business Objectives

The capability described in this document exists to deliver the following business outcomes.

### 3.1 Primary Objectives

1. Eliminate manual handling of prescription PDF reports arriving by email, so that staff time is not consumed by routine data entry.
2. Make the data contained in those reports reliably available in a single governed location that the business already trusts for operational data.
3. Ensure that every prescription report received by the business is captured, no record is lost, and no record is double-counted.
4. Establish a verifiable audit trail of what was processed and when, sufficient to answer internal and external inquiries about how a particular record entered the system.

### 3.2 Secondary Objectives

1. Support a one-time historical catch-up so that previously received reports can be brought into the new dataset, giving the business a continuous history rather than a fresh start.
2. Operate on a predictable daily schedule so that downstream consumers know when fresh data is available.
3. Tolerate routine disruptions, such as temporary email or database availability issues, without losing data and without requiring manual cleanup.

---

## 4. Stakeholders

The following groups have an interest in this capability and its outputs.

| Stakeholder | Interest | Engagement Level |
|---|---|---|
| Pharmacy Operations | Relies on the captured data for day-to-day prescription oversight; primary consumer of the resulting dataset. | Primary user |
| Compliance and Audit | Needs assurance that intake is complete, accurate, and traceable. Will review the audit trail. | Reviewer |
| Finance and Reporting | Uses the captured prescription data for revenue, volume, and program reporting (e.g. 340B classification). | Downstream consumer |
| Information Security | Concerned with how mailbox access and database access are granted, scoped, and monitored. | Approver |
| IT Operations | Responsible for the environment in which the capability runs and for responding when scheduled runs do not complete. | Operator |
| Business Sponsor | Owns the business case, funds the work, and accepts the delivered capability. | Decision maker |

---

## 5. Scope

### 5.1 In Scope

- Automated retrieval of emails sent to the designated business mailbox used to receive prescription reports.
- Reading PDF attachments on those emails and capturing the prescription information contained in their tables.
- Storing the captured prescription records in the organization's governed database environment.
- A one-time historical load that goes back to a defined cutoff date agreed by the business.
- Ongoing daily operation that picks up only what is new since the previous run.
- Preventing duplicate records when the same prescription is seen more than once.
- Logging every run and every email processed, with enough detail to support audit and troubleshooting.

### 5.2 Out of Scope

- Reports arriving by any channel other than the designated mailbox (for example, paper, fax, or other inboxes). These remain handled by their existing processes unless added in a future phase.
- Downstream reporting, dashboards, or analytics built on the captured data. These are separate efforts that consume the dataset produced here.
- Changes to how prescription reports are produced or formatted by the upstream sources sending them.
- Replacement of any existing pharmacy management system. This capability adds intake; it does not change systems of record.

---

## 6. Stakeholder Requirements

This section captures what each stakeholder group needs from the capability, expressed as the outcome they expect rather than how it is achieved.

### 6.1 Pharmacy Operations

- Every prescription report received in the mailbox is captured into the dataset within one business day of arrival.
- The captured records contain the same information that appears on the report, faithful to the source.
- Operations can rely on the dataset being refreshed on a known, predictable schedule.

### 6.2 Compliance and Audit

- There is a verifiable record of which emails were processed, when, and with what outcome.
- If a record is questioned, the originating email and PDF attachment can be traced from the record.
- Failed or partial processing is recorded explicitly rather than being silently dropped.

### 6.3 Finance and Reporting

- Each prescription record carries the fields needed for downstream reporting, including identifiers for the prescription, patient, drug, prescriber, dispensing dates, quantity, and program eligibility flags.
- Records are deduplicated so that volume and revenue reports built on the dataset are not inflated.

### 6.4 Information Security

- Access to the mailbox is scoped to the single mailbox used for this purpose and cannot be used to read other mailboxes in the organization.
- Credentials used by the capability are stored and rotated under organizational standards.
- Database access is scoped to the tables that hold this data.

### 6.5 IT Operations

- Scheduled runs produce a clear pass / partial / fail outcome that operations can monitor.
- Failed runs leave the system in a state that can be safely retried without producing duplicate or partial data.
- Routine failures (such as a temporary email service blip) are absorbed without operator intervention; sustained failures are surfaced for action.

---

## 7. Functional Capabilities

The capability shall provide the following business functions.

### 7.1 Email Intake

- Automatically connect to the designated business mailbox and identify emails carrying prescription PDF attachments.
- Identify only emails that have not yet been processed, so that the same email is not handled twice.
- Operate without any human inbox interaction, including without forwarding or moving emails between folders.

### 7.2 Prescription Data Capture

From each PDF attachment the capability shall capture twenty-three pieces of information for every prescription on the report. These are described here in business terms; the precise field names appear in the data dictionary in section 11.

- **Identifiers:** the prescription number, the patient, the prescriber (including their license and national provider identifier where present).
- **Drug information:** drug name, drug type, brand or generic indicator, dispense-as-written indicator, drug class, lot number.
- **Clinical and demographic context:** patient date of birth, patient sex, patient type.
- **Fulfillment information:** quantity dispensed, day supply, total prescription amount, refill authorization, prescription origin, and the dispensing date.
- **Program flags:** 340B program eligibility, prescription status, and order date.

### 7.3 Storage and Deduplication

- Captured records are written to the organization's governed database in a single, well-defined location.
- If the same prescription is seen more than once (for example, on a re-sent report), it is recognized as the same record and not duplicated. The combination of prescription number and dispensing date determines uniqueness.
- If the same prescription is seen again with updated values, the stored record is updated to reflect the latest version rather than producing a second copy.

### 7.4 Operating Modes

| Mode | Business Behavior |
|---|---|
| One-time historical load | Brings into the dataset every prescription report received from a business-defined start date forward. Run once at go-live, and again only if the business chooses to extend history further back. May be safely interrupted and resumed without producing duplicates. |
| Ongoing daily run | Picks up only emails received since the last successful run. Runs on a fixed daily schedule without intervention. Designed to be the steady-state mode of operation after go-live. |

### 7.5 Audit and Logging

- Every run of the capability produces a record that captures when it started, when it finished, how many emails it looked at, how many it processed, how many records were stored, and whether the overall run succeeded, partially succeeded, or failed.
- Every email processed produces a record showing its identifier, subject, received date, the number of records extracted from it, the outcome, and any error detail if it could not be processed.
- These records are retained in the same governed environment as the prescription data and are available to compliance and operations on the same terms.

---

## 8. Non-Functional Requirements

These requirements describe expected qualities of the capability rather than specific functions.

| Quality | Business Expectation |
|---|---|
| Schedule reliability | The daily run completes on its scheduled day. Missed runs are visible to operations the next business day at the latest. |
| Data completeness | Every email reaching the mailbox that contains a prescription PDF attachment is accounted for: either processed successfully, processed with explicit partial result, or recorded as failed with reason. |
| Data accuracy | Captured records faithfully reflect the contents of the source PDF. Where the source is ambiguous or unreadable, the record is not silently fabricated; the email is recorded as partial or failed. |
| No double-counting | Re-running, retrying, or re-receiving an email never produces duplicate records in the dataset. |
| Recoverability | If a run fails partway through, restarting it picks up where it left off. No manual cleanup of the dataset is required. |
| Security of credentials | Mailbox and database credentials are not stored in plain form alongside source code or configuration. Their lifecycle (issue, rotate, retire) follows organizational standards. |
| Least-privilege access | The mailbox connection used by this capability is technically restricted to only the designated business mailbox. It cannot be used to read other mailboxes in the organization. |
| Auditability | For any record in the dataset, the originating email can be identified. For any run, an outcome record exists. |
| Maintainability | When the format of incoming PDFs changes, the capability fails clearly rather than silently producing wrong data, so the change can be addressed before bad data accumulates. |

---

## 9. Assumptions, Constraints, and Dependencies

### 9.1 Assumptions

- The designated business mailbox will continue to be the single intake point for prescription reports of this type.
- PDF reports arriving in the mailbox follow a structurally consistent layout. Minor variations are tolerated; wholesale format changes will require business and technical review.
- The combination of prescription number and dispensing date is sufficient to uniquely identify a prescription record for deduplication purposes.
- Downstream consumers of the dataset accept that records may be updated when newer versions of the same prescription are received.

### 9.2 Constraints

- Access to the mailbox must be granted under the organization's identity and access standards, including administrative approval at setup.
- Access to the destination database is limited to the tables and operations needed for this capability.
- Credentials used by the capability must be renewable on the organization's standard rotation cycle.

### 9.3 Dependencies

- Availability of the designated business mailbox and continued delivery of prescription PDFs to it.
- Availability of the destination database environment in which records are stored.
- Availability of the scheduling environment that runs the daily job.
- Availability of identity and access services that grant the capability its mailbox and database access.

---

## 10. Business Risks

The following risks have been identified at the business level. Mitigations describe what the business expects, not how the technical implementation achieves it.

| Risk | Likelihood | Business Mitigation |
|---|---|---|
| Upstream PDF format changes silently and the dataset begins to drift from the truth. | Medium | The capability fails loudly rather than producing questionable records. Operations is alerted; the dataset is not corrupted in the meantime. |
| Mailbox access is granted too broadly and exposes other mailboxes in the organization. | Medium | Mailbox access is technically scoped to the single designated mailbox. This scoping is verified at setup and reviewed periodically by Information Security. |
| Credentials used by the capability expire and the daily run stops working. | Medium | Credential expiry is tracked under the organization's normal credential lifecycle. Long-lived alternatives are preferred where available. |
| A historical email is reprocessed and produces a duplicate record in the dataset. | Low | Deduplication is built into how records are stored. Reprocessing the same prescription does not create a second copy. |
| A scheduled run is missed and goes undetected. | Low | Each run is logged. Operations can see the absence of a run and the audit trail makes a missing day visible. |
| Existing legacy spreadsheet data does not align with the new dataset. | Low | The historical load is bounded by a business-chosen start date; reconciliation with legacy spreadsheets is performed once at go-live and then retired. |

---

## 11. Data Captured Per Prescription

The following twenty-three pieces of information are captured per prescription. Each is described in business terms. Together they constitute the record of a single prescription as it arrives in the dataset.

| Information | Type | Business Description |
|---|---|---|
| Prescription number | Identifier | The unique number assigned to the prescription by the dispensing system. |
| Patient name | Identifier | The name of the patient receiving the prescription. |
| Drug name | Reference | The name of the drug dispensed. |
| Day supply | Quantity | The number of days the prescription is intended to last. |
| Total prescription amount | Financial | The total monetary amount associated with the prescription. |
| Drug type | Reference | The category or type classification of the drug. |
| Brand indicator | Flag | Indicates whether the prescription was dispensed as a brand product. |
| Dispense-as-written indicator | Flag | Indicates whether dispense-as-written instructions applied. |
| Prescription origin | Reference | How the prescription originated (for example, electronic, written, telephone). |
| Prescriber name | Identifier | The name of the prescribing clinician. |
| Prescription status | Status | The current state of the prescription (for example, filled, on hold). |
| Dispensing date | Date | The date on which the prescription was filled. |
| Refill authorization | Reference | The refill authorization information attached to the prescription. |
| Order date | Date | The date on which the prescription was ordered. |
| Patient date of birth | Demographic | The patient's date of birth. |
| Patient sex | Demographic | The patient's recorded sex. |
| Lot number | Reference | The dispensed lot number, where applicable. |
| Patient type | Reference | The classification of the patient (for example, inpatient, outpatient). |
| Drug class | Reference | The therapeutic or regulatory class of the drug. |
| Prescriber NPI | Identifier | The prescriber's National Provider Identifier. |
| Prescriber license | Identifier | The prescriber's license number. |
| 340B indicator | Flag | Indicates whether the prescription is associated with the 340B drug pricing program. |
| Quantity | Quantity | The quantity of the drug dispensed. |

---

## 12. Operational Expectations

### 12.1 Run Frequency and Timing

- The capability runs once per day at a fixed business-agreed time. The current expectation is end of business day.
- Ad-hoc runs may be initiated by IT Operations to recover from outages or to perform a one-time historical load.

### 12.2 Outcomes Communicated

Each run produces one of three outcomes, which are visible in the audit trail and to monitoring:

- **Success** — every email examined was processed and the resulting records were stored.
- **Partial** — some emails were processed and some were not. The reasons for the unprocessed ones are recorded.
- **Failed** — the run did not complete. The dataset is not left in an inconsistent state; the run can be safely retried.

### 12.3 Monitoring and Alerting

- IT Operations is the first responder to a failed or persistently partial run.
- Compliance can review run outcomes on demand without requiring access to the underlying systems.

### 12.4 Retention

- Captured prescription records are retained per the organization's retention policy for prescription data.
- Audit records of runs and email processing are retained for the period required to support audit inquiries.

---

## 13. Acceptance Criteria

The capability is considered delivered when all of the following are demonstrated:

1. A historical load brings prescription reports received from the agreed cutoff date forward into the dataset, and the records can be reviewed by Pharmacy Operations and reconciled against the legacy spreadsheet.
2. A daily scheduled run completes on schedule for at least ten consecutive business days without manual intervention, and each run is reflected in the audit trail.
3. Re-running an already-processed email produces no duplicate records in the dataset.
4. A re-sent prescription with updated values causes the existing record to be updated, not duplicated.
5. A run that is interrupted partway through can be restarted and completes successfully without producing duplicate or missing records.
6. Mailbox access used by the capability is verified by Information Security to be restricted to the single designated mailbox.
7. Compliance can produce, on demand, a list of every email processed in a given period along with each one's outcome.
8. Pharmacy Operations confirms that the captured records faithfully represent the contents of source PDF reports based on a representative sample review.

---

## 14. Glossary

| Term | Meaning in this Document |
|---|---|
| Designated business mailbox | The single shared mailbox at the organization where prescription PDF reports are received. It is the sole intake point in scope for this capability. |
| Prescription report | A PDF document attached to an email arriving in the designated mailbox, containing tabular prescription data. |
| Record | One row of prescription information stored in the dataset, derived from one row in a PDF report. |
| Dataset | The collection of stored prescription records and the related audit information, held in the organization's governed database environment. |
| Historical load | A one-time operation that brings into the dataset every prescription report received since a business-defined start date. |
| Daily run | The recurring scheduled operation that picks up only emails received since the previous successful run. |
| Deduplication | Recognizing that a prescription seen more than once is the same record, and storing it only once. |
| Audit trail | The combined record of which runs occurred, which emails were processed, with what outcome, and with what result. |
| 340B | A federal drug pricing program; the captured indicator records whether a prescription is associated with this program. |
| NPI | National Provider Identifier; the standard identifier for the prescribing clinician. |

---

## 15. Document Notes

This document was produced by reverse engineering an existing technical solution and reframing what it does in business terms. It deliberately avoids prescribing a specific implementation, technology, or architecture: the solution today happens to use specific tools to retrieve email, read PDFs, and write to a database, but those choices are implementation details and are not part of these requirements. If the organization later chooses to implement the same business capability with different technical components, the requirements in this document still apply unchanged.

Sign-off on this document indicates business agreement on what the capability must accomplish and how its delivery will be judged. Detailed technical specification, design, and operational runbooks are produced separately and reference this document as their source of truth for business intent.
