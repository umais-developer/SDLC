class IntegrationHelpers:
    @staticmethod
    def simulate_interruption():
        raise ConnectionError("Simulated interruption")

    @staticmethod
    def build_test_email(email_id: str, subject: str):
        return {"id": email_id, "subject": subject, "receivedDateTime": "2026-05-09T10:00:00Z"}
