---
title: recoding — 음성 녹음 자동 전사 파이프라인 설계안 v1
created: 2026-11-18
status: 설계 (미구현)
tags:
  - project/recoding
  - design
  - asr
  - obsidian-automation
---

# recoding — 음성 녹음 → 텍스트 자동화 설계안 v1

> [!warning] 개정됨 — [[design_v2]]를 보세요
> "맥 우선 개발 + 윈도우 최소변경 이식" 제약이 추가되어 v2에서 권장안이 **안 A 단독 → 하이브리드 어댑터(대안 3)** 로 바뀌었다. 이 문서는 대안·실측 데이터 원본으로만 유지.

> [!abstract] 한 줄 요약
> Syncthing으로 들어오는 산책 녹음(m4a)을 **자동 감지 → 한국어 전사 → 키워드 1개로 파일명 생성 → Obsidian `result/`에 md 저장**하는 로컬 파이프라인. 본 문서는 구현 전 설계안이며, 승인 후에만 코딩한다.


---

## 1. 목표와 범위

| 구분 | 내용 |
|---|---|
| 입력 | 스마트폰 녹음 파일 (`.m4a`, AAC mono) — Syncthing 동기화 |
| 트리거 | 새 파일 도착 시 자동 (수동 실행도 가능해야 함) |
| 처리 | 한국어 음성 → 텍스트, 구간 타임스탬프(선택), 키워드 추출 |
| 출력 | `0.Projects/recoding/result/{키워드}.md` (Obsidian 포맷) |
| 부가 | 처리 이력 관리(중복 방지), 원본 오디오 아카이브 정책 |

**범위 밖(1차)**: 화자 분리(diarization), 실시간 스트리밍 전사, 요약문 자동 생성(2차 후보).

---

## 2. 실측 환경 (설계 근거)

설계 전 현재 머신을 실제로 조사한 결과다. **spec.md의 경로와 실제 경로가 다르다.**

| 항목               | 실측값                                                        | 설계 영향                                           |
| ---------------- | ---------------------------------------------------------- | ----------------------------------------------- |
| 하드웨어             | Apple Silicon arm64, 10 core, 32GB RAM                     | 로컬 추론 충분 (Metal/ANE 활용 가능)                      |
| OS               | macOS 26.6.2 (Tahoe)                                       | **`SpeechAnalyzer` / `FoundationModels` 사용 가능** |
| Syncthing 폴더     | `~/syncthing/recoding` (label: recoding)                   | ⚠️ spec의 `~/recoding` 아님 → 경로 확정 필요             |
| Syncthing 데몬     | 실행 중 (앱: `/Volumes/Syncthing/Syncthing.app`)               | fsWatcher 활성, rescan 3600s                      |
| ffmpeg / ffprobe | `/opt/homebrew/bin` 설치됨                                    | 리샘플링 16kHz mono 즉시 가능                           |
| Python           | 시스템 3.9.6 + pyenv 3.12.3                                   | venv 구성 가능 (`uv`는 미설치)                          |
| Swift            | Swift 6.3.1 (CLT)                                          | 네이티브 단일 바이너리 빌드 가능                              |
| 한국어 STT 지원       | `SpeechTranscriber.supportedLocales`에 **ko-KR 포함 (실측 확인)** | 무설치·무료 한국어 전사 경로 확보                             |
| 클라우드 키           | DeepSeek, OpenRouter (OpenAI 키 없음)                         | ffmpeg+로컬 우선, 클라우드는 옵션                          |

### 2.1 입력 파일 실측 (현재 12개, 총 약 76분)

| 파일 | 길이 | 비고 |
|---|---|---|
| 음성 004.m4a | **52분 01초** | 최장 — 청크/타임아웃 설계 필수 |
| 음성 002.m4a | 14분 51초 | 장시간 |
| 음성 007.m4a | 12분 35초 | |
| 음성 003.m4a | 2분 34초 | |
| 음성 261118_134537.m4a | 2분 42초 | 최근 파일 |
| 음성 261117_180209.m4a | 51초 | |
| 나머지 6개 | 1~44초 | 대부분 짧은 테스트 녹음 |

> [!warning] 파일명 인코딩 주의
> 실제 파일명이 **NFD(분해형) 한글**이다. macOS Finder에서는 정상으로 보이지만 스크립트에서 문자열 비교/키 생성 시 NFC 변환이 필요하다. 파일명을 그대로 `id`로 쓰면 중복 판정이 어긋날 수 있음.

---

## 3. 전체 파이프라인

