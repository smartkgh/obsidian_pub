---
type: module
title: ocr — 영수증 인식
tags: [모듈, OCR]
related:
  - "[[ADR-0002-OCR-엔진-Tesseract-js]]"
  - "[[ADR-0003-맥-OCR-Apple-Vision-로컬-도우미]]"
  - "[[card-receipt-parsing]]"
  - "[[system]]"
created: 2026-11-25
updated: 2026-11-25
---

# ocr — 영수증 인식

## 역할
영수증 사진에서 기기 안(맥은 로컬 도우미)에서 글자를 읽은 뒤, 승인일자와 금액을 뽑는다. 확신이 없으면 빈칸.

## 엔진 선택
| 상황 | 엔진 | 품질 |
|---|---|---|
| 맥에서 `npm run serve` 실행 중 (폰도 USB 연결 중이면 해당) | **Apple Vision 도우미** — `localhost:8080/api/ocr` | 실제 영수증 2/2 |
| 그 외 (서버 없이 설치된 앱, 케이블 뺀 폰) | Tesseract.js (기본 인식) | 실제 영수증 0/2 — 직접 입력 위주 |
시작 시 `/api/ocr/health`로 확인(1.5초 제한). 도우미가 실패하면 기본 엔진으로 다시 시도.

## 코드 위치
- `~/my_projects/expense-report/src/ocr/image.ts` — 저장용 축소, 인식용 흑백·대비
- `~/my_projects/expense-report/src/ocr/engine.ts` — `OcrEngine`, `pickEngine()`, Apple Vision(로컬 서버 호출), Tesseract.js(kor+eng, 로컬 파일)
- `~/my_projects/expense-report/native/mac/VisionOCR.swift` — Apple Vision 도우미. 글자 칸을 세로 위치로 같은 줄끼리 묶어 출력
- `~/my_projects/expense-report/server/ocr-middleware.ts` — 로컬 서버 `/api/ocr` (localhost 요청만, 임시 파일 즉시 삭제)
- `~/my_projects/expense-report/scripts/build-mac-ocr.mjs` — `swiftc`로 `bin/vision-ocr` 컴파일 (소스 바뀔 때만)
- `~/my_projects/expense-report/src/ocr/parser.ts` — 일자·금액 추출 규칙
- `~/my_projects/expense-report/src/ocr/index.ts` — `analyzeReceipt()`

## 금액 추출 순서
1. 정확한 키워드 (승인금액 → 결제금액 → … → 합계 → 금액). 공급가·부가세·할인 줄 제외
2. 줄이 '합' 또는 '총'으로 시작 (OCR이 키워드 일부를 잘못 읽은 경우)
3. 품목 금액 합과 같은 금액 (검산)
4. 모두 아니면 빈칸

## 키워드 (TEST-04에서 추가)
- 일자: `구매`, `구매일시` / 금액: `카드결제액`, `결제액`
- 날짜와 시간이 붙어 나오면 띄움: `2026-11-1171:49` → `2026-11-11 71:49`

## 일자 추출 순서
1. 키워드(승인일시 등) 줄 또는 다음 줄의 날짜
2. 영수증 전체에서 첫 번째 유효한 날짜 (미래, 2년 넘게 지난 날짜 제외)

## 오프라인
- worker, core(LSTM 3종), 언어 데이터는 `public/`에 복사되어 서비스 워커가 미리 저장한다.
- worker는 Blob URL을 쓰지 않는다(`workerBlobURL: false`) — 서비스 워커가 요청을 처리하도록.

## 관련 요구사항 / 결정
- REQ-002, REQ-003, REQ-004, REQ-014
- [[ADR-0002-OCR-엔진-Tesseract-js]]

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현. 점검 중 "합 A" 오인식 대응 규칙(2, 3번) 추가 |
| v1 | TEST-04 실패 → 맥 Apple Vision 도우미 추가, 엔진 자동 선택, 키워드 보완 (ADR-0003) |
