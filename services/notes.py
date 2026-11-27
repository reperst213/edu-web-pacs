"""검토 메모 (FR-11). 담당: 팀원 2 · 기한 12/8. 수정 전 내용은 notes/{id}/revisions에 보존."""
from services.types import Actor


def add_note(actor: Actor, case_id: str, body: str,
             image_id: str | None = None, run_id: str | None = None) -> str:
    raise NotImplementedError("팀원 2 · 12/8")


def edit_note(actor: Actor, note_id: str, body: str) -> None:
    raise NotImplementedError("팀원 2 · 12/8")


def list_notes(actor: Actor, case_id: str) -> list[dict]:
    raise NotImplementedError("팀원 2 · 12/8")