```mermaid
flowchart LR
    A[스마트폰 녹음] -->|Syncthing| B["~/syncthing/recoding"]
    B --> C{새 파일 감지<br/>launchd WatchPaths}
    C -->|안정화 대기·해시 확인| D[전처리<br/>ffmpeg 16kHz mono]
    D --> E[전사 엔진<br/>ASR]
    E --> F[후처리<br/>문장 다듬기·구간 병합]
    F --> G[키워드 1개 추출]
    G --> H["result/{키워드}.md<br/>Obsidian"]
    D -.원본.-.-> I[아카이브 _done/]
    H --> J[(ledger.sqlite<br/>처리 이력)]
    E --> J
```

### 3.1 단계별 상세

| # | 단계 | 내용 | 실패 시 |
|---|---|---|---|
| 1 | 감지 | launchd `WatchPaths` (또는 폴링 30초) + `*.m4a,*.wav,*.mp3,*.caf` | 로그만 남기고 다음 주기 |
| 2 | 안정화 | `.syncthing.*.tmp` 무시, `size+mtime` 2회 연속 동일 확인 (10초 간격) | 3회 후 보류 큐로 |
| 3 | 중복 체크 | SHA-1 해시 + 원본 파일명 조합으로 ledger 조회 | 처리 완료면 skip |
| 4 | 전처리 | `ffmpeg -i in -ac 1 -ar 16000 -c:a pcm_s16le out.wav` | 손상 파일 → error 로그 |
| 5 | 전사 | ASR 엔진 (아래 §4) — 언어 `ko`, 필요 시 `en` 코드스위칭 | 청크 재시도 2회 |
| 6 | 정리 | 무음/환각 제거(반복 문장, "감사합니다" 단독 등), 문단화 | — |
| 7 | 키워드 | 전사문 → 키워드 1개 (§4.3) | 실패 시 `녹음_YYYYMMDD_HHMM` |
| 8 | 저장 | md 렌더 → `result/` (충돌 시 `-2`) | — |
| 9 | 아카이브 | 원본을 `_done/` 이동 (정책 옵션: 유지/삭제) | — |
| 10 | 이력 | ledger에 duration, model, 처리시간, 상태 기록 | — |

---

## 4. 기술 스택: 대안 3개

### 4.1 ASR 엔진 선택지

| 엔진 | 설치 | 한국어 정확도 | 속도(52분 파일) | 비용 | 비고 |
|---|---|---|---|---|---|
| **A. Apple `SpeechAnalyzer`/`SpeechTranscriber`** | 없음 (Swift 빌드) | 중~상 (온디바이스) | 매우 빠름 (실시간 대비 수 배) | 무료 | macOS 26+, ko-KR 지원 실측 확인. 고유명사·전문용어 약함 |
| **B. whisper.cpp (large-v3-turbo)** | `brew install whisper-cpp` (~1.6GB 모델) | 상 | 빠름 (Metal, 예상 5~10분) | 무료 | 환각(hallucination) 간혹, 무음 구간 주의 |
| **C. mlx-whisper (large-v3-turbo)** | pyenv 3.12 venv + pip (~1.5GB) | 상 | 가장 빠름 (MLX 최적화) | 무료 | Python 생태계 통합 쉬움, MLX 의존 |
| D. 클라우드 API (OpenAI/Groq Whisper) | 키 필요 (현재 없음) | 최상 | 업로드 시간 의존 | 유료 (Groq 저렴) | 프라이버시 이슈, 오프라인 불가 |

---

### 🅰️ 안 A — 완전 네이티브 (Swift 단일 바이너리)

| 구성 요소 | 기술 | 장점 | 단점 |
|---|---|---|---|
| 감지 | launchd `WatchPaths` + Swift `DispatchSource` | 의존성 0, 재부팅 후 자동 복구 | 디렉터리 단위 이벤트만, 세밀 폴링은 직접 구현 |
| 전사 | `SpeechAnalyzer` + `SpeechTranscriber` (ko-KR) | 설치·모델 다운로드 없음, 온디바이스(프라이버시), 메모리 적음, 파일 입력 지원 | Apple 모델 품질 한계(고유명사/방언), 언어 자산 최초 다운로드 필요 |
| 키워드 | `FoundationModels` (Apple Intelligence 온디바이스 LLM) | 완전 무료·오프라인, 한국어 프롬프트 가능 | 모델 자산 존재는 확인했으나 한국어 출력 품질·토큰 제한 검증 필요 |
| 오디오 | `AVFoundation` 직접 읽기 | ffmpeg 불필요 | 포맷 다양성 낮음 |
| 산출물 | 단일 실행 파일 + plist | 배포·재현 쉬움, 크래시 격리 | Swift 수정 시 재컴파일 |

