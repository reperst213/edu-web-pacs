"""특화 기능 특징 벡터 (계획서 8.2). 담당: 팀원 4 · 기한 12/7.

75차원 = Lab 평균·표준편차 6 + 색 다양도 1 + a*b* 히스토그램 8×8 64
       + 면적 비율 1 + 비대칭도 2 + 경계 불규칙도 1
"""
FEATURE_VERSION = "0.1"
FEATURE_DIM = 75


def extract(rgb, mask):
    """반환: float32 배열 (75,)."""
    raise NotImplementedError("팀원 4 · 12/7")
