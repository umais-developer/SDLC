from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

class AuditLogger:
    def __init__(self, db_session: Session):
        self.session = db_session

    def create_run_record(self, run_id: uuid.UUID, start_time: datetime) -> None:
        query = text("""
            INSERT INTO run_audit (run_id, start_time, status)
            VALUES (:run_id, :start_time, 'STARTED')
        """)
        self.session.execute(query, {"run_id": run_id, "start_time": start_time})
        self.session.commit()

    def record_email_processed(self, email_id: str, status: str, run_id: uuid.UUID, 
                               subject: Optional[str] = None, 
                               received_date: Optional[datetime] = None,
                               error_message: Optional[str] = None,
                               original_email_path: Optional[str] = None) -> None:
        query = text("""
            INSERT INTO email_audit (email_id, subject, received_date, status, error_message, run_id, original_email_path)
            VALUES (:email_id, :subject, :received_date, :status, :error_message, :run_id, :original_email_path)
            ON CONFLICT (email_id) DO UPDATE SET
                status = EXCLUDED.status,
                error_message = EXCLUDED.error_message
        """)
        self.session.execute(query, {
            "email_id": email_id,
            "subject": subject,
            "received_date": received_date,
            "status": status,
            "error_message": error_message,
            "run_id": run_id,
            "original_email_path": original_email_path
        })
        
        # Update run_audit counts
        if status == 'PROCESSED':
            self.session.execute(
                text("UPDATE run_audit SET emails_processed = emails_processed + 1 WHERE run_id = :run_id"),
                {"run_id": run_id}
            )
        self.session.commit()

    def finalize_run_record(self, run_id: uuid.UUID, end_time: datetime, status: str) -> None:
        # Also count recorded prescriptions for this run via original_email_path join if needed, 
        # but for simplicity we'll just update final status and end time.
        query = text("""
            UPDATE run_audit 
            SET end_time = :end_time, status = :status
            WHERE run_id = :run_id
        """)
        self.session.execute(query, {"run_id": run_id, "end_time": end_time, "status": status})
        self.session.commit()
    
    def query_run_records(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Basic implementation for dashboard/audit
        query = "SELECT * FROM run_audit"
        if filters:
            conditions = [f"{k} = :{k}" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
        
        result = self.session.execute(text(query), filters).mappings().all()
        return [dict(row) for row in result]