**적합**: 설치를 최소화하고 "그냥 돌아가는" 것을 최우선할 때. **총 예상 구현: 반나절~1일.**

---

### 🅱️ 안 B — whisper.cpp + 얇은 스크립트 (Bash/Python)

| 구성 요소 | 기술 | 장점 | 단점 |
|---|---|---|---|
| 감지 | launchd `WatchPaths` → 셸 스크립트 | 단순, 디버깅 쉬움 | 상태 관리를 스크립트로 직접 |
| 전사 | `whisper-cli -m ggml-large-v3-turbo -l ko --output-json` | 정확도 높음, Metal 가속, JSON에 세그먼트/타임스탬프 포함 | 모델 1.6GB 다운로드, brew 의존, 긴 파일은 CPU/GPU 세그먼트 처리 시간 |
| 키워드 | DeepSeek API 호출 (curl) 또는 `ollama`(미설치) | 한국어 키워드 품질 좋음, 비용 극소(파일당 <1원) | 네트워크 필요, API 키 관리 |
| 오디오 | ffmpeg | 포맷 무관 | ffmpeg 경로를 plist에 명시 필요 |
| 상태 | JSON ledger 파일 | 단순 | 동시성 처리 직접 |

**적합**: 정확도 우선 + 로직을 짧은 스크립트로 유지하고 싶을 때. **예상 구현: 3~4시간.**

---

### 🅲 안 C — Python 파이프라인 (mlx-whisper + watchdog)

| 구성 요소 | 기술 | 장점 | 단점 |
|---|---|---|---|
| 감지 | `watchdog` 상주 프로세스 / launchd KeepAlive | 코드 내 이벤트 처리, 확장 쉬움 | 상주 프로세스 관리(로그 로테이션 등) |
| 전사 | `mlx-whisper` (large-v3-turbo, `word_timestamps`) | Apple Silicon 최고 속도, 정확도 상, 배치 API 간단 | 가상환경·패키지 관리, MLX 버전 종속 |
| 키워드 | OpenRouter (예: 저가 모델) 또는 DeepSeek | 모델 교체 자유, 요약까지 확장 | 외부 의존, 키 필요 |
| 오디오 | ffmpeg-python | 표준 | — |
| 상태 | SQLite | 쿼리·재처리 편함 | 스키마 관리 |
| 확장 | 요약·태그·화자분리(pyannote) 로드맵 | 장기 확장성 최고 | 1차 구현 복잡도 최대 |

**적합**: 앞으로 요약·태그·화자분리까지 붙일 계획이면 유리. **예상 구현: 1일.**

---

### 4.3 키워드 1개 생성 방식 비교

| 방식 | 예시 결과 | 장점 | 단점 |
|---|---|---|---|
| 온디바이스 LLM (FoundationModels) | `산책단상` | 무료·즉시·프라이버시 | 품질 검증 필요 |
| 클라우드 LLM (DeepSeek/OpenRouter) | `아파트재건축` | 문맥 이해·한국어 자연스러움 | 네트워크, 비용(무시 가능) |
| TF-IDF/빈도 휴리스틱 | `산책` | 의존성 없음 | "산책"처럼 무의미한 단어가 뽑히기 쉬움 |
| Whisper 자체 title(JSON) | `일상 대화` | 구현 난이도 최저 | 한국어 파일명 품질 낮음 |

> [!tip] 권장 조합
> ASR은 **로컬**(안 A 또는 B), 키워드는 **LLM 1회 호출**(클라우드 또는 온디바이스)로 분리. 전사 실패가 파일명 생성을 막지 않도록 **항상 날짜 기반 fallback**을 둔다.

---

## 5. 출력 포맷 (Obsidian)

### 5.1 파일명 규칙

- 형식: `{키워드}.md` (기본) — 옵션 `YYYY-MM-DD {키워드}.md`
- 한글 허용, 공백 → `-` 또는 제거, 금지 문자 `/ \ : * ? " < > |` 치환
- 길이 40자 제한, NFC 정규화, 중복 시 `-2`, `-3`
- 전사 실패·무음: `녹음-20261118-1345.md`

### 5.2 md 템플릿

```markdown
---
title: 산책 단상
source: 음성 261118_134537.m4a
recorded: 2026-11-18T13:45:37
duration: 00:02:42
transcribed: 2026-11-18T17:30:02
engine: apple-SpeechTranscriber/ko-KR
lang: ko
tags:
  - recoding
  - 산책
---

# 산책 단상

> [!quote] 핵심 한 줄
> (전사문에서 추출한 대표 문장)

## 전사

(본문 문단)

## 구간 (선택)

- 00:00 오늘은 아파트 단지 쪽으로 걸었다
- 01:12 요즘 생각한 것들
```

