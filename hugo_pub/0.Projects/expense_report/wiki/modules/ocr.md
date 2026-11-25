---
type: module
title: ocr — 영수증 인식
tags: [모듈, OCR]
related: [[ADR-0002-OCR-엔진-Tesseract-js]], [[card-receipt-parsing]], [[system]]
created: 2026-11-25
updated: 2026-11-25
---

# ocr — 영수증 인식

## 역할
영수증 사진을 전처리하고, 기기 안에서 글자를 읽은 뒤, 승인일자와 금액을 뽑는다. 확신이 없으면 빈칸.

## 코드 위치
- `~/my_projects/expense-report/src/ocr/image.ts` — 저장용 축소, 인식용 흑백·대비
- `~/my_projects/expense-report/src/ocr/engine.ts` — `OcrEngine` 인터페이스, Tesseract.js(kor+eng, 로컬 파일)
- `~/my_projects/expense-report/src/ocr/parser.ts` — 일자·금액 추출 규칙
- `~/my_projects/expense-report/src/ocr/index.ts` — `analyzeReceipt()`

## 금액 추출 순서
1. 정확한 키워드 (승인금액 → 결제금액 → … → 합계 → 금액). 공급가·부가세·할인 줄 제외
2. 줄이 '합' 또는 '총'으로 시작 (OCR이 키워드 일부를 잘못 읽은 경우)
3. 품목 금액 합과 같은 금액 (검산)
4. 모두 아니면 빈칸

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
