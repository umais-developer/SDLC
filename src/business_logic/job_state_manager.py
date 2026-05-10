from typing import Optional
import uuid
from datetime import datetime
from sqlalchemy import text

class JobStateManager:
    def __init__(self, audit_logger):
        self.audit_logger = audit_logger
        self.session = audit_logger.session

    def initialize_run_state(self, run_mode: str, start_date: Optional[str] = None) -> uuid.UUID:
        """
        Initializes a new run or resumes an interrupted one.
        """
        run_id = uuid.uuid4()
        self.audit_logger.create_run_record(run_id, datetime.now())
        return run_id

    def get_resumption_point(self) -> Optional[str]:
        """
        Queries the database for the last successful email processed 
        to determine where to resume if a job was interrupted.
        """
        query = text("""
            SELECT received_date FROM email_audit 
            WHERE status = 'PROCESSED' 
            ORDER BY received_date DESC LIMIT 1
        """)
        result = self.session.execute(query).scalar()
        return result.isoformat() if result else None

    def mark_email_as_processed(self, email_id: str, run_id: uuid.UUID, **kwargs) -> bool:
        """
        Checkpoints an individual email as processed.
        """
        self.audit_logger.record_email_processed(
            email_id=email_id,
            status='PROCESSED',
            run_id=run_id,
            **kwargs
        )
        return True

    def finalize_run_state(self, run_id: uuid.UUID, status: str) -> bool:
        """
        Finalizes the run record.
        """
        self.audit_logger.finalize_run_record(run_id, datetime.now(), status)
        return True

