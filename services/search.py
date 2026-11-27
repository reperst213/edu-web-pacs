"""유사 병변 검색 (특화 기능, FR-15·16). 담당: 팀원 4 · 기한 12/10. 명세는 계획서 8장."""
from services.types import Actor, Roi, SearchResult


def search_similar(actor: Actor, image_id: str, roi: Roi | None = None,
                   weights: tuple[float, float, float] = (1.0, 1.0, 1.0),
                   k: int = 5) -> SearchResult:
    """같은 patient_id·lesion_id·공식 중복 쌍·분할 실패 후보는 제외한다."""
    raise NotImplementedError("팀원 4 · 12/10")


def select_references(actor: Actor, search_id: str, image_ids: list[str]) -> None:
    raise NotImplementedError("팀원 4 · 12/10")
