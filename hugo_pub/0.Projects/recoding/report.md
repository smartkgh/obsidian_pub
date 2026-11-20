---
title: recoding — 작업 정리 (구현 완료 보고)
created: 2026-11-20
status: 완료 — macOS 1차 동작 중
tags:
  - project/recoding
  - report
  - asr
---

# recoding 작업 정리

> [!abstract] 한 줄 요약
> 폰 산책 녹음이 Syncthing으로 들어오면 **자동으로 한국어 전사 → 키워드 파일명 → Obsidian 노트**로 저장되는 로컬 파이프라인을 macOS에서 완성했다. 52분 녹음도 **17초**에 전사된다. 윈도우는 설계상 최소 변경(설정 4곳)으로 이식 가능하도록 경계를 미리 분리해 뒀다.

| 항목 | 내용 |
|---|---|
| 착수 | 2026-11-20 (설계 v1 → v2 승인 후) |
| 상태 | **구현·검증 완료**, launchd 자동화 등록되어 상시 동작 |
| 산출물 | 노트 5개 · 아카이브 원본 5개 · ledger 14행 |
| 문서 | [[spec]] → [[design_v1]] → [[design_v2]] → [[README]] |

---

## 1. 무엇을 만들었나

```
recoding/
├── main.py               CLI 8개 명령 (doctor/once/file/watch/list/bootstrap/reset/helper)
├── config.toml           경로·엔진·출력·키워드·아카이브·후처리 설정
├── core/                 크로스플랫폼 코어 — 윈도우 이식 시 수정 0줄
│   ├── pipeline.py       감지→안정화→중복→전사→정리→키워드→렌더→아카이브
│   ├── config.py         TOML + .env 로딩, 점표기 섹션
│   ├── ledger.py         SQLite(WAL) 이력, sha1 키, 상태머신
│   ├── render.py         Obsidian md 렌더, 파일명 규칙(NFC·금지문자·길이·중복)
│   ├── keyword.py        키워드+한줄요약 (DeepSeek 1회, 실패 시 휴리스틱)
│   ├── spacing.py        띄어쓰기 교정 (문자 고정, 공백만 이식)
│   └── log.py            파일+stderr 로깅
├── adapters/             엔진 교체 경계 = 유일한 플랫폼 분기
│   ├── base.py           ASRAdapter / Transcript 스키마
│   ├── asr_apple.py      SpeechTranscriber (macOS, 기본 엔진)
│   └── asr_whispercpp.py whisper-cli (윈도우·대안, 1차에 이미 작성)
└── platforms/
    ├── macos/            SpeechHelper.swift · build.sh · launchd plist(등록됨)
    └── windows/          install.md (2차 체크리스트, 초안)
```

**의존성 0개** — Python 3.11+ 표준 라이브러리 + ffmpeg + Swift(헬퍼 빌드). pip 패키지를 쓰지 않아 윈도우 이식 시 환경 문제가 없다.

---

## 2. 확정된 결정

| 항목 | 결정 | 근거 |
|---|---|---|
| 수신 경로 | `~/syncthing/recoding` | spec의 `~/recoding`은 실측과 불일치 |
| 구조 | **하이브리드 어댑터** (Python 코어 + 교체형 ASR) | 맥 품질 유지 + 윈도우 최소 변경 |
| 기본 엔진 | `apple` SpeechTranscriber (ko-KR) | 무설치·무료·온디바이스·최속도 |
| 원본 처리 | `~/syncthing/recoding_done/` 로 이동 | **Syncthing 폴더 밖** (재동기화 방지) |
| 파일명 | `{키워드}.md` | spec 원문("키워드 하나로") 준수, `{date} {keyword}` 로 전환 가능 |
| 본문 | 전사 + 한 줄 요약 + 구간(2개 이상일 때) | 읽기·검색 균형 |
| 기존 12개 | 가장 짧은 3개만 처리, 나머지 9개 `ignored` | 일괄 처리 방지 요청 |
| 자동화 | launchd one-shot (`WatchPaths` + 5분 스캔) | 상주 프로세스 없이 크래시·재부팅 자동 복구 |
| 윈도우 | 2차로 보류, `install.md` 초안만 | — |

---

## 3. 검증 결과

### 3.1 실측 성능 (M-series 32GB)

| 입력 | 길이 | 전사 | 총 소요 | 결과 |
|---|---|---|---|---|
| `음성 261117_093336.m4a` | 4초 | 0.14초 | 1.0초 | `좋은아침.md` |
| `음성 메모 001.m4a` | 7초 | 0.14초 | 1.1초 | `자기소개.md` |
| `음성 261120_155500.m4a` | 10초 | 0.15초 | 1.3초 | `한강산책.md` |
| `음성 261120_160500.m4a` | 10초 | 0.15초 | 3.8초 | `재건축추진위회의.md` |
| **`음성 004.m4a`** | **52분 1초** | **17초** | 85초 | `인공지능과인간.md` (13,607자, 구간 218) |

- 52분 파일 = **약 180배 실시간**. 17초가 전사, 나머지 68초는 띄어쓰기 교정(LLM 5청크).
- 자동 감지 실측: 파일 투입 → 노트 생성까지 **24초**(launchd 트리거 + 안정화 대기 10초 포함).

### 3.2 정식 테스트 (stdlib unittest, 21개)

