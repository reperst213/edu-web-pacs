"""감사 로그 (FR-14). 담당: 팀원 1 · 기한 12/1. Firestore audit_logs에 남긴다.

저장소는 앱 시작 시 configure(repo)로 한 번 넣어 준다.
이 모듈은 repositories.base.Repository 인터페이스만 쓴다 (Firestore를 직접 부르지 않는다).
"""
import uuid
from datetime import datetime, timezone

from repositories.base import Repository
from services.types import Actor

COLLECTION = "audit_logs"
RESULTS: tuple[str, ...] = ("allow", "deny", "error")

_repo: Repository | None = None


def configure(repo: Repository | None) -> None:
    """감사 로그를 쓸 저장소를 정한다. None이면 설정을 지운다 (테스트용)."""
    global _repo
    _repo = repo


def log(actor: Actor, action: str, target: str, result: str, reason: str = "") -> None:
    """result: "allow" | "deny" | "error"."""
    if result not in RESULTS:
        raise ValueError(f"result는 {RESULTS} 중 하나여야 합니다: {result!r}")
    if _repo is None:
        raise RuntimeError("audit.configure(repo)를 먼저 호출해야 합니다.")
    _repo.create(COLLECTION, uuid.uuid4().hex, {
        "actor_uid": actor.uid,
        "action": action,
        "target": target,
        "result": result,
        "reason": reason,
        "at": datetime.now(timezone.utc),
    })
