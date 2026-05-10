# Local Test Guide - Prescription Data Capture

## 1. Microsoft Graph Credentials
1. Register app in Azure Portal (Microsoft Entra ID).
2. Add Application Permission: `Mail.Read`.
3. Create a Client Secret.
4. (Optional) Create an Application Access Policy to restrict to one mailbox.

## 2. Environment Setup
Create a `.env` file:
```env
GRAPH_TENANT_ID=...
GRAPH_CLIENT_ID=...
GRAPH_CLIENT_SECRET=...
GRAPH_MAILBOX_ID=rx-intake@yourdomain.com
DB_CONNECTION=postgresql://postgres:pass@localhost:5432/prescription_db
```

## 3. Database
Run `src/persistence/schema.sql` against your local Postgres.

## 4. Run
```bash
python src/orchestration/application_entry.py
```
Check `run_audit` table for results.
