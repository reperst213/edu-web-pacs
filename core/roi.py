"""ROI 검사·통계 (FR-06). 담당: 팀원 3 · 기한 12/5.

입력 검사: 영상 범위 밖, 너비·높이 8px 미만은 ValidationError.
반환 dict: 채널별(RGB, Lab) mean·var·std·hist, 마스크 면적 비율.
"""
MIN_ROI_SIZE = 8


def roi_stats(rgb, roi=None, mask=None) -> dict:
    raise NotImplementedError("팀원 3 · 12/5")
