---
title: recoding — 사용 설명서
created: 2026-11-20
tags:
  - project/recoding
  - readme
---

# recoding

스마트폰 산책 녹음(Syncthing 동기화) → **한국어 전사 → 키워드 1개로 파일명 → Obsidian `result/`에 md 저장** 파이프라인.
설계: [[design_v2]] · 요구사항: [[spec]]

- 엔진: **Apple `SpeechTranscriber`** (macOS 26+, 무설치·무료·온디바이스). `whispercpp` 어댑터도 내장(윈도우 이식용).
- 의존성: **Python 3.11+ 표준 라이브러리만** (외부 pip 패키지 0개) + ffmpeg + Swift(헬퍼 빌드용)

---

## 1. 최초 설치 (1회)

```bash
cd ~/obsidian/obsidian_pub/hugo_pub/0.Projects/recoding

# 1) 가상환경 (pyenv 3.12 기준)
~/.pyenv/versions/3.12.3/bin/python3 -m venv .venv

# 2) Swift 헬퍼 빌드 (macOS 26+)
./platforms/macos/build.sh

# 3) 환경 점검
.venv/bin/python main.py doctor
```

`doctor` 출력에서 ffmpeg/ffprobe/엔진/ledger 가 모두 OK 이면 준비 완료.

> [!tip] 실행은 그냥 `python3 main.py` 로
> 시스템 파이썬(3.9)으로 실행해도 `main.py` 가 **자동으로 `.venv` 파이썬(3.12)으로 재실행**한다.
> `.venv` 가 없을 때만 "Python 3.11+ 필요" 안내를 내고 종료한다(트레이스백 없음).

```bash
# 4) 언어 자산 확인 (ko-KR 이 installed 여야 함)
.venv/bin/python main.py helper --list-locales
```

---

## 2. 사용법

| 명령 | 설명 |
|---|---|
| `python main.py doctor` | 환경·엔진·경로·ledger 상태 점검 |
| `python main.py once` | 안정화된 신규 파일을 전부 처리하고 종료 |
| `python main.py once --limit 2` | 최대 2개만 |
| `python main.py once --retry` | `failed` 상태 재시도 |
| `python main.py file "음성 001.m4a"` | 지정 파일 1개 즉시 처리 (아카이브에서도 찾음) |
| `python main.py watch` | 상주 폴링 감시 (Ctrl-C 종료) |
| `python main.py list` | 처리 이력 표 |
| `python main.py bootstrap` | **현재 있는 파일을 전부 `ignored` 등록** (기존분 일괄 처리 방지) |
| `python main.py reset --all` | 이력 초기화 (재처리 허용) |
| `python main.py reset "파일명"` | 특정 파일 이력만 삭제 |
| `python3 run_tests.py` | **테스트 실행** (stdlib unittest, 21개) |
| `-n / --dry-run` | 파일 쓰기·이동 없이 미리보기 |
| `-v / --verbose` | DEBUG 로그 |

### 테스트

```bash
python3 run_tests.py        # 요약 (구버전 파이썬이면 .venv 로 자동 재실행)
python3 run_tests.py -v     # 테스트별 출력
```

표준 라이브러리 `unittest` 만 사용한다(추가 의존성 0). 커버: 파일명 규칙·시간포맷·문단화·
세그먼트 정리·키워드 휴리스틱·띄어쓰기 병합(문자 보존)·ledger CRUD·config·파이프라인 통합
(감지→처리→아카이브→중복)·손상/짧은 파일·스캔 중 파일 소실.

### 처리 흐름

```
신규 파일 감지 → 안정화(size+mtime 2회 동일) → sha1 중복 확인
  → ffprobe 길이(3초 미만 skip) → 전사 → 무음/반복 제거
  → 키워드+한줄요약(LLM) → 띄어쓰기 교정(검증) → result/{키워드}.md
  → 원본을 recoding_done/ 으로 이동 → ledger 기록
```

---

## 3. 자동화 (launchd)

