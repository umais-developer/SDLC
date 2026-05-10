from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from persistence.audit_logger import AuditLogger

class VerificationService:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.audit_logger = AuditLogger(db_session)

    def record_verification(self, run_id: str, operator_id: str, comment: str, is_manual_match: bool = True):
        """
        Records a manual verification by an operator for a specific run.
        """
        query = text("""
            INSERT INTO verification_audit (run_id, operator_id, comment, verified_at, is_manual_match)
            VALUES (:run_id, :operator_id, :comment, NOW(), :is_manual_match)
        """)
        self.session.execute(query, {
            "run_id": run_id,
            "operator_id": operator_id,
            "comment": comment,
            "is_manual_match": is_manual_match
        })
        self.session.commit()

    def verify_run_counts(self, run_id: str, expected_count: int) -> bool:
        """
        Verify if the number of records stored in a run matches the expected count.
        """
        query = text("""
            SELECT records_stored FROM run_audit WHERE run_id = :run_id
        """)
        actual_count = self.session.execute(query, {"run_id": run_id}).scalar()
        
        if actual_count is None:
            return False
            
        return actual_count == expected_count
