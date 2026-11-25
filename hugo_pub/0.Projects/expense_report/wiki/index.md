---
type: index
title: Index
updated: 2026-11-25
---

# Index

위키 전체 목차. 에이전트는 작업 전에 이 파일을 먼저 읽는다. 페이지를 만들거나 지우면 여기를 갱신한다.

- [[overview]] — 프로젝트 요약
- [[log]] — 작업 기록

## Versions
| 버전 | 상태 | 요약 |
|---|---|---|
| [[versions/v1/requirements\|v1]] · [[versions/v1/plan\|plan]] · [[versions/v1/test-plan\|test]] · [[versions/v1/tasks\|tasks]] | ④ 검증 중 — 맥 TEST-04 통과(Apple Vision), 폰·수동 항목 남음 | 영수증 인식 → 지출결의서 DOCX/PDF, 안드로이드·맥북 로컬 전용 |

## Research
- [[ocr-options]] — 오프라인 영수증 OCR 선택지 (ML Kit, Apple Vision, Tesseract.js)
- [[card-receipt-parsing]] — 카드 영수증에서 일자·금액 뽑는 규칙
- [[document-generation]] — 오프라인 DOCX·PDF 생성, 한글 폰트
- [[local-app-packaging]] — 안드로이드·맥북 로컬 앱 형태 (PWA, Capacitor, 네이티브)

## Concepts

## Architecture
- [[system]] — 시스템 구조, 모듈, 데이터 구조
- [[form-layout]] — 결의서 레이아웃 (14줄, 증빙 6장/쪽)
- [[install-guide]] — 맥북, 안드로이드 USB 설치 안내
- `architecture/ui-mockup.html` — 화면 시안

## Decisions
- [[ADR-0001-앱-형태-PWA-USB-설치]] — 웹앱(PWA) + USB 설치
- [[ADR-0002-OCR-엔진-Tesseract-js]] — Tesseract.js, 교체 가능 구조 (맥은 ADR-0003으로 대체)
- [[ADR-0003-맥-OCR-Apple-Vision-로컬-도우미]] — 맥 OCR을 Apple Vision 로컬 도우미로

## Modules
- [[store]] — 결의서 데이터, 합계, 14줄 제한
- [[storage]] — 기기 안 저장 (IndexedDB)
- [[ocr]] — 영수증 인식 (Tesseract.js, 파서)
- [[layout]] — 결의서 레이아웃 정의
- [[export]] — PDF·DOCX 출력
- [[ui]] — 화면

## Queries