```bash
cp platforms/macos/com.smartkgh.recoding.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.smartkgh.recoding.plist

launchctl list | grep recoding          # 확인
launchctl unload ~/Library/LaunchAgents/com.smartkgh.recoding.plist   # 해제
```

- `WatchPaths`: Syncthing 수신 폴더에 변화가 생기면 즉시 `once` 1회 실행
- `StartInterval 300`: 이벤트가 없어도 5분마다 안전 스캔 (안정화 대기 파일 회수)
- 로그: `~/syncthing/recoding_state/logs/` (`recoding-YYYYMM.log`, `launchd.err.log`)
- 단일 실행 락: `~/syncthing/recoding_state/lock` — launchd 와 수동 실행이 겹치면 나중 것이 즉시 건너뛴다

> [!note] 왜 상주 프로세스가 아닌가
> launchd one-shot 방식은 크래시·재부팅에 자동 복구되고 메모리를 점유하지 않는다. 상태는 ledger에 있으므로 언제 죽어도 이어서 처리된다.

---

## 4. 확정된 결정 (2026-11-20)

| 항목 | 결정 |
|---|---|
| 수신 경로 | `~/syncthing/recoding` (spec의 `~/recoding` 아님) |
| 기본 엔진 | `apple` (SpeechTranscriber, ko-KR) |
| 원본 처리 | 처리 후 **`~/syncthing/recoding_done/` 로 이동** |
| 파일명 | `{키워드}.md` (예: `재건축추진위회의.md`) |
| 본문 | 전사문 + 한 줄 요약 + 구간 타임스탬프(2개 이상일 때) |
| 기존 12개 | 가장 짧은 2개만 처리, 나머지 10개는 `ignored` |
| 윈도우 | 2차. `platforms/windows/install.md` 초안만 작성 |

> [!warning] 아카이브 위치 주의
> `_done/`을 **Syncthing 폴더 안**에 두면 원본이 폰으로 다시 동기화되어 폰 저장공간을 계속 먹는다.
> 그래서 아카이브를 `~/syncthing/recoding_done/`(동기화 폴더의 형제 디렉터리)로 분리했다.

---

## 5. 자주 바꾸는 설정 (`config.toml`)

| 설정 | 기본값 | 의미 |
|---|---|---|
| `[asr].engine` | `apple` | `apple` / `whispercpp` |
| `[asr].min_duration` | `3.0` | 이보다 짧으면 skip |
| `[asr].settle_seconds` | `10` | 안정화 대기 |
| `[output].filename` | `{keyword}` | `{date} {keyword}` 로 바꾸면 `2026-11-20 재건축.md` |
| `[output].include_timestamps` | `true` | `## 구간` 섹션 |
| `[output].include_summary` | `true` | `> [!quote] 핵심 한 줄` |
| `[keyword].provider` | `deepseek` | `deepseek` / `openrouter` / `heuristic` |
| `[postprocess].spacing_fix` | `true` | Apple 엔진 띄어쓰기 교정(LLM, 청크 단위 + 2중 검증) |
| `[postprocess].chunk_chars` | `3000` | 한 번에 교정할 분량. 52분 녹음(13.6k자) ≈ 5청크 |
| `[postprocess].max_total_chars` | `100000` | 이보다 긴 전사문은 교정 생략 |
| `[archive].move_originals` | `true` | false면 원본을 수신 폴더에 남긴다 |

엔진 전환은 한 줄이면 된다:

```bash
# whisper.cpp 로 교체 (brew install whisper-cpp 필요, 모델 ~1.6GB)
# config.toml → [asr] engine = "whispercpp"
```

---

## 6. 성능 실측 (2026-11-20, M-series 32GB)

| 입력 | 길이 | 전사 시간 | 결과 |
|---|---|---|---|
| `음성 261117_093336.m4a` | 4초 | 0.14초 | 노트 생성 1.0초 |
| `음성 메모 001.m4a` | 7초 | 0.14초 | 노트 생성 1.1초 |
| `음성 261120_155500.m4a` | 10초 | 0.15초 | 노트 생성 1.3초 |
| **`음성 004.m4a`** | **52분 1초** | **17초** (약 180배 실시간) | 13,607자 · 구간 218개 |
| 52분 + 띄어쓰기 교정(5청크) | — | +68초 (총 85초) | LLM 5회 호출 |
| 나머지 9개 일괄(총 34분) | 1.3초~14분51초 | 51초 | 노트 7개 + skip 2개 |

