---
type: decision
title: ADR-0003 맥 OCR — Apple Vision 로컬 도우미
status: accepted
version: v1
tags: [OCR, Apple Vision, macOS]
sources: [raw/test-logs/2026-11-25-v1-TEST-04.log]
related: [[ADR-0002-OCR-엔진-Tesseract-js]], [[verification]], [[system]], [[ocr]]
created: 2026-11-25
updated: 2026-11-25
---

# ADR-0003 맥 OCR — Apple Vision 로컬 도우미

## 배경
TEST-04에서 Tesseract.js가 실제 카드 영수증 2장의 일자·금액을 하나도 맞히지 못했다(0/2, 0/2). 전처리 20여 조합도 불안정했다.
같은 사진을 macOS 내장 Apple Vision으로 읽으면 일자·금액 줄을 정확히 읽었다. ([[verification]])

## 선택지
| 선택지 | 장점 | 단점 |
|---|---|---|
| A. 맥 Apple Vision + 폰 APK(ML Kit) | 두 기기 모두 정확 | 폰 설치 방식 변경, Android Studio 필요 |
| **B. 맥만 Apple Vision, 폰은 당분간 Tesseract.js** | 맥은 바로 개선, 작업량 작음 | 폰 자동 인식 문제는 남음 |
| C. 그대로 | 작업 없음 | 자동 인식 거의 안 됨 |

## 결정
**B.** (사용자 결정, 2026-11-25)
- 맥에서는 Apple Vision을 쓰는 작은 Swift 프로그램(로컬 도우미)을 만들고, `npm run serve`가 띄우는 로컬 서버(`localhost:8080`)에 `/api/ocr` 주소로 연결한다.
- 앱은 시작할 때 도우미가 있는지 확인하고, 있으면 도우미를, 없으면 Tesseract.js를 쓴다. (`OcrEngine` 교체 구조 — ADR-0002)
- 도우미는 글자 칸들을 위치(좌표)로 같은 줄끼리 다시 묶어서, 기존 파서가 그대로 쓸 수 있는 줄 단위 텍스트를 돌려준다.

## 이유
- 사진과 결과가 맥 밖으로 나가지 않는다. (`localhost` 안에서만 오감, REQ-014 유지)
- 화면, 문서 생성, 파서는 그대로 두고 인식 엔진만 바꾼다.

## 영향
- 맥: `npm run serve` 실행 중일 때만 도우미 사용. 서버 없이 설치된 앱만 열면 Tesseract.js로 동작
- 폰: USB 연결로 `npm run phone` 실행 중에는 맥 도우미를 쓸 수 있지만, 케이블을 뺀 뒤에는 Tesseract.js (자동 인식 품질 낮음, 직접 입력 위주)
- 파서 보완: 일자 키워드 `구매`, 금액 키워드 `카드결제액`, 날짜와 시간이 붙어 나오는 경우(`2026-11-1171:49`)
- 폰 개선(APK + ML Kit)은 다음 단계 후보로 남긴다
- 관련 요구사항: REQ-002, REQ-003, REQ-014, REQ-016

## 근거
- `raw/test-logs/2026-11-25-v1-TEST-04.log`