```bash
python3 run_tests.py     # OK (21 tests)
```

| 파일 | 범위 |
|---|---|
| `tests/test_core.py` | render 6 · clean/keyword 3 · spacing 4 · ledger 1 · config 2 · main 가드 2 · pipeline 3 |

### 3.3 ad-hoc 검증 (정식 테스트 스위트 아님)

임시 스크립트로 변경 동작만 검증 — **28/28 PASS**. 전부 임시 디렉터리에서 실행해 실제 녹음·노트·ledger 는 건드리지 않았다.

| 대상 | 검증 내용 |
|---|---|
| `spacing.py` | 문자 고정 병합 3케이스(단어 삽입 시도 포함), 문단 보존, `fix_spacing` 6분기, 청크 상한 준수, 전체 문자 보존 |
| `pipeline.py` | 스캔 중 파일 소실(`FileNotFoundError`)에도 미붕괴, 통합 흐름(등록→처리→노트→아카이브→중복 없음) |
| `config.toml` | 엔진·청크·총량·아카이브 경로 값 검증 |
| 라이브 | `doctor` 전 항목 OK, `once` 무처리, 노트 5 = 아카이브 5 |

---

## 4. 구현 중 발견해 고친 것 (설계 결함 포함)

| # | 문제 | 원인 | 수정 |
|---|---|---|---|
| 1 | 원본이 **폰으로 재동기화**되어 폰 저장공간 소모 | 설계 v1/v2가 `_done/`을 Syncthing 폴더 **안**에 두도록 했음 | 아카이브를 `~/syncthing/recoding_done/`(형제 디렉터리)로 분리 |
| 2 | 한국어가 **어절 단위로 붙어 나옴** (`동의서는이번주까지걷기로했어요`) | Apple 온디바이스 모델의 한글 띄어쓰기 약점 | 공백만 교정하는 후처리 추가 |
| 3 | 교정 청크가 **통째로 버려짐** (5개 중 2개) | LLM이 `영향 받지`처럼 단어를 1개 삽입 → 문자 동일성 검증 실패 | `difflib` 정렬로 **원문 문자는 고정, 공백 위치만 이식** → 단어 변조 위험 구조적 0, 부분 적용 가능 |
| 4 | 신규 녹음이 **최대 5분 대기** | 트리거 1회로는 안정화 대기를 못 넘김 | `once`가 같은 실행에서 10초 대기 후 재스캔 |
| 5 | 스캔 중 파일이 사라지면 `once` **전체 크래시** | `file_sha1()`이 `stat()` try 블록 밖 | `FileNotFoundError`/`PermissionError` 동시 처리 (윈도우 파일 잠금 대비) |
| 6 | `python3 main.py` 실행 시 `ModuleNotFoundError: tomllib` | 시스템 파이썬 3.9 로 실행 (코드는 3.11+ 필요) | `main.py` 최상단 **인터프리터 가드** — 구버전이면 `.venv` 파이썬으로 자기 재실행, venv 없으면 안내 후 종료 |
| 7 | 가드가 재실행 대상을 `main.py` 로 고정 → `run_tests.py` 에서 import 시 argparse 오류 | 진입 스크립트를 구분하지 않음 | **원래 진입 스크립트(`sys.argv[0]`)** 를 재실행하도록 수정 |

> [!tip] 3번이 이 작업의 핵심 교훈
> LLM에게 텍스트를 고치게 하면 반드시 내용을 바꾼다. **"LLM은 판단만, 원본은 코드가 소유"** 구조로 바꾸면 검증 없이도 안전해진다.

---

## 5. 자주 쓰는 명령

```bash
cd ~/obsidian/obsidian_pub/hugo_pub/0.Projects/recoding

.venv/bin/python main.py doctor                 # 환경 점검
.venv/bin/python main.py once                   # 신규 처리
.venv/bin/python main.py file "음성 002.m4a"     # 지정 파일 즉시 처리(아카이브에서도 검색)
.venv/bin/python main.py list                   # 이력
.venv/bin/python main.py -n file "…"            # dry-run
```

- 자동화 해제: `launchctl unload ~/Library/LaunchAgents/com.smartkgh.recoding.plist`
- 로그: `~/syncthing/recoding/.recoding/logs/`

---

## 6. 남은 일

| 우선순위 | 항목 | 비고 |
|---|---|---|
| 선택 | 기존 `ignored` 9개 처리 | 14분·12분·52분 외 파일들. `reset` → `file` 개별 실행 |
| 2차 | **Windows 이식** | [[install]] 체크리스트. 코어 diff 0줄, 설정 4곳 + 작업 스케줄러 |
| 선택 | 파일명 규칙 전환 | `filename = "{date} {keyword}"` |
| 선택 | 품질 비교 | `engine = "whispercpp"` 로 같은 코어에서 A/B (고유명사 정확도) |
| Phase 3 | 태그 자동분류·월간 인덱스·주간 다이제스트 | 설계 v2 로드맵 |

> [!warning] 프라이버시
> 전사 오디오는 완전 로컬이지만 **전사문 텍스트는 키워드·띄어쓰기 교정을 위해 DeepSeek 로 전송**된다. 완전 로컬이 필요하면 `[keyword].provider = "heuristic"`, `[postprocess].spacing_fix = false`.

---
*관련: [[spec]] · [[design_v1]] · [[design_v2]] · [[README]] · [[install]]*
