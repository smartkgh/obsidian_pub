---
title: recoding — 음성 녹음 자동 전사 파이프라인 설계안 v2
created: 2026-11-20
status: 설계 (미구현) — 결정 대기
supersedes: "[[design_v1]]"
tags:
  - project/recoding
  - design
  - asr
  - obsidian-automation
  - cross-platform
---

# recoding — 설계안 v2: macOS 우선 + 윈도우 최소변경 이식

> [!abstract] v1에서 바뀐 것
> v1은 "맥에서 가장 좋은 것"만 기준으로 **안 A(순수 Swift 네이티브)** 를 권장했다. v2는 제약이 하나 늘었다.
> **① 1차 목표는 macOS 동작 ② 윈도우는 나중에 '최소 변경'으로 이식.**
> 이 제약 때문에 "1차에 무엇을 고르느냐"가 곧 "2차 이식 비용"이 된다. 결론부터: **대안 3(하이브리드 어댑터) 권장.**

---

## 1. 왜 v1 권장안(A)을 그대로 못 쓰는가

| 안 | macOS | Windows 이식 | 이식 비용 |
|---|---|---|---|
| A. 순수 Swift 네이티브 | ◎ 최상 (무설치·무료·빠름) | ❌ `SpeechAnalyzer`·`FoundationModels`·`AVFoundation`·`launchd` 전부 Apple 전용 | **재작성 (1일+)** — Swift 자산 대부분 폐기, 공유되는 건 md 템플릿과 ledger 스키마뿐 |
| B. whisper.cpp + 스크립트 | ○ 양호 (Metal, 52분 → 5~10분) | ✅ whisper.cpp는 C++ 크로스플랫폼(CUDA/Vulkan/CPU) | **최소 (config 2줄 + 감지 등록)** |
| C. mlx-whisper | ◎ 최고 속도 | ❌ MLX는 Apple Silicon 전용 | 엔진 교체 필수 → 사실상 B로 수렴 |

> [!warning] 핵심 판단
> "윈도우 최소 변경"이 요구사항인 순간, **안 A 단독 채택은 선택지에서 빠진다.** A의 장점(무설치·온디바이스)을 살리면서 이식성도 확보하려면 **엔진을 갈아끼울 수 있는 경계**를 1차부터 설계해야 한다.

---

## 2. 대안 3개 (macOS 우선 + Windows 최소변경 기준)

### 🅰️ 대안 1 — v1 안 A 그대로, 윈도우는 나중에 별도 구현

| 항목 | 내용 |
|---|---|
| macOS | Swift 단일 바이너리 + `launchd`. 최고 성능·무설치 |
| Windows | Python + whisper.cpp로 **처음부터 다시 작성** |
| 공유 자산 | md 템플릿, ledger 스키마, 파일명 규칙 (문서 수준) |

- ✅ 1차 개발이 가장 짧다 (반나절~1일). 맥 경험이 최상.
- ❌ **"최소 변경" 요구에 정면 위배.** 2차에 1일+ 재투자, 그 사이 두 코드베이스가 갈라짐(버그 수정 2회).
- **적합**: 윈도우가 "언젠가 될 수도" 수준이고, 지금 맥 품질만 중요할 때.

---

### 🅱️ 대안 2 — whisper.cpp 단일 파이프라인 (Python 래퍼)

| 구성 요소 | 기술 | 장점 | 단점 |
|---|---|---|---|
| 감지 | Python `watchdog` (맥·윈도우 동일 코드) | 크로스플랫폼, 이벤트 기반 | 상주 프로세스 관리 필요 |
| 전사 | `whisper-cli -m ggml-large-v3-turbo -l ko --output-json` | 명령줄이 **두 OS에서 동일**. 맥 Metal / 윈도우 CUDA | 모델 1.6GB 다운로드, 환각 리스크, 맥에서 A보다 느림 |
| 키워드 | DeepSeek/OpenRouter HTTP | 플랫폼 무관, 한국어 품질 좋음 | 네트워크·키 필요 (파일당 <1원) |
| 오디오 | ffmpeg (경로는 config) | 포맷 무관, 양 OS 빌드 존재 | 경로 하드코딩 금지 |
| 상태 | SQLite (WAL) | 쿼리·재처리 편함, 파일 복사만으로 이전 | 스키마 관리 |
| 실행 | macOS `launchd` / Win 작업 스케줄러·NSSM | 각 OS 표준 방식 | 등록 스크립트 2벌 (문서로 흡수) |

