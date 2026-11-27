"""케이스 관리 (FR-01, FR-03). 담당: 팀원 2 · 기한 12/4."""
from services.types import Actor


def create_case(actor: Actor, exam_type: str, body_site: str) -> str:
    """반환: case_id (MC-0001 형식, counters/cases 트랜잭션으로 발급)."""
    raise NotImplementedError("팀원 2 · 12/4")


def get_case(actor: Actor, case_id: str) -> dict:
    raise NotImplementedError("팀원 2 · 12/4")


def search_cases(actor: Actor, filters: dict, page_size: int = 20,
                 cursor: str | None = None) -> tuple[list[dict], str | None]:
    """반환: (케이스 목록, 다음 페이지 cursor 또는 None)."""
    raise NotImplementedError("팀원 2 · 12/4")
