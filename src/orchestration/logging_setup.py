import structlog
import sys

def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
logger = logger.bind(service="prescription-intake")