> [!note] 띄어쓰기 교정은 선택
> 전사 자체는 17초인데 교정이 68초를 더 쓴다. 긴 녹음은 `[postprocess].spacing_fix = false` 로 끄면 5배 빠르다(대신 어절이 붙어 나옴).

---

## 7. 알려진 제한

| 제한 | 내용 / 대응 |
|---|---|
| Apple 엔진 띄어쓰기 | 어절을 붙여서 내보내는 경우가 있다 → `spacing_fix`로 공백만 교정(문자 동일성 검증 통과 시에만 적용) |
| 고유명사·전문용어 | Apple 온디바이스 모델의 약점. 정확도가 중요하면 `whispercpp` 전환 |
| 52분 장시간 파일 | 전사는 17초지만 띄어쓰기 교정이 청크 5회(≈68초) 추가된다. 필요 없으면 `spacing_fix = false` |
| 인물 실명 | 전사문이 DeepSeek(키워드 생성)로 전송된다. 완전 로컬을 원하면 `[keyword].provider = "heuristic"` |
| NFD 파일명 | macOS Syncthing은 NFD로 저장 → 내부에서 NFC 정규화해 처리 |
| 3초 미만 녹음 | `skipped` 처리 후 아카이브로 이동 |

---

## 8. 디렉터리 구조

```
0.Projects/recoding/
├── main.py                 # CLI
├── config.toml             # 설정
├── core/                   # 크로스플랫폼 코어 (윈도우 이식 시 무수정)
│   ├── config.py  ledger.py  pipeline.py  render.py  keyword.py  spacing.py  log.py
├── adapters/               # 엔진 교체 경계 (유일한 플랫폼 분기)
│   ├── base.py  asr_apple.py  asr_whispercpp.py
├── platforms/
│   ├── macos/  SpeechHelper.swift  build.sh  com.smartkgh.recoding.plist
│   └── windows/ install.md
├── result/                 # 산출물 (Obsidian 노트) + _raw/*.json
└── .venv/                  # (git ignore)

{프로젝트}/tests/            # unittest 22개 · run_tests.py

~/syncthing/recoding/          # 수신 (Syncthing 전용, 상태 파일 없음)
├── 음성 261118_134537.m4a
└── .stfolder/
~/syncthing/recoding_state/    # 상태 (동기화 폴더 밖)
├── ledger.sqlite  lock
└── logs/  tmp/
~/syncthing/recoding_done/     # 처리 완료 원본
~/syncthing/recoding_failed/   # 손상 파일
```

---

## 9. 트러블슈팅

| 증상 | 확인 |
|---|---|
| `SpeechHelper 가 없습니다` | `./platforms/macos/build.sh` 실행 |
| `locale not supported` | `main.py helper --list-locales` 로 ko-KR installed 확인 |
| 파일이 계속 처리 안 됨 | `main.py list` 에서 status 확인. `ignored` 면 `reset` 후 `file` 로 수동 처리 |
| `처리 대상 없음` | 신규 파일은 첫 스캔에서 등록만 되고 **다음 스캔(10초 후)** 에 처리된다 |
| `건너뜀: 다른 recoding 프로세스가 실행 중` | 정상 동작. launchd 와 수동 실행이 겹친 경우로, 중복 처리를 막은 것 |
| `ModuleNotFoundError: tomllib` | Python 3.9 로 실행된 경우. `.venv` 가 있으면 자동 재실행되므로, 이 오류가 뜨면 `.venv` 부재 → 1번 설치 단계 재실행 |
| 키워드가 영어/이상함 | `main.py doctor` 로 API 키 확인. 키가 없으면 휴리스틱 폴백 |
| 원본이 폰에 계속 남음 | `[archive].move_originals = true` 인지, `done_dir` 가 Syncthing 폴더 밖인지 확인 |
