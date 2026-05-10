import logging
import requests
import os

logger = logging.getLogger(__name__)

def dispatch_alert(run_metrics: dict):
    """
    Classifies failures and dispatches alerts via logging and Webhooks.
    """
    status = run_metrics.get("status", "UNKNOWN")
    run_id = run_metrics.get("run_id")
    error_msg = run_metrics.get("error", "No detailed error provided")

    # 1. Critical Logging
    if status == "FAILED":
        logger.critical(f"JOB FAILURE: Run {run_id} failed. Error: {error_msg}")
        
        # 2. Webhook Notification (e.g., Teams/Slack)
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if webhook_url:
            payload = {
                "text": f"🚨 *Prescription Data Capture Failure*\n*Run ID:* {run_id}\n*Error:* {error_msg}"
            }
            try:
                requests.post(webhook_url, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send alert webhook: {e}")
    else:
        logger.info(f"Job completed with status: {status}")

