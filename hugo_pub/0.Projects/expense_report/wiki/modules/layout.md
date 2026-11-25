---
type: module
title: layout — 결의서 레이아웃
tags: [모듈]
related:
  - "[[form-layout]]"
  - "[[export]]"
created: 2026-11-25
updated: 2026-11-25
---

# layout — 결의서 레이아웃

## 역할
[[form-layout]]을 코드로 옮긴 것. 칸 위치·크기(mm)를 한 곳에 정의하고 PDF, DOCX, 미리보기가 함께 쓴다.

## 코드 위치
- `~/my_projects/expense-report/src/layout/form.ts`

## 주요 구성
| 이름 | 설명 |
|---|---|
| `formTable()` | 표 전체 행/칸 정의 (헤더, 14줄, 합계, 송금처, 서명·예산·회색 칸) — DOCX와 박스가 공용 |
| `buildFormBoxes()` | 1쪽을 그릴 박스 목록 — PDF, 미리보기 |
| `evidencePages()` | 증빙 페이지 배치 (6장/쪽, 2열×3행), 캡션 |
| `fitText()` | 넘치면 글자 축소 후 2줄 줄바꿈 |
| `CHURCH_NAME`, `FORM_REVISION` | 바닥 고정 문구 |

## 원본과 다른 점
- 회색 칸의 담당자 이름(원본에 인쇄된 이름)은 넣지 않았다. 직함만 표시.

## 관련 요구사항
- REQ-010, REQ-011, REQ-012, REQ-013

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현 |
