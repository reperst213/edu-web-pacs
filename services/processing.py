"""영상처리 실행·이력 (FR-05~07). 담당: 팀원 3 · 기한 12/9.

run_id = SHA-1(json.dumps({image_id, algorithm, version, params, roi}, sort_keys=True)).
같은 run_id가 committed면 재사용(reused=True), 없으면 pending 문서를 create()로 먼저 만든다.
"""
from services.types import Actor, Roi, RunResult


def run(actor: Actor, image_id: str, algorithm: str, params: dict,
        roi: Roi | None = None) -> RunResult:
    raise NotImplementedError("팀원 3 · 12/9")


def list_runs(actor: Actor, image_id: str) -> list[dict]:
    raise NotImplementedError("팀원 3 · 12/9")
