"""저장소 인터페이스 (계획서 18.3). 담당: 팀원 2 · 기한 12/1.

서비스는 Firestore를 직접 부르지 않고 이 인터페이스만 쓴다.
- firestore_repo.py: 실제 Firestore 구현 (APP_MODE=firebase)
- memory_repo.py: 메모리 가짜 구현 (APP_MODE=local, 테스트)
"""
from abc import ABC, abstractmethod
from typing import Any, Callable


class Repository(ABC):
    @abstractmethod
    def get(self, col: str, id: str) -> dict | None:
        """문서가 없으면 None."""

    @abstractmethod
    def create(self, col: str, id: str, data: dict) -> None:
        """이미 있으면 실패한다 (예외 종류는 팀원 2가 12/1에 정해 계획서 18장에 추가)."""

    @abstractmethod
    def update(self, col: str, id: str, data: dict) -> None:
        """주어진 필드만 바꾼다."""

    @abstractmethod
    def query(self, col: str, where: list[tuple[str, str, Any]] | None = None,
              order_by: list[tuple[str, str]] | None = None, limit: int | None = None,
              start_after: str | None = None) -> list[dict]:
        """where 예: [("status", "==", "ASSIGNED")], order_by 예: [("registered_at", "desc")]."""

    @abstractmethod
    def run_transaction(self, fn: Callable[["Repository"], Any]) -> Any:
        """fn 안의 읽기·쓰기를 한 트랜잭션으로 실행한다."""
