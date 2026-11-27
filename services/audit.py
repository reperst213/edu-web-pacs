"""감사 로그 (FR-14). 담당: 팀원 1 · 기한 12/1. Firestore audit_logs에 남긴다."""
from services.types import Actor


def log(actor: Actor, action: str, target: str, result: str, reason: str = "") -> None:
    """result: "allow" | "deny" | "error"."""
    raise NotImplementedError("팀원 1 · 12/1")