- ✅ **이식 비용 최소.** 코어 코드 100% 공유, 윈도우에서 바뀌는 건 `config.toml`의 바이너리 경로와 등록 방식뿐.
- ✅ 코드베이스 1벌 → 유지보수 단순.
- ❌ 맥에서 **A안 대비 품질·속도 손해**(특히 고유명사/환각). 무설치 장점 상실(brew + 모델 1.6GB).
- **적합**: "두 OS 동등 지원 + 코드 1벌"을 최우선할 때. **예상 구현 3~4시간.**

---

### 🅲 대안 3 — 하이브리드 어댑터 (Python 코어 + 교체형 ASR) ⭐

크로스플랫폼 Python 코어를 두고, **플랫폼 의존 부품만 어댑터로 격리**한다. 맥은 Apple 엔진(무설치·최속도), 윈도우는 whisper.cpp.

```
recoding/
├── core/                     # 크로스플랫폼 · 표준 라이브러리 우선 (이식 시 diff 0)
│   ├── pipeline.py           #   오케스트레이션 (감지→안정화→중복→전사→정리→키워드→렌더→아카이브)
│   ├── watcher.py            #   watchdog (맥·윈도우 공용)
│   ├── ledger.py             #   SQLite(WAL), sha1 키, pending/transcribing/done/failed
│   ├── render.py             #   Obsidian md 렌더
│   ├── keyword.py            #   DeepSeek/OpenRouter + 날짜 fallback
│   └── config.py             #   config.toml 로드, 경로·인코딩 해석
├── adapters/
│   ├── base.py               #   ASRAdapter: transcribe(path) -> Transcript(segments, lang, engine)
│   ├── asr_apple.py          #   macOS: Swift 헬퍼 subprocess → JSON
│   └── asr_whispercpp.py     #   공용: whisper-cli subprocess → JSON  ← 1차에 함께 구현
├── platforms/
│   ├── macos/  SpeechHelper.swift · build.sh · com.user.recoding.plist
│   └── windows/ install.md (작업 스케줄러/NSSM 등록) · 경로 예시
└── config.toml               # asr.engine = "apple" | "whispercpp"
```

| 구성 요소 | 기술 | 장점 | 단점 |
|---|---|---|---|
| 감지 | `watchdog` (공용) | 코드 1벌, 양 OS 검증됨 | 상주 프로세스 (로그 로테이션 필요) |
| 전사(맥) | `SpeechAnalyzer`/`SpeechTranscriber` (ko-KR) | **무설치·무료·온디바이스·최속도**. 오디오가 밖으로 안 나감 | 고유명사·전문용어 약함, Swift 빌드 필요 |
| 전사(윈도우) | `whisper-cli` 어댑터 | 맥에서 미리 검증 가능 → 이식이 "설정 변경"으로 끝남 | — |
| 키워드 | DeepSeek/OpenRouter HTTP (코어) | 플랫폼 무관, 품질 좋음 | 네트워크·키. **온디바이스 아님이 유일한 프라이버시 예외** |
| 오디오 | ffmpeg (config 경로) | 양 OS 표준 | 경로 외부화 필수 |
| 상태 | SQLite WAL | 이전 = 파일 복사 | 동시성은 WAL로 해결 |
| 어댑터 경계 | `ASRAdapter` 인터페이스 + 정규화된 `Transcript` 스키마 | 엔진 교체 = 파일 1개 추가 + config 1줄 | 경계 설계 비용(반나절), 엔진별 출력 정규화 필요 |

> [!tip] 이 안의 핵심 트릭 — "윈도우 이식 리허설"
> **1차에 `asr_whispercpp.py`를 함께 만들고 맥에서 한 번 돌려본다.** 그러면 윈도우에서 실제로 바뀌는 것은 ① `config.toml`의 `asr.engine` 값 ② whisper-cli/ffmpeg 경로 ③ 실행 등록 방식(작업 스케줄러) 세 가지뿐이고, **코어 diff는 0줄**. 윈도우 도착 전에 이식의 80%가 검증된 상태가 된다.

- ✅ 맥 최상 품질 유지 + 윈도우 최소 변경 (요구사항 둘 다 충족)
- ✅ 2차에 엔진 품질 비교가 쉬움 (같은 코어에서 apple vs whispercpp A/B)
- ❌ 1차 구현이 대안 2보다 조금 길다 (어댑터 1개 + Swift 헬퍼 빌드) — **예상 6~8시간**
- ❌ Swift 헬퍼는 서명/재빌드 관리 필요(`build.sh`로 고정)

---

## 3. 권장안

> [!success] 권장: **대안 3 (하이브리드 어댑터)**
> ① 맥에서는 v1 안 A의 장점(무설치·무료·온디바이스·최속도)을 그대로 얻고 ② 윈도우 이식은 "어댑터 파일 1개(이미 존재) + config 1줄 + 등록 방식"으로 끝나며 ③ 두 엔진을 같은 코어에서 비교할 수 있어 품질 판단도 쉬워진다. 대안 1은 2차 비용이 크고, 대안 2는 맥 품질을 불필요하게 포기한다.

