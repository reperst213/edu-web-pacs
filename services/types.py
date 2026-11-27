"""공통 타입 (계획서 18.1, 18.3). 담당: 팀원 1.

12/1에 고정한다. 바꾸려면 Issue + PR로 제안하고 전원 승인 후 반영한다.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

Role = Literal["registrar", "reviewer", "admin"]
ROLES: tuple[Role, ...] = ("registrar", "reviewer", "admin")
ROLE_LABELS: dict[str, str] = {
    "registrar": "등록 담당자",
    "reviewer": "검토자",
    "admin": "관리자",
}


@dataclass(frozen=True)
class Actor:
    """요청한 사용자. 검증된 ID 토큰의 uid와 DB의 role로만 만든다."""

    uid: str
    role: Role
    email: str = ""


class Status(str, Enum):
    """케이스 상태 (계획서 4장)."""

    RECEIVED = "RECEIVED"          # 접수
    ASSIGNED = "ASSIGNED"          # 배정
    IN_REVIEW = "IN_REVIEW"        # 검토 중
    NEEDS_REWORK = "NEEDS_REWORK"  # 보완 요청
    DONE = "DONE"                  # 완료


STATUS_LABELS: dict[Status, str] = {
    Status.RECEIVED: "접수",
    Status.ASSIGNED: "배정",
    Status.IN_REVIEW: "검토 중",
    Status.NEEDS_REWORK: "보완 요청",
    Status.DONE: "완료",
}


@dataclass(frozen=True)
class Roi:
    """관심 영역. 처리용 사본(긴 변 1,024px) 픽셀 좌표 기준."""

    x: int
    y: int
    w: int
    h: int


@dataclass
class Session:
    """로그인 세션 (팀원 1, services.auth)."""

    uid: str
    email: str
    id_token: str
    refresh_token: str
    expires_at: float  # time.time() 기준 만료 시각(초)


@dataclass
class RunResult:
    """processing.run()의 반환값 (팀원 3)."""

    run_id: str
    result: Any            # RGB uint8 (H, W, 3) NumPy 배열
    roi_stats: dict
    reused: bool           # 같은 설정의 기존 결과를 재사용했으면 True


@dataclass
class SearchResult:
    """search.search_similar()의 반환값 (팀원 4)."""

    search_id: str
    items: list[dict] = field(default_factory=list)
    excluded_count: int = 0
