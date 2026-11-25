# 웹 검색 기록: 오프라인 OCR, DOCX 생성 (2026-11-25)

수집: 에이전트 웹 검색 (요약 결과). 원문 전체가 아니라 검색 결과 요약과 출처 URL이다.

## 1. Google ML Kit Text Recognition v2 — 한국어 (Android)
- 번들 모델 의존성: `com.google.mlkit:text-recognition-korean:16.0.1`
  (Play 서비스 방식: `play-services-mlkit-text-recognition-korean:16.0.1` — 모델을 동적으로 다운로드)
- 번들 방식은 빌드 시 모델이 앱에 포함되어 바로 사용 가능. 처리는 기기 안에서 하며 오프라인 동작.
- 크기: 스크립트당 아키텍처별 약 4MB 증가.
- 한국어 모듈 16.0.1 릴리스: 2024-08-07. (최신 버전은 릴리스 노트에서 확인 필요)
- 출처:
  - https://developers.google.com/ml-kit/vision/text-recognition/v2/android?hl=ko
  - https://developers.google.com/ml-kit/vision/text-recognition/v2?hl=ko
  - https://developers.google.com/ml-kit/release-notes?hl=ko

## 2. Apple Vision VNRecognizeTextRequest — 한국어 (macOS)
- Revision 1은 영어만 지원. 초기 Revision 2 목록에는 한국어 없음.
- 최신 OS에서는 한국어 지원 보고 있음 (iOS 18.1 포럼 보고, macOS Tahoe 26 기준 OCRmyPDF-AppleOCR 표에 kor 포함).
- OS/리비전별 공식 지원표는 찾지 못함 → `supportedRecognitionLanguages`로 실행 중 확인 권장.
- `recognitionLanguages = ["ko-KR", "en-US"]` 지정 방식.
- 출처:
  - https://developer.apple.com/documentation/vision/recognizetextrequest/supportedrecognitionlanguages.md
  - https://developer.apple.com/forums/thread/121048
  - https://developer.apple.com/forums/thread/684807
  - https://github.com/mkyt/OCRmyPDF-AppleOCR

## 3. Tesseract.js — 오프라인 사용
- `createWorker`에 `workerPath`, `langPath`, `corePath`를 로컬 경로로 지정하면 모든 파일을 로컬에서 제공 가능.
- 언어 파일: `langPath + langCode + '.traineddata.gz'` (한국어: `kor.traineddata.gz`), tessdata 저장소에서 받음.
- `corePath`는 core 파일 4개가 있는 폴더를 가리켜야 함.
- 경로 설정이 빠지면 오프라인에서 "Failed to fetch" 오류 보고 사례 있음.
- 출처:
  - https://unpkg.com/tesseract.js@6.0.1/docs/local-installation.md
  - https://github.com/naptha/tessdata
  - https://github.com/naptha/tesseract.js/issues/155

## 4. docx (npm) — 브라우저에서 DOCX 생성
- Node.js와 브라우저 모두 동작. 브라우저에서는 `Packer.toBlob(doc)`으로 Blob 생성 후 다운로드.
- 현재 문서는 9.x 기준.
- 출처:
  - https://docx.js.org/api/classes/Packer.html
  - https://tessl.io/registry/tessl/npm-docx/files/docs/document-export.md
