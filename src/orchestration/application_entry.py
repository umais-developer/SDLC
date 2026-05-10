import signal
import sys
import logging
import threading
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orchestration.config import config
from orchestration.logging_setup import setup_logging
from orchestration.apscheduler_job_runner import APSchedulerJobRunner
from orchestration.intake_orchestrator import IntakeOrchestrator
from infrastructure.secrets_provider import SecretsProvider
from integrations.mailbox_connector import MailboxConnector
from business_logic.email_new_identifier import EmailNewIdentifier
from business_logic.pdf_extraction_engine import PDFExtractionEngine
from business_logic.data_validator import DataValidator
from business_logic.job_state_manager import JobStateManager
from persistence.prescription_repository import PrescriptionRepository
from persistence.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.runner = None
        self.engine = None
        self._setup_orchestrator()

    def _setup_orchestrator(self):
        # Database setup
        self.engine = create_engine(config.DB_CONNECTION)
        SessionLocal = sessionmaker(bind=self.engine)
        db_session = SessionLocal()

        # Component Initialization
        secrets = SecretsProvider(config.VAULT_ADDR, config.VAULT_TOKEN)
        mailbox = MailboxConnector(secrets)
        
        repo = PrescriptionRepository(db_session)
        audit = AuditLogger(db_session)
        
        identifier = EmailNewIdentifier(repo)
        extractor = PDFExtractionEngine()
        validator = DataValidator()
        state_manager = JobStateManager(audit)

        orchestrator = IntakeOrchestrator(
            mailbox=mailbox,
            identifier=identifier,
            extractor=extractor,
            validator=validator,
            repo=repo,
            audit=audit,
            state_manager=state_manager
        )

        self.runner = APSchedulerJobRunner(orchestrator, config.DB_CONNECTION)

        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/')
        def health_check():
            return jsonify({"status": "running"}), 200

    def start(self):
        logger.info("Starting Prescription Data Capture Service...")
        
        # Schedule daily run based on config
        hour, minute = map(int, config.DAILY_RUN_TIME.split(":"))
        self.runner.schedule_daily_run(hour=hour, minute=minute)
        
        self.runner.start_scheduler()
        logger.info(f"Daily intake scheduled for {config.DAILY_RUN_TIME}")
        
        # Start Flask app in a background thread to satisfy the UAT health check
        threading.Thread(target=lambda: self.flask_app.run(host='0.0.0.0', port=5000, use_reloader=False), daemon=True).start()
        logger.info("Started HTTP health check server on http://localhost:5000")

    def stop(self, *args):
        logger.info("Shutting down gracefully...")
        if self.runner:
            self.runner.scheduler.shutdown()
        if self.engine:
            self.engine.dispose()
        sys.exit(0)

def main():
    setup_logging()
    
    app = Application()
    
    # Handle termination signals
    signal.signal(signal.SIGINT, app.stop)
    signal.signal(signal.SIGTERM, app.stop)

    app.start()
    
    # Keep the main thread alive
    import time
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        app.stop()

if __name__ == "__main__":
    main()
