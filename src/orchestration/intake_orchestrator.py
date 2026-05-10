import uuid
from datetime import datetime
from typing import Optional

class IntakeOrchestrator:
    def __init__(self, mailbox, identifier, extractor, validator, repo, audit, state_manager):
        self.mailbox = mailbox
        self.identifier = identifier
        self.extractor = extractor
        self.validator = validator
        self.repo = repo
        self.audit = audit
        self.state_manager = state_manager

    async def run_daily_intake(self):
        run_id = self.state_manager.initialize_run_state("daily")
        await self.execute_intake_job(run_id)

    async def execute_intake_job(self, run_id: uuid.UUID):
        """
        Executes the full intake job: retrieve emails, extract data, validate, and store.
        Implements FR-1, FR-2, FR-3, and FR-11.
        """
        try:
            # 1. Fetch emails from mailbox
            emails = await self.mailbox.get_unread_emails_with_attachments()
            
            # 2. Filter for new emails based on identifier
            new_emails = [e for e in emails if self.identifier.is_new_email(e["id"])]
            
            total_extracted = 0
            
            for email_data in new_emails:
                try:
                    # 3. Process each attachment
                    for attachment in email_data["attachments"]:
                        if attachment["filename"].lower().endswith(".pdf"):
                            # 4. Extract fields using PDF engine
                            fields = self.extractor.extract_fields(attachment["content"])
                            
                            # 5. Validate extracted fields
                            is_valid, errors = self.validator.validate_prescription_fields(fields)
                            
                            if is_valid:
                                # 6. Upsert to repository (deduplication handled by repo)
                                fields["original_email_path"] = email_data["id"]
                                self.repo.upsert_prescription(fields)
                                total_extracted += 1
                                outcome = "SUCCESS"
                            else:
                                outcome = f"PARTIAL_INVALID: {', '.join(errors)}"
                        
                        # 7. Audit each email processing result
                        self.audit.log_email_processing(
                            run_id=run_id,
                            email_id=email_data["id"],
                            outcome=outcome,
                            record_count=1 if is_valid else 0
                        )
                    
                    # 8. Mark as processed in checkpoint
                    self.state_manager.checkpoint_email(email_data["id"])
                    
                except Exception as e:
                    self.audit.log_email_processing(
                        run_id=run_id,
                        email_id=email_data["id"],
                        outcome=f"FAILED: {str(e)}",
                        record_count=0
                    )
            
            # 9. Update final run status
            self.state_manager.complete_run(run_id, total_extracted)
            
        except Exception as e:
            self.state_manager.fail_run(run_id, str(e))