**엔진 기본값**: `apple` (맥). 고유명사 정확도가 부족하면 `whispercpp`로 한 줄 전환.

### 3.1 Windows 이식 체크리스트 (2차 작업, 1~2시간 예상)

| # | 항목 | 변경 내용 | 난이도 |
|---|---|---|---|
| 1 | ASR | `asr.engine = "whispercpp"`, `whisper_cli` 경로 | ★ |
| 2 | ffmpeg | `ffmpeg_path` config 값 | ★ |
| 3 | 인코딩 | `PYTHONUTF8=1`, 콘솔 cp949 대응 (`chcp 65001`) | ★ |
| 4 | 인코딩(파일명) | 맥의 NFD 문제는 사라지지만 **경로 길이/공백·OneDrive 폴더 회피** 확인 | ★ |
| 5 | 감지 실행 | `launchd` → 작업 스케줄러(로그온 시) 또는 NSSM 서비스 | ★★ |
| 6 | 파일 잠금 | Windows Defender/Syncthing가 파일을 잠글 수 있음 → 안정화 대기에서 `open()` 실패 재시도 3회 | ★★ |
| 7 | 알림 | `osascript` → Windows 토스트(선택, 없으면 로그만) | ★ |
| 8 | GPU | NVIDIA 없으면 `large-v3-turbo` → `medium` 다운그레이드 결정 (52분 파일 처리시간) | ★★ |
| 9 | 원본 경로 | Syncthing 폴더 경로만 config 교체 | ★ |

> [!note] 코어에 미리 박아둘 이식 대비 3가지 (1차 구현 시)
> 1. **경로 하드코딩 금지** — `/opt/homebrew/bin/ffmpeg` 같은 절대경로는 전부 `config.toml`
> 2. **플랫폼 분기 최소화** — `sys.platform` 분기는 `config.py` 한 곳에만
> 3. **어댑터 반환 스키마 고정** — `Transcript{segments:[{start,end,text}], lang, engine}`. 엔진이 달라도 코어는 이 스키마만 본다

---

## 4. 그대로 유지되는 부분 (v1 §5~§7 승계)

- **출력**: `result/{키워드}.md`, Obsidian frontmatter + `## 전사` + 선택적 `## 구간`
- **파일명**: 키워드 40자 제한, 금지 문자 치환, NFC 정규화, 중복 시 `-2`, 실패 시 `녹음-YYYYMMDD-HHMM`
- **상태**: `~/syncthing/recoding/{_done,_failed,.recoding/ledger.sqlite,logs}`
- **중복 방지**: `sha1(내용)` 키 → 재동기화·이름변경에도 재처리 방지
- **엣지**: 3초 미만 skip, `.syncthing.*.tmp` 무시, size+mtime 2회 동일 확인, 52분 파일 처리, 무음 환각 제거

---

## 5. 구현 순서 (승인 시)

| 단계 | 작업 | 예상 |
|---|---|---|
| 0 | 경로 확정(`~/syncthing/recoding`), `_done/`·ledger 스키마, `config.toml` | 15분 |
| 1 | **맥 PoC** — Swift `SpeechHelper`로 짧은 파일 1개 한국어 품질 확인 | 1시간 |
| 2 | `core/` (ledger·render·keyword) + `asr_apple` 어댑터 | 2시간 |
| 3 | `asr_whispercpp` 어댑터 + **맥에서 교차 검증**(윈도우 리허설) | 1시간 |
| 4 | `watcher` + 안정화 + launchd 등록 | 1~2시간 |
| 5 | 기존 12개 일괄 실행 + 품질 리뷰(엔진 2종 비교) | 1시간 |
| 6 | 실패 처리·로그 로테이션·README(+`platforms/windows/install.md` 초안) | 40분 |

> [!question] 개발 승인 전 확정 필요 (v1 §10 이월)
> 1. 경로: `~/syncthing/recoding` 확정 여부
> 2. 기본 엔진: `apple`로 시작 OK인지
> 3. 원본 처리: 유지 / `_done/` 이동 / 삭제
> 4. 파일명: `키워드.md` vs `YYYY-MM-DD 키워드.md`
> 5. 본문: 전사문만 / + 타임스탬프 / + 한 줄 요약
> 6. 기존 12개 일괄 처리 여부 (52분 포함)
> 7. 윈도우 착수 시점 — 지금은 `install.md` 초안만 남기고 보류?

---
*다음 단계: 위 7개 확정 후 "개발해줘" 지시 시 착수. 이전 설계: [[design_v1]] · 원 요구사항: [[spec]]*
