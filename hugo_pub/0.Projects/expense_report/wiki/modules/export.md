---
type: module
title: export — PDF·DOCX 출력
tags: [모듈]
related: [[layout]], [[document-generation]]
created: 2026-11-25
updated: 2026-11-25
---

# export — PDF·DOCX 출력

## 역할
결의서 1쪽 + 영수증 증빙 페이지를 PDF와 DOCX로 만들고 기기에 저장하거나 공유한다.

## 코드 위치
- `~/my_projects/expense-report/src/export/pdf.ts` — pdf-lib + 나눔고딕 전체 내장
- `~/my_projects/expense-report/src/export/docx.ts` — docx, 같은 치수의 표 (열 경계를 합친 격자 + 칸 병합)
- `~/my_projects/expense-report/src/export/browser.ts` — 폰트 불러오기, 다운로드, 공유

## 알아둘 점
- PDF 폰트를 일부만 넣으면(subset) 한글이 빠지는 문제가 있어 전체를 넣는다 → PDF 약 1.6MB
- 나눔고딕에 ①~⑤가 없어 PDF에서는 원과 숫자를 직접 그린다
- DOCX 글꼴은 맑은 고딕 지정. 여는 기기에 없으면 다른 글꼴로 표시된다
- 파일 이름: `지출결의서_<팀명>_<작성일>.pdf|docx`, 다운로드 폴더에 저장, 지원 기기에서는 공유 버튼

## 관련 요구사항
- REQ-011, REQ-012, REQ-013

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현 |
