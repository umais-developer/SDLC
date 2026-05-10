from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class APSchedulerJobRunner:
    def __init__(self, orchestrator, db_url: str):
        self.orchestrator = orchestrator
        self.scheduler = BackgroundScheduler()

    def start_scheduler(self) -> bool:
        self.scheduler.start()
        return True

    def schedule_daily_run(self, hour: int, minute: int):
        self.scheduler.add_job(
            self.orchestrator.run_daily_intake,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_intake'
        )
