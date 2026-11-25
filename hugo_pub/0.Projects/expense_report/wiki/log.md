---
type: log
title: Log
---

# Log

작업 기록. 새 기록은 맨 아래에 추가하고 기존 기록은 고치지 않는다.

## [2026-11-25] version | 위키 템플릿 생성
- 변경: AGENTS.md, README.md, wiki/index.md, wiki/overview.md, templates/

## [2026-11-25] version | expense_report 프로젝트 시작
- 변경: llmwiki_template 복사, AGENTS.md 프로젝트 설정, overview.md, index.md

## [2026-11-25] requirements | v1 요구사항 초안
- 변경: versions/v1/requirements.md (REQ-001~016, 열린 질문 6개)
- 메모: 원본 양식 raw/assets/지출결의서.jpeg 기준. 서명은 출력 후 수기, 영수증은 뒤 페이지 증빙 첨부, 안드로이드·맥북 각각 로컬 전용

## [2026-11-25] requirements | v1 요구사항 열린 질문 반영
- 변경: versions/v1/requirements.md (REQ-001~017)
- 메모: 항목 2개(야유회비, 교사 월례회의), 결의서 1페이지 고정, 금액 자동 인식 실패 시 빈칸, 송금처·예산 칸은 비워 두고 별도 기입, 카드 영수증만, 출력 모양은 원본 이미지 기준

## [2026-11-25] requirements | v1 요구사항 승인
- 변경: versions/v1/requirements.md (status: approved)

## [2026-11-25] research | ① 조사 — OCR, 문서 생성, 앱 형태
- 변경: raw/research/2026-11-25-web-search-ocr-docx.md, research/ocr-options.md, research/card-receipt-parsing.md, research/document-generation.md, research/local-app-packaging.md, index.md
- 메모: 앱 설치 방식(인터넷 주소에서 1회 설치 허용 여부)과 실제 영수증 샘플이 설계 전 확인 필요

## [2026-11-25] design | 화면 시안 (초안)
- 변경: architecture/ui-mockup.html
- 메모: 폰 기준 3개 화면(작성, 영수증 확인·입력, 미리보기·내보내기). 설치 방식(USB/APK)은 미정

## [2026-11-25] design | ② 설계 — 구조, 레이아웃, 계획, 검증 계획
- 변경: decisions/ADR-0001, ADR-0002, architecture/system.md, form-layout.md, install-guide.md, ui-mockup.html(증빙 6장), versions/v1/plan.md, test-plan.md, requirements.md(결정 사항 추가), index.md
- 메모: 사용자 결정 — 영수증 증빙 6장/쪽, USB(adb reverse) 설치. 최대 14줄. 사용자 승인 대기
