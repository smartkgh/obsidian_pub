---
type: module
title: ui — 화면
tags: [모듈]
related:
  - "[[system]]"
  - "[[storage]]"
  - "[[ocr]]"
created: 2026-11-25
updated: 2026-11-25
---

# ui — 화면

## 역할
화면 3개(① 작성, ② 영수증 확인·입력, ③ 미리보기·내보내기)와 맥 넓은 화면(왼쪽 입력 + 오른쪽 미리보기). 시안: `architecture/ui-mockup.html`

## 코드 위치
- `~/my_projects/expense-report/src/ui/app.ts` — 화면, 이벤트, 영수증 추가·인식 순서 처리
- `~/my_projects/expense-report/src/ui/preview.ts` — 레이아웃 박스를 HTML로 그림
- `~/my_projects/expense-report/src/ui/styles.css`
- `~/my_projects/expense-report/src/main.ts`

## 동작
- 영수증 여러 장 → 한 장씩 차례로 인식. 사용자가 이미 입력한 값은 덮어쓰지 않음
- 인식 결과: 초록(인식됨) / 노랑(인식 못함), "인식된 글자 보기"
- 14줄이면 추가 버튼 비활성 + 안내
- 줄 순서 바꾸기(▲▼), 삭제, 새 결의서(기본 정보 유지)
- 오른쪽 아래 상태: "오프라인 준비 완료 ✓" / 작업 중 표시

## 관련 요구사항
- REQ-001, REQ-004~007, REQ-009, REQ-010, REQ-016, REQ-017

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현 |
