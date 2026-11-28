# edu-web-pacs (DermaPACS-Edu)

- 저장소: https://github.com/reperst213/edu-web-pacs
- 서비스: http://s.jedutools.io:50076

피부경(dermoscopy) 컬러 DICOM을 등록·조회·처리·검토하는 **교육용 웹 PACS**입니다.
특화 기능은 "ROI 특징 기반 유사 병변 검색 + 근거 비교 카드"입니다.
초급프로젝트 PBL Term Project (마감 2026-12-15 23:59).

> **교육용 모의 케이스 · 진단용 아님.** 모든 수치와 검색 결과는 교육용이며 실제 진단이나 임상 성능을 뜻하지 않습니다.

## 팀원

| 번호 | 이름 | 역할 | GitHub |
| --- | --- | --- | --- |
| 팀원 1 | 조은보 (팀장) | 플랫폼 · 권한 · 배포 | [reperst213](https://github.com/reperst213) |
| 팀원 2 | 장수희 | 데이터 · 케이스 · 기록 | |
| 팀원 3 | 조서린 | 뷰어 · 영상처리 | |
| 팀원 4 | 장민성 | 검토 흐름 · 특화 기능 | |

자기 행의 GitHub 칸은 각자 PR로 채웁니다 (아래 "처음 할 일" 6번).

## 처음 할 일 (11/29까지)

1. 저장소를 clone하고 커밋 작성자를 본인 GitHub 계정과 맞춥니다.
   ```bash
   # HTTPS (처음이면 이쪽이 쉽다. push할 때 GitHub 로그인 창이 뜬다)
   git clone https://github.com/reperst213/edu-web-pacs.git
   # SSH 키를 GitHub에 등록해 둔 사람은
   # git clone git@github.com:reperst213/edu-web-pacs.git
   cd edu-web-pacs
   git config user.name "GitHub 사용자 이름"
   git config user.email "GitHub에 등록한 이메일"
   ```
   팀장이 보낸 Collaborator 초대를 먼저 수락해야 push할 수 있습니다.
2. uv를 설치합니다 (macOS: `brew install uv` 또는 `curl -LsSf https://astral.sh/uv/install.sh | sh`, Windows: `winget install --id=astral-sh.uv -e`).
3. 의존성을 설치합니다. Python 3.12가 없으면 uv가 내려받습니다.
   ```bash
   uv sync
   ```
4. 설정 파일을 만듭니다.
   ```bash
   cp .env.example .env      # Windows: copy .env.example .env
   ```
   `APP_MODE=local` 그대로 두면 로그인 없이 개발할 수 있습니다.
5. 실행과 테스트를 확인합니다.
   ```bash
   uv run streamlit run app.py   # 브라우저에서 http://localhost:8080
   uv run pytest -q
   ```
   사이드바에서 역할(등록 담당자·검토자·관리자)을 바꾸면 메뉴가 달라집니다.
6. Git 흐름 연습: Issue를 만들고 → `docs/<번호>-team-table` 브랜치에서 위 팀원 표의 자기 GitHub 칸을 채워 → PR → 리뷰 → 병합까지 한 번 해봅니다.

## 설정 (`.env`)

| 항목 | 예 | 설명 |
| --- | --- | --- |
| `APP_MODE` | `local` / `firebase` | local이면 로그인 생략(사이드바에서 역할 선택) + 메모리 저장소 |
| `DEV_ROLE` | `reviewer` | 로컬 모드의 기본 역할 |
| `FIREBASE_WEB_API_KEY` | (팀장에게 1:1로 받음) | Firebase 로그인용 |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/Users/본인계정/.config/edu-web-pacs/sa-이름.json` | 서비스 계정 키 전체 경로 (저장소 밖) |
| `DATA_DIR` | `./data_local` | 원본·결과·특징 파일 위치 |
| `DEPLOY` | `0` / `1` | JCloud에서는 1 (local 모드로 시작되지 않음) |

`.env`, `secrets/`, 데이터 파일은 **절대 커밋하지 않습니다** (`.gitignore`에 있음).

### 서비스 계정 키는 저장소 밖에

서비스 계정 키(JSON)가 있으면 데이터베이스 전체를 읽고 쓸 수 있습니다. 그래서 저장소 폴더 **밖**에 둡니다. 저장소 안에 두면 채팅 앱(Claude 앱, ChatGPT 등)에 폴더를 연결할 때 함께 노출될 수 있습니다.

```bash
# Mac (Windows는 C:\Users\본인계정\.config\edu-web-pacs\ 에 둔다)
mkdir -p ~/.config/edu-web-pacs && chmod 700 ~/.config/edu-web-pacs
mv ~/Downloads/<받은키>.json ~/.config/edu-web-pacs/sa-이름.json
chmod 600 ~/.config/edu-web-pacs/sa-이름.json
```

그리고 `.env`의 `GOOGLE_APPLICATION_CREDENTIALS`에 그 **전체 경로**를 적습니다 (`~`는 쓰지 않음).
`secrets/` 폴더는 쓰지 않지만, 실수로 넣어도 Git(`.gitignore`)과 AI 도구(`.claude/settings.json`, `.codex/config.toml`)가 막도록 규칙은 남겨 둡니다.
키와 `.env` 내용은 어떤 AI 채팅에도 붙여 넣지 않습니다.

## 폴더 구조

```text
app.py            진입점 · 역할별 메뉴 (팀원 1)
pages/            화면 P0~P8 (파일 맨 위에 담당자 표시)
ui/               공통 화면 부품 (팀원 1)
services/         서비스 계층 · 권한 검사 · 상태 전이 (함수 시그니처는 계획서 18장)
repositories/     저장소 인터페이스 · Firestore/메모리 구현 (팀원 2)
core/             순수 함수: 영상 입출력, 알고리즘, ROI, 특징 (Firebase·Streamlit 없음)
storage/          파일 저장 규칙 (팀원 2)
scripts/          데이터 선별·시드·특징 생성·정합성 점검·백업
experiments/      알고리즘·특화 기능 비교 실험
tests/            pytest
deploy/           JCloud systemd 서비스 파일
data_manifest/    선별 데이터 목록 CSV (데이터 자체는 팀 드라이브)
docs/             AI 사용 기록, 보고서용 그림
```

아직 구현되지 않은 함수는 `NotImplementedError("팀원 N · 기한")`을 던집니다. 이름과 인자는 바꾸지 말고 내용을 채웁니다. 바꿔야 하면 Issue로 제안합니다.

## 협업 규칙 (요약)

- 모든 변경은 Issue → 브랜치(`feat/<번호>-<설명>`) → PR → 리뷰 짝 승인 → 병합.
- PR에는 테스트 결과와 AI 사용 내용을 적습니다 (템플릿 있음). `docs/ai_usage.md`에도 한 줄 추가합니다.
- 남의 담당 파일은 직접 고치지 않고 Issue를 남깁니다.
- `st.session_state` 키 접두어: `auth.`(1), `case.`(2), `viewer.`(3), `review.`·`search.`(4).
- 자세한 내용은 팀 계획서(DermaPACS-Edu 프로젝트 계획서) 14·17·18·20장.

## Firebase 설정 (팀원 1)

- Authentication: 이메일/비밀번호 로그인 사용.
- Cloud Firestore: 위치 asia-northeast3(서울). 보안 규칙은 `firestore.rules`(전면 거부), 색인은 `firestore.indexes.json`.
- 앱은 서버에서 Admin SDK로만 Firestore에 접근하고, 권한 검사는 `services/permissions.py`가 합니다.

### 테스트 계정

| 이메일 | 역할 | 용도 |
| --- | --- | --- |
| `registrar1@dermapacs.test` | 등록 담당자 | 케이스 등록·보완 재제출 |
| `reviewer1@dermapacs.test` | 검토자 | 배정받아 검토 |
| `reviewer2@dermapacs.test` | 검토자 | 미배정 케이스 접근 거부 시험 |
| `admin1@dermapacs.test` | 관리자 | 배정·재오픈·역할 변경·감사 로그 |

비밀번호는 README·코드에 적지 않고 팀장이 1:1로 알려 줍니다. 계정은 팀장이 만듭니다.

```bash
uv run python scripts/create_users.py --dry-run   # 무엇을 만들지만 출력
uv run python scripts/create_users.py             # 비밀번호를 입력받아 Auth 계정 + users/{uid} 생성
```

다시 실행해도 안전합니다 (이미 있는 계정은 비밀번호를 그대로 두고 역할만 맞춤).

## JCloud 배포 (팀원 1)

| 항목 | 값 |
| --- | --- |
| 서비스 URL | http://s.jedutools.io:50076 (서버 안에서는 8080) |
| SSH | `s.jedutools.io` 포트 `10076`, 계정 `ubuntu` |
| 서버 | Ubuntu 24.04 · RAM 2GB(+스왑 1GB) · 내부 IP 10.0.0.76 |
| 경로 | 코드 `/srv/dermapacs/app` · 데이터 `/srv/dermapacs/data` · 키 `/srv/dermapacs/secrets/` |

### 접속

```bash
ssh -i <받은 키 파일 경로> -p 10076 ubuntu@s.jedutools.io
```

SSH 키(`.pem`)는 팀장이 1:1로 전달합니다. 저장소 밖(예: `~/.ssh/`)에 두고 `chmod 600` 합니다.

### 처음 설치 (한 번만)

```bash
sudo mkdir -p /srv/dermapacs/{app,data,secrets} && sudo chown -R ubuntu:ubuntu /srv/dermapacs
chmod 700 /srv/dermapacs/secrets
git clone https://github.com/reperst213/edu-web-pacs.git /srv/dermapacs/app
cd /srv/dermapacs/app && uv sync && uv run pytest -q
# 서버 키를 /srv/dermapacs/secrets/sa-server.json 에 두고 chmod 600 (내 Mac에서 scp로 올림)
cp .env.example .env && chmod 600 .env
# .env: APP_MODE=firebase, DEPLOY=1, DATA_DIR=/srv/dermapacs/data,
#       GOOGLE_APPLICATION_CREDENTIALS=/srv/dermapacs/secrets/sa-server.json, FIREBASE_WEB_API_KEY=...
# deploy/dermapacs.service 의 CHANGE_ME_USER 를 ubuntu 로 바꾼 뒤
sudo cp deploy/dermapacs.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now dermapacs
```

### 새 버전 올리기

```bash
cd /srv/dermapacs/app
git fetch --tags && git checkout v0.1     # 배포는 태그된 커밋으로 (첫 배포 12/2는 main)
uv sync && uv run pytest -q               # 테스트가 통과할 때만 재시작
sudo systemctl restart dermapacs
```

### 상태·로그

```bash
sudo systemctl status dermapacs
journalctl -u dermapacs -f
```

- `DEPLOY=1`이면 `APP_MODE=local`로는 앱이 시작되지 않습니다. 로그인 없는 로컬 모드를 바깥에 띄워 두지 않습니다.
- RAM이 2GB라 서버에서 특징 행렬 생성 같은 무거운 작업은 하지 않습니다 (팀원 PC에서 만들어 결과만 올림).

## 데이터 출처와 이용 조건

- ISIC 2020 Challenge Dataset (SIIM-ISIC Melanoma Classification), doi:10.34970/2020-DS01, **CC BY-NC**.
  Rotemberg V. et al., *Scientific Data* 8, 34 (2021).
- 비상업 교육 목적으로만 사용합니다. 선별한 부분집합은 팀 드라이브로만 공유하고 GitHub에는 올리지 않습니다.
- 화면에는 모의 케이스 ID(MC-0001…)만 표시합니다.
