"""A2 털 제거: 흑백 → Black-hat → 임계값 마스크 → cv2.inpaint(Telea). 담당: 팀원 3 · 기한 12/8.

파라미터: kernel 9~25, threshold 10~30, inpaint_radius 3~7.
OpenCV 호출 직전·직후에만 BGR로 바꾼다 (계획서 18.4).
"""


def apply(rgb, kernel: int = 17, threshold: int = 10, inpaint_radius: int = 5):
    """반환: (털을 지운 RGB, 털 마스크)."""
    raise NotImplementedError("팀원 3 · 12/8")
