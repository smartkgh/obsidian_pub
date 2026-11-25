---
type: module
title: store — 결의서 데이터
tags: [모듈]
related: [[system]], [[form-layout]]
created: 2026-11-25
updated: 2026-11-25
---

# store — 결의서 데이터

## 역할
결의서와 내역 줄의 데이터 구조, 합계 계산, 14줄 제한, 표시 형식(`11월 8일`, `49,700원`).

## 코드 위치
- `~/my_projects/expense-report/src/store/report.ts`

## 주요 구성
| 이름 | 설명 |
|---|---|
| `ExpenseReport`, `ExpenseLine`, `Profile` | 데이터 구조. 빈 값은 `null` → 출력물 빈칸 |
| `MAX_LINES = 14`, `addLine()` | 14줄이면 추가하지 않고 `null` (REQ-010) |
| `total()` | 빈 금액 제외 합계 (REQ-008) |
| `CATEGORIES` | `야유회비`, `교사 월례회의` (REQ-005) |

## 관련 요구사항 / 결정
- REQ-005, REQ-008, REQ-009, REQ-010

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현 |
