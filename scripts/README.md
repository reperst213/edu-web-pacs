# scripts

| 파일 | 담당 | 기한 | 내용 |
| --- | --- | --- | --- |
| `create_users.py` | 팀원 1 | 12/1 | 테스트 계정 4개와 users/{uid}.role 생성 |
| `select_subset.py` | 팀원 2 | 12/3 | ISIC 2020에서 약 1,000장 선별 → `data_manifest/subset.csv` (시드 고정) |
| `seed_demo.py` | 팀원 2 | 12/5 | 시연용 모의 케이스 20개 (접수·배정·검토 중·완료 각 5) |
| `build_features.py` | 팀원 4 | 12/9 | 검색 대상 특징 행렬 생성 (팀원 PC에서 실행, 결과만 JCloud로) |
| `reconcile.py` | 팀원 2 | 12/10 | 문서 없는 파일, 파일 없는 문서, 오래된 pending 보고 |
| `backup.py` | 팀원 2 | 12/10 | Firestore 컬렉션 JSON 내보내기 + data 묶기 |
