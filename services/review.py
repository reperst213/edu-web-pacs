"""검토 상태 전이·작업 목록 (FR-09, FR-10). 담당: 팀원 4 · 기한 12/4~12/5.

케이스 상태를 바꾸는 경로는 이 함수 하나다 (계획서 4장, 18.3).
Firestore 트랜잭션 안에서 권한·현재 상태·version을 확인하고 상태와 events를 함께 쓴다.
"""
from services.types import Actor, Status


def transition(actor: Actor, case_id: str, to: Status, expected_version: int,
               reason: str = "") -> int:
    """반환: 새 version. 허용되지 않으면 InvalidTransition/PermissionDenied/ConcurrentUpdate."""
    raise NotImplementedError("팀원 4 · 12/4")


def worklist(actor: Actor) -> dict:
    """반환: {"todo": [...], "done": [...]}."""
    raise NotImplementedError("팀원 4 · 12/5")
