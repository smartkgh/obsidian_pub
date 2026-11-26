---
type: plan
title: v1 계획
status: done
version: v1
tags: []
related:
  - "[[requirements]]"
  - "[[system]]"
  - "[[form-layout]]"
  - "[[install-guide]]"
  - "[[ADR-0001-앱-형태-PWA-USB-설치]]"
  - "[[ADR-0002-OCR-엔진-Tesseract-js]]"
created: 2026-11-25
updated: 2026-11-26
---

# v1 계획

## 개요
TypeScript 웹앱(PWA)으로 만든다. 폰에는 USB(adb reverse)로 설치하고, 맥은 `localhost:8080`에서 쓴다.
영수증은 Tesseract.js로 기기 안에서 읽고, 결의서는 공통 레이아웃 정의로 PDF와 DOCX를 만든다.

## 설계
- 구조: [[system]]
- 결의서 레이아웃: [[form-layout]] (14줄, 증빙 6장/쪽)
- 화면: `architecture/ui-mockup.html`
- 설치: [[install-guide]]
- 결정: [[ADR-0001-앱-형태-PWA-USB-설치]], [[ADR-0002-OCR-엔진-Tesseract-js]]

## 요구사항별 구현 방안

| REQ | 구현 방안 | 모듈 |
|---|---|---|
| REQ-001 | `<input type="file" accept="image/*" multiple>` — 안드로이드에서 카메라/사진첩 선택 창이 뜸 | ui |
| REQ-002 | 전처리 → Tesseract.js → 파서가 승인일시 키워드 근처 날짜 추출 ([[card-receipt-parsing]]) | ocr |
| REQ-003 | 파서가 승인금액/합계 키워드 근처 금액 추출, 확신 낮으면 null | ocr |
| REQ-004 | ② 화면에서 모든 값 수정 가능, 영수증 확대 보기, 인식 결과 색 표시 | ui |
| REQ-005 | 선택 상자: 야유회비, 교사 월례회의, 선택 안 함(null) | ui, store |
| REQ-006 | 적요, 비고 입력란 | ui |
| REQ-007 | "직접 입력" 버튼 → 영수증 없는 줄 | ui, store |
| REQ-008 | null 제외 합계, `49,700원` 형식 | store |
| REQ-009 | ① 화면 기본 정보 입력, 다음 결의서에도 유지 | ui, storage |
| REQ-010 | store에서 14줄 초과 추가 차단 + 안내 | store, ui |
| REQ-011 | docx로 1쪽 표 + 2쪽부터 증빙 | export, layout |
| REQ-012 | pdf-lib + 나눔고딕 내장, 같은 레이아웃 정의 사용 | export, layout |
| REQ-013 | 2쪽부터 6장/쪽, 캡션 표시, 사진 축소 | export |
| REQ-014 | 모든 파일을 앱에 포함, 외부 요청 없음, 서비스 워커 사전 캐시 | 전체 |
| REQ-015 | 폰 크롬 + USB 설치 ([[install-guide]]) | 배포 |
| REQ-016 | 맥 크롬 `localhost:8080` | 배포 |
| REQ-017 | IndexedDB 자동 저장, `navigator.storage.persist()` | storage |

## 개발 순서 (③ 개발 단계에서 tasks.md로 세분화)
1. 프로젝트 골격 (Vite, TS, PWA, 테스트 도구)
2. 데이터 구조 + 합계 + 줄 수 제한 + 저장
3. 화면 3개 (시안 기준)
4. 레이아웃 정의 + PDF 출력 → 원본과 비교하며 조정
5. DOCX 출력
6. 영수증 증빙 페이지
7. OCR 전처리 + 엔진 + 파서
8. 오프라인(서비스 워커), 폰 USB 설치 스크립트

## 위험 요소

| 위험 | 영향 | 대응 |
|---|---|---|
| Tesseract.js 인식률이 낮음 | 자동 입력이 자주 빈칸 | 전처리 조정, 파서 보정. 부족하면 v2에서 APK + ML Kit 검토 |
| 실제 영수증 샘플 없음 | 파서 규칙 검증 부족 | 사용자에게 샘플 3~5장 요청, 없으면 직접 만든 텍스트로 단위 테스트 |
| 앱 크기 (언어 데이터 + 폰트 약 15MB) | 첫 설치가 느림 | USB 설치라 영향 작음. 폰트 서브셋 검토 |
| 폰에서 OCR 속도 | 영수증당 수 초 | 진행 표시, 한 장씩 순차 처리 |
| DOCX를 한컴오피스에서 열 때 모양 차이 | 출력 모양 어긋남 | PDF를 기준 출력물로 안내 |
| 크롬 데이터 삭제 시 앱·데이터 손실 | 작성 중 결의서 손실 | 영구 저장 요청, 설치 안내에 주의 문구 |

## 계획 변경 (2026-11-25, ④ 검증 중)
- TEST-04 실패로 맥 OCR을 Apple Vision 로컬 도우미로 바꾼다 → [[ADR-0003-맥-OCR-Apple-Vision-로컬-도우미]]
- 추가 작업: TASK-13 도우미(Swift) + 로컬 서버 연결, TASK-14 앱의 엔진 자동 선택, TASK-15 파서 보완(구매, 카드결제액, 날짜·시간 붙음)
- 폰은 당분간 Tesseract.js 유지

## 승인
- [x] 사용자 승인 (날짜: 2026-11-25)
