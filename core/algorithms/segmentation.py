"""A3 병변 분할: 블러 → 채널 선택 → Otsu → 열기·닫기 → 중앙 최대 연결 성분. 담당: 팀원 3 · 기한 12/8.

실패 판정: 면적이 영상의 1% 미만·80% 초과, 또는 윤곽의 50% 이상이 가장자리에 닿음.
"""


def apply(rgb, blur: int = 5, channel: str = "blue", morph: int = 7):
    """반환: (마스크 bool HxW, info dict {"failed": bool, "reason": str, ...})."""
    raise NotImplementedError("팀원 3 · 12/8")
