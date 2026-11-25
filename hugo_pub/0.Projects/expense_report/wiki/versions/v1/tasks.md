---
type: tasks
title: v1 작업 목록
status: done
version: v1
tags: []
related: [[plan]], [[system]], [[form-layout]]
created: 2026-11-25
updated: 2026-11-25
---

# v1 작업 목록

코드 위치: `~/my_projects/expense-report`

| 완료 | ID | 작업 | REQ | 코드 위치 | 비고 |
|---|---|---|---|---|---|
| [x] | TASK-01 | 프로젝트 골격: Vite, TypeScript, PWA, Vitest, 오프라인 자산 준비 스크립트 | 014 | `package.json`, `vite.config.ts`, `scripts/` | |
| [x] | TASK-02 | 데이터 구조, 합계, 14줄 제한 | 008, 010 | `src/store/` | |
| [x] | TASK-03 | IndexedDB 저장/복원, 영구 저장 요청, 기본 정보 유지 | 009, 017 | `src/storage/` | |
| [x] | TASK-04 | 영수증 파서 (일자, 금액) | 002, 003 | `src/ocr/parser.ts` | |
| [x] | TASK-05 | 이미지 전처리, OcrEngine(Tesseract.js 로컬) | 002, 003, 014 | `src/ocr/` | |
| [x] | TASK-06 | 결의서 레이아웃 정의 (박스 목록, 14줄, 증빙 6장/쪽) | 010, 013 | `src/layout/` | |
| [x] | TASK-07 | PDF 출력 (나눔고딕 내장, 증빙 페이지) | 012, 013 | `src/export/pdf.ts` | |
| [x] | TASK-08 | DOCX 출력 (같은 치수, 증빙 페이지) | 011, 013 | `src/export/docx.ts` | |
| [x] | TASK-09 | 화면 ① 작성, ② 영수증 확인·입력, ③ 미리보기·내보내기, 맥 넓은 화면 | 001, 004~007, 009 | `src/ui/` | |
| [x] | TASK-10 | 서비스 워커 오프라인 캐시, 오프라인 준비 표시 | 014, 015, 016 | `vite.config.ts`, `src/main.ts` | |
| [x] | TASK-11 | 폰 USB 설치 스크립트 (`npm run phone`) | 015 | `scripts/phone.sh` | |
| [x] | TASK-12 | 단위 테스트 (파서, 합계, 레이아웃, PDF/DOCX 생성) | 002, 003, 008, 010, 013 | `tests/` | |
| [x] | TASK-13 | 맥 Apple Vision 도우미(Swift) + 로컬 서버 `/api/ocr` 연결 (ADR-0003) | 002, 003, 016 | `native/mac/`, `vite.config.ts` | 검증 중 추가 |
| [x] | TASK-14 | 앱에서 엔진 자동 선택 (도우미 있으면 Vision, 없으면 Tesseract.js) | 002, 003 | `src/ocr/` | 검증 중 추가 |
| [x] | TASK-15 | 파서 보완: 구매, 카드결제액, 날짜·시간 붙음 | 002, 003 | `src/ocr/parser.ts` | 검증 중 추가 |

## 진행 메모
- 2026-11-25: 개발 환경에 Node.js가 없어 Homebrew로 설치 (v26.13.1)
- TASK-07: pdf-lib 폰트 서브셋(subset: true) 사용 시 한글 글자 대부분이 빠지는 문제 → 폰트 전체 내장으로 변경. PDF 크기 약 1.6MB
- TASK-07: 나눔고딕에 ①~⑤ 글자가 없음 → PDF에서는 원과 숫자를 직접 그림 (미리보기·DOCX는 기기 폰트로 표시)
- TASK-04: 브라우저 점검에서 OCR이 "합 계"를 "합 A"로 읽어 금액이 빈칸 → 보완 규칙 2개 추가 (줄 첫 글자 '합/총', 품목 합 검산)
- TASK-09: 줄 추가·삭제 직후 새로고침하면 저장 전에 사라지는 문제 → 구조 변경은 즉시 저장, 입력은 0.25초 모아서 저장
- TASK-09: 편집 화면에 "인식된 글자 보기" 추가 (인식 결과 확인용, 계획에 없던 작은 추가)
- 영수증 위치 강조(이미지 위 파란 상자, 시안에 있던 것)는 v1에서 제외 → 인식됨/인식 못함 색 표시로 대체
- 브라우저 자동 점검 `scripts/smoke.mjs` 추가 (Playwright): 8/8 통과 — 상세 결과는 ④ 검증 단계에서 기록

- TASK-13~15 (2026-11-25, 검증 중 추가): 맥 Apple Vision 도우미 `native/mac/VisionOCR.swift` → `bin/vision-ocr`(npm run serve 때 자동 컴파일), 로컬 서버 `/api/ocr`(localhost 요청만, 임시 파일 즉시 삭제), 앱 엔진 자동 선택·실패 시 기본 엔진 전환, 상태 표시에 엔진 이름. 실험 도구 `lab/`, `scripts/ocr-eval.mjs`

## 개발 중 테스트 결과 (요약)
- 단위 테스트: 32/32 통과 (`npm test`)
- 브라우저 점검(가짜 영수증, 맥 크롬 헤드리스): 서비스 워커 설치, 일자·금액 인식, 합계, 오프라인 새로고침, 오프라인 PDF/DOCX 저장, 외부 요청 0건 — 8/8 통과
