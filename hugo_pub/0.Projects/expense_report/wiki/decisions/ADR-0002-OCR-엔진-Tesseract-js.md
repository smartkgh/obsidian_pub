---
type: decision
title: ADR-0002 OCR 엔진 — Tesseract.js (교체 가능 구조)
status: accepted  # 맥에서는 ADR-0003으로 대체
version: v1
tags: [OCR, Tesseract.js]
sources: [raw/research/2026-11-25-web-search-ocr-docx.md]
related: [[ocr-options]], [[ADR-0001-앱-형태-PWA-USB-설치]], [[system]]
created: 2026-11-25
updated: 2026-11-25
---

# ADR-0002 OCR 엔진 — Tesseract.js (교체 가능 구조)

> 2026-11-25: TEST-04 실패로 **맥에서는 [[ADR-0003-맥-OCR-Apple-Vision-로컬-도우미]]로 대체**. 폰과 도우미가 없을 때의 대체 엔진으로는 계속 사용.

## 배경
ADR-0001로 앱이 브라우저(PWA)에서 돈다. ML Kit, Apple Vision은 네이티브 앱에서만 쓸 수 있다.

## 선택지
| 선택지 | 장점 | 단점 |
|---|---|---|
| **Tesseract.js (kor+eng)** | 브라우저에서 오프라인 동작, 폰·맥 공통 | 사진 인식 정확도가 네이티브보다 낮음, 언어 파일 수 MB |
| 브라우저 내장 인식 API | 추가 파일 없음 | 표준화되지 않아 안드로이드 크롬에서 사용 불가 |

## 결정
**Tesseract.js**를 쓰고, 엔진 파일(worker, core wasm, `kor`/`eng` 언어 데이터)을 모두 앱에 포함해 오프라인으로 동작시킨다.
인식 엔진은 `OcrEngine` 인터페이스 뒤에 두어 나중에 교체할 수 있게 한다.

## 이유
- 필요한 값이 숫자(일자, 금액)와 몇 개의 키워드라서 Tesseract.js로도 충분할 가능성이 높다.
- 인식 실패 시 빈칸 + 사용자 수정 흐름(REQ-004)이 있어 정확도 부담이 줄어든다.

## 영향
- 정확도를 높이기 위해 인식 전에 이미지 전처리(크기 조정, 흑백, 대비)를 한다.
- 검증 단계에서 실제 카드 영수증으로 인식률을 측정한다. 목표에 못 미치면 v2에서 APK + ML Kit 전환을 검토한다.
- 관련 요구사항: REQ-002, REQ-003, REQ-014

## 근거
- [[ocr-options]]
