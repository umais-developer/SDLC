from typing import List, Set, Optional
from datetime import datetime

class EmailNewIdentifier:
    def __init__(self, prescription_repo):
        self.repo = prescription_repo
        self.processed_ids: Set[str] = set()

    def identify_new_emails(self, emails: List[str]) -> List[str]:
        # Filter logic using repo or internal cache
        return [e for e in emails if e not in self.processed_ids]

    def mark_email_processed(self, email_id: str, run_id: str) -> bool:
        self.processed_ids.add(email_id)
        return True

    def is_email_already_processed(self, email_id: str) -> bool:
        return email_id in self.processed_ids