- Obsidian 규칙: YAML frontmatter는 문서 최상단, `tags`는 리스트 형태, 콜아웃/구간 목록은 그대로 렌더됨
- 원본 JSON(세그먼트 전체)은 `result/_raw/{slug}.json`에 보관 → 나중에 재가공 가능

---

## 6. 상태 관리 · 중복 방지

```
~/syncthing/recoding/
├── 음성 261118_134537.m4a      # 신규
├── _done/                       # 처리 완료 원본 (정책: keep)
├── _failed/                     # 손상/전사 실패
└── .recoding/
    ├── ledger.sqlite            # id, sha1, size, path, status, engine, dur, ms, error
    └── logs/recoding-YYYYMM.log
```

- **키**: `sha1(파일 내용)` → 같은 파일 재동기화/이름변경에도 중복 처리 방지
- **상태**: `pending → transcribing → done | failed` (크래시 복구용)
- Syncthing `.stfolder`, `.syncthing.*.tmp`, `.DS_Store` 무시

---

## 7. 엣지 케이스 · 리스크

| 리스크 | 대응 |
|---|---|
| 동기화 중 부분 파일 전사 | 안정화 대기(size/mtime 2회 동일) + `.tmp` 무시 |
| 무음/1초 파일 | 3초 미만 skip, ledger에 `skipped` |
| 긴 파일(52분) 타임아웃 | native: 스트리밍 처리 / whisper: 10분 청크 + 오프셋 보정 |
| Whisper 환각(무음 구간 반복) | `--no-context`, 반복 문장 제거, VAD(`--vad`) 사용 |
| 한/영 코드스위칭 | `language=ko` 고정 후 영문 구간 후처리, 또는 auto 감지 |
| NFD 한글 파일명 | NFC 변환 후 slug 생성 |
| 키워드 중복 | ledger에서 최근 사용 키워드 조회 → suffix |
| launchd 환경 PATH 없음 | 절대경로 사용(`/opt/homebrew/bin/ffmpeg`) |
| 개인정보(대화 녹음) | 기본 완전 로컬, 클라우드 사용 시 명시적 옵션 플래그 |

---

## 8. 권장안

> [!success] 권장: **안 A (네이티브) 로 시작 → 필요 시 안 B/C 확장**
> 근거: ① ko-KR 지원 실측 확인으로 무설치 경로가 실제 동작 ② 52분 녹음도 로컬에서 수 분 내 처리 ③ 개인 대화가 외부로 나가지 않음 ④ launchd 등록만으로 상시 자동화 완성. 단, 고유명사 정확도가 부족하면 안 B/whisper로 엔진만 교체.

**단계적 로드맵**

1. **Phase 1 (MVP)** — 감지 + 전사 + 키워드 + md 저장 + ledger. 기존 12개 일괄 처리로 품질 확인
2. **Phase 2** — 무음/환각 정리, 구간 타임스탬프, 요약 콜아웃
3. **Phase 3** — 태그 자동 분류, 월간 인덱스 노트(`result/_index.md`), 주간 다이제스트

---

## 9. 구현 순서 (개발 승인 시)

| 단계 | 작업 | 예상 |
|---|---|---|
| 0 | 경로 확정(`~/syncthing/recoding`), `_done/`·ledger 스키마 생성 | 10분 |
| 1 | ASR 단일 파일 PoC — 짧은 파일 1개로 한국어 품질 확인 | 30분 |
| 2 | 전사→md 렌더 + 키워드 생성 | 1~2시간 |
| 3 | 감지(launchd) + 중복/안정화 로직 | 1~2시간 |
| 4 | 기존 12개 일괄 실행 + 품질 리뷰 | 1시간 |
| 5 | 실패 처리·로그·README | 30분 |

---

## 10. 결정 필요 사항

1. **경로**: `~/recoding`(spec) vs `~/syncthing/recoding`(실제) — 실제 쪽으로 확정해도 되는지
2. **엔진**: 안 A(무설치 네이티브) / 안 B(whisper.cpp) / 안 C(mlx-whisper) 중 선택
3. **원본 처리**: ① 유지 ② `_done/` 이동 ③ 전사 후 삭제
4. **파일명**: `키워드.md` 만 / `YYYY-MM-DD 키워드.md`
5. **본문 구성**: 전사문만 / + 타임스탬프 / + 한 줄 요약
6. **기존 12개**: 일괄 처리 여부 (52분 파일 포함)

---
*다음 단계: 위 6개 항목 확정 후 "개발해줘" 지시 시 착수. 관련 노트: [[spec]]*
