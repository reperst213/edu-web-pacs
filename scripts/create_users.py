"""테스트 계정 생성 (FR-13 준비). 담당: 팀원 1 · 기한 12/1.

Firebase Auth 계정과 Firestore users/{uid} 문서(role)를 함께 만든다.

    uv run python scripts/create_users.py --dry-run     # 무엇을 할지만 출력
    uv run python scripts/create_users.py               # 비밀번호를 입력받아 생성

- 비밀번호는 실행할 때 입력받는다. 코드·README·출력에 남기지 않는다.
- 다시 실행해도 안전하다: 이미 있는 계정은 비밀번호를 건드리지 않고 users 문서만 맞춘다.
- 문서 쓰기가 실패하면 방금 만든 Auth 계정을 지운다 (반쪽 계정 방지).
- 키: .env의 GOOGLE_APPLICATION_CREDENTIALS (저장소 밖 전체 경로).
"""
import argparse
import getpass
import sys
from datetime import datetime, timezone
from typing import NamedTuple

DEFAULT_DOMAIN = "dermapacs.test"  # .test는 실제로 쓰이지 않는 예약 도메인
MIN_PASSWORD = 8


class Account(NamedTuple):
    local: str          # 이메일 @ 앞부분
    role: str
    display_name: str


ACCOUNTS: tuple[Account, ...] = (
    Account("registrar1", "registrar", "등록 담당자 1"),
    Account("reviewer1", "reviewer", "검토자 1"),
    Account("reviewer2", "reviewer", "검토자 2 (미배정 거부 시험용)"),
    Account("admin1", "admin", "관리자 1"),
)


def ensure_user(fb_auth, db, email: str, display_name: str, role: str,
                password: str) -> tuple[str, bool]:
    """계정과 users 문서를 맞춘다. 반환: (uid, 새로 만들었는지)."""
    try:
        uid = fb_auth.get_user_by_email(email).uid
        created = False
    except fb_auth.UserNotFoundError:
        uid = fb_auth.create_user(email=email, password=password,
                                  display_name=display_name).uid
        created = True

    ref = db.collection("users").document(uid)
    doc = {"email": email, "display_name": display_name, "role": role, "active": True}
    try:
        if created or not ref.get().exists:
            doc["created_at"] = datetime.now(timezone.utc)
        ref.set(doc, merge=True)
    except Exception:
        if created:
            fb_auth.delete_user(uid)
        raise
    return uid, created


def read_password() -> str:
    pw = getpass.getpass(f"테스트 계정 공통 비밀번호 ({MIN_PASSWORD}자 이상): ")
    if len(pw) < MIN_PASSWORD:
        sys.exit(f"비밀번호는 {MIN_PASSWORD}자 이상이어야 합니다.")
    if getpass.getpass("한 번 더: ") != pw:
        sys.exit("두 비밀번호가 다릅니다.")
    return pw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="테스트 계정 4개 생성")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="이메일 도메인")
    parser.add_argument("--dry-run", action="store_true", help="만들지 않고 계획만 출력")
    args = parser.parse_args(argv)

    emails = [(f"{a.local}@{args.domain}", a) for a in ACCOUNTS]
    if args.dry_run:
        for email, a in emails:
            print(f"[dry-run] {email:32} {a.role:10} {a.display_name}")
        return 0

    from dotenv import load_dotenv
    import firebase_admin
    from firebase_admin import auth as fb_auth, firestore

    load_dotenv()
    password = read_password()
    if not firebase_admin._apps:
        firebase_admin.initialize_app()  # GOOGLE_APPLICATION_CREDENTIALS 사용
    db = firestore.client()

    for email, a in emails:
        uid, created = ensure_user(fb_auth, db, email, a.display_name, a.role, password)
        print(f"{'새로 만듦' if created else '이미 있음'}  {email:32} {a.role:10} uid={uid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
