"""
Typed exception classes for SDLC pipeline verification gates.

Each exception represents a specific kind of failure that can be caught,
logged, and reported to the user with actionable detail.
"""


class SDLCVerificationError(Exception):
    """Base exception for all SDLC pipeline verification failures."""

    def __init__(self, stage: str, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"[Stage {stage}] {reason}")


class StructureError(SDLCVerificationError):
    """JSON schema validation failed."""

    def __init__(self, stage: str, reason: str):
        super().__init__(stage, f"Structure Error: {reason}")


class TraceabilityError(SDLCVerificationError):
    """Reference integrity check failed (e.g., story links to non-existent requirement)."""

    def __init__(self, stage: str, reason: str):
        super().__init__(stage, f"Traceability Error: {reason}")


class CompletionError(SDLCVerificationError):
    """Required items missing (e.g., not all stories have code)."""

    def __init__(self, stage: str, reason: str):
        super().__init__(stage, f"Completion Error: {reason}")


class GateError(SDLCVerificationError):
    """Deployment gate not met (e.g., test failures, build errors)."""

    def __init__(self, stage: str, reason: str):
        super().__init__(stage, f"Gate Error: {reason}")


class MalIntentError(SDLCVerificationError):
    """Intent screening failed — request is adversarial or out of scope."""

    def __init__(self, stage: str, reason: str):
        super().__init__(stage, f"Mal-Intent Error: {reason}")
