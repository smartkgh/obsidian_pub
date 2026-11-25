---
type: tasks
title: v1 작업 목록
status: in-progress
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
| [ ] | TASK-01 | 프로젝트 골격: Vite, TypeScript, PWA, Vitest, 오프라인 자산 준비 스크립트 | 014 | `package.json`, `vite.config.ts`, `scripts/` | |
| [ ] | TASK-02 | 데이터 구조, 합계, 14줄 제한 | 008, 010 | `src/store/` | |
| [ ] | TASK-03 | IndexedDB 저장/복원, 영구 저장 요청, 기본 정보 유지 | 009, 017 | `src/storage/` | |
| [ ] | TASK-04 | 영수증 파서 (일자, 금액) | 002, 003 | `src/ocr/parser.ts` | |
| [ ] | TASK-05 | 이미지 전처리, OcrEngine(Tesseract.js 로컬) | 002, 003, 014 | `src/ocr/` | |
| [ ] | TASK-06 | 결의서 레이아웃 정의 (박스 목록, 14줄, 증빙 6장/쪽) | 010, 013 | `src/layout/` | |
| [ ] | TASK-07 | PDF 출력 (나눔고딕 내장, 증빙 페이지) | 012, 013 | `src/export/pdf.ts` | |
| [ ] | TASK-08 | DOCX 출력 (같은 치수, 증빙 페이지) | 011, 013 | `src/export/docx.ts` | |
| [ ] | TASK-09 | 화면 ① 작성, ② 영수증 확인·입력, ③ 미리보기·내보내기, 맥 넓은 화면 | 001, 004~007, 009 | `src/ui/` | |
| [ ] | TASK-10 | 서비스 워커 오프라인 캐시, 오프라인 준비 표시 | 014, 015, 016 | `vite.config.ts`, `src/main.ts` | |
| [ ] | TASK-11 | 폰 USB 설치 스크립트 (`npm run phone`) | 015 | `scripts/phone.sh` | |
| [ ] | TASK-12 | 단위 테스트 (파서, 합계, 레이아웃, PDF/DOCX 생성) | 002, 003, 008, 010, 013 | `tests/` | |

## 진행 메모
- 2026-11-25: 개발 환경에 Node.js가 없어 Homebrew로 설치 (v26.13.1)
