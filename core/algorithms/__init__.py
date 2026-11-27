"""영상처리 알고리즘 (계획서 7장). 담당: 팀원 3.

A1 color_constancy (Shades of Gray) · A2 hair_removal (Black-hat + inpaint)
· A3 segmentation (Otsu). 모든 함수는 입력 배열을 바꾸지 않고 복사본을 처리한다.
계산 방식을 바꾸면 ALGO_VERSION을 올린다.
"""
ALGO_VERSION = "0.1"

DEFAULT_PARAMS: dict = {
    "color_constancy": {"p": 6, "gamma": 1.0},
    "hair_removal": {"kernel": 17, "threshold": 10, "inpaint_radius": 5},
    "segmentation": {"blur": 5, "channel": "blue", "morph": 7},
}


def run_pipeline(rgb, params: dict | None = None):
    """A1 → A2 → A3 고정 파이프라인. 반환: (처리 결과 RGB, 마스크 bool HxW, info dict).

    12/3: 첫 버전(A1 + 임시 Otsu) → 팀원 4에게 전달, 12/8: 최종판.
    """
    raise NotImplementedError("팀원 3 · 12/3")
