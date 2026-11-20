---
title: recoding — Windows 이식 가이드 (초안, 2차 작업)
created: 2026-11-20
status: 초안 · 미검증
tags:
  - project/recoding
  - windows
  - porting
---

# Windows 이식 — 최소 변경 가이드

> [!abstract] 전제
> 1차는 macOS(Apple `SpeechTranscriber`)로 완성됐다. 코어(`core/`)와 어댑터 경계(`adapters/base.py`)는
> 플랫폼 의존이 없으므로, **윈도우에서 바뀌는 것은 아래 8개 항목뿐**이다. `core/` 코드는 수정하지 않는다.

---

## 1. 준비물

| 항목 | 내용 |
|---|---|
| Python | 3.11 이상 (3.12 권장). 설치 시 **"Add python.exe to PATH"** 체크 |
| ffmpeg | https://www.gyan.dev/ffmpeg/builds/ (release-full) → `C:\tools\ffmpeg\bin` 에 압축 해제 |
| whisper-cli | whisper.cpp 릴리스 바이너리 `whisper-cli.exe` (CUDA 빌드 권장) |
| 모델 | `ggml-large-v3-turbo.bin` (~1.6GB) — GPU 없으면 `ggml-medium.bin` 으로 낮춤 |
| 프로젝트 | 이 폴더 전체 복사 (`0.Projects\recoding`) |

```powershell
# 디렉터리 예시
C:\recoding\                 # 이 프로젝트 복사본
C:\tools\ffmpeg\bin\ffmpeg.exe
C:\tools\whisper\whisper-cli.exe
C:\models\ggml-large-v3-turbo.bin
```

---

## 2. 필수 변경 (config.toml)

TOML 에서 Windows 경로는 **백슬래시를 두 번** 쓰거나 슬래시를 쓴다.

```toml
[paths]
incoming = "C:/Users/<사용자>/Syncthing/recoding"
output   = "C:/recoding/result"
state    = "C:/Users/<사용자>/Syncthing/recoding/.recoding"

[asr]
engine = "whispercpp"            # ← 이것만 바꾸면 엔진 교체 완료

[asr.whispercpp]
binary = "C:/tools/whisper/whisper-cli.exe"
model  = "C:/models/ggml-large-v3-turbo.bin"
extra_args = ["-np", "--no-context"]

[audio]
ffmpeg  = "C:/tools/ffmpeg/bin/ffmpeg.exe"
ffprobe = "C:/tools/ffmpeg/bin/ffprobe.exe"

[archive]
done_dir   = "C:/recoding_archive/done"       # Syncthing 폴더 밖!
failed_dir = "C:/recoding_archive/failed"
```

> [!warning] `engine = "apple"` 은 macOS 전용
> `adapters/__init__.py` 가 `sys.platform != "darwin"` 일 때 명확한 에러를 낸다.

---

## 3. 인코딩 (한글 깨짐 방지)

```powershell
setx PYTHONUTF8 1                      # 시스템 환경변수로 등록 (재로그인 필요)
chcp 65001                             # 현재 콘솔만 UTF-8
```

- `config.toml`, `main.py` 는 UTF-8 로 저장되어 있어야 한다 (BOM 없이).
- 레거시 cp949 콘솔에서 로그의 한글이 깨지면 위 두 줄로 해결.

---

## 4. 검증 순서

```powershell
cd C:\recoding
python -m venv .venv
.venv\Scripts\python main.py doctor
.venv\Scripts\python main.py file "음성 006.m4a"
.venv\Scripts\python main.py list
```

- `doctor` 에서 `asr engine : whispercpp(...)` OK, ffmpeg/ffprobe 경로 OK 확인
- 첫 실행에서 모델 로딩 때문에 수십 초 걸릴 수 있다

---

## 5. 자동 실행 (작업 스케줄러)

macOS `launchd WatchPaths` 대응 = **작업 스케줄러 + 1분 간격 폴링**이 가장 단순하고 견고하다.

```powershell
# 1분마다 once 실행 (로그온 상태에서)
schtasks /Create /TN "recoding" /SC MINUTE /MO 1 /F ^
  /TR "\"C:\recoding\.venv\Scripts\pythonw.exe\" \"C:\recoding\main.py\" once"

schtasks /Run    /TN "recoding"        # 즉시 1회
schtasks /Query  /TN "recoding" /V /FO LIST
schtasks /Delete /TN "recoding" /F     # 해제
```

대안:
- **NSSM** 으로 `python main.py watch` 를 서비스 등록 (상주형, 즉시 반응)
- 시작프로그램 폴더에 `.bat` 등록 (가장 간단하지만 로그온 필요)

> [!tip] `pythonw.exe` 를 쓰면 콘솔 창이 뜨지 않는다. 로그는 `.recoding/logs` 에 남는다.

---

## 6. 윈도우 특유의 함정

| 함정 | 대응 |
|---|---|
| Syncthing / Defender 가 파일을 잠금 | `settle_seconds` 를 20~30초로 올린다. `open()` 실패는 다음 스캔에서 재시도됨 |
| 경로 260자 제한 | 프로젝트를 `C:\recoding` 처럼 짧은 경로에 둔다 |
| OneDrive 동기화 폴더 | 수신/출력 폴더를 OneDrive 안에 두지 않는다(잠금·지연) |
| `_done` 을 Syncthing 폴더 안에 둠 | 폰으로 재동기화된다. 반드시 폴더 밖(`C:\recoding_archive`) |
| GPU 없음 | 52분 파일이 수십 분 걸릴 수 있다 → `ggml-medium.bin` 또는 `-t` 스레드 조정 |
| whisper 환각 | `extra_args` 에 `--no-context`, 필요 시 `--vad` 추가 |
| 파일명 NFD 문제 | 윈도우는 NFC 를 쓰므로 해당 없음 (코드는 NFC 정규화만 수행) |

---

## 7. 코어가 건드리지 않는 것 (확인용)

| 파일 | 윈도우에서 수정? |
|---|---|
| `core/*.py` | ❌ 없음 |
| `adapters/base.py` | ❌ 없음 |
| `adapters/asr_whispercpp.py` | ❌ 없음 (1차에 이미 작성·검증) |
| `adapters/asr_apple.py` | 사용 안 함 |
| `config.toml` | ✅ 경로·엔진 값만 |
| 실행 등록 | ✅ 작업 스케줄러 (plist 대체) |

---

## 8. 2차 작업 체크리스트

- [ ] Python 3.11+ 설치, `PYTHONUTF8=1`
- [ ] ffmpeg / whisper-cli / 모델 배치
- [ ] `config.toml` 4개 섹션 수정 (paths, asr, audio, archive)
- [ ] `main.py doctor` 통과
- [ ] 짧은 파일 1개 전사 확인 (`engine=whisper.cpp` 로 기록되는지)
- [ ] 띄어쓰기 품질 확인 → 필요하면 `[postprocess].spacing_fix` 유지
- [ ] 작업 스케줄러 등록 + 신규 파일 자동 처리 확인
- [ ] 52분 파일 처리 시간 측정 (모델/스레드 결정)
