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

## [2026-11-25] design | v1 설계 승인
- 변경: versions/v1/plan.md (status: approved)

## [2026-11-25] develop | ③ 개발 — TASK-01~12 완료
- 변경: versions/v1/tasks.md, modules/store.md, storage.md, ocr.md, layout.md, export.md, ui.md, index.md
- 코드: ~/my_projects/expense-report (git 저장소 생성, 아직 커밋하지 않음)
- 메모: Node.js 설치(Homebrew). 개발 중 발견·수정 4건(PDF 한글 누락, ①~⑤ 글자 없음, "합 A" 오인식, 저장 타이밍). 단위 테스트 32/32, 브라우저 점검 8/8

## [2026-11-25] verify | ④ 검증 (맥북) — 실제 영수증 2장 인식 실패
- 변경: versions/v1/verification.md, raw/test-logs/2026-11-25-v1-TEST-04.log, raw/test-logs/2026-11-25-vision-ocr.swift
- 원본: raw/assets/KakaoTalk_Photo_2026-11-25-20-43-28 001.jpeg, …-29 002.jpeg (사용자 추가, 실제 카드 영수증)
- 메모: Tesseract.js 일자 0/2·금액 0/2, 전처리 20여 조합도 불안정. Apple Vision은 정확. 엔진 교체는 설계 변경 → 사용자 결정 대기
- 코드: src/ocr/image.ts에 전처리 옵션 추가(기본값은 기존과 동일), 실험 도구 lab/, scripts/ocr-eval.mjs 추가

## [2026-11-25] design | 맥 OCR 엔진 교체 결정 (B안)
- 변경: decisions/ADR-0003-맥-OCR-Apple-Vision-로컬-도우미.md, ADR-0002(맥은 대체됨 표시), versions/v1/plan.md(계획 변경), tasks.md(TASK-13~15 추가)

## [2026-11-25] develop | TASK-13~15 — Apple Vision 도우미, 엔진 자동 선택, 파서 보완
- 변경: versions/v1/tasks.md, modules/ocr.md, architecture/system.md, architecture/install-guide.md
- 코드: native/mac/VisionOCR.swift, server/ocr-middleware.ts, scripts/build-mac-ocr.mjs, src/ocr/engine.ts·index.ts·parser.ts, src/ui/app.ts

## [2026-11-25] verify | TEST-04 맥 재검증 통과
- 변경: versions/v1/verification.md, raw/test-logs/2026-11-25-v1-TEST-04-recheck.log, index.md
- 메모: 실제 영수증 일자 2/2, 금액 2/2 (장당 약 0.5초). 도우미 없을 때 기본 엔진 전환 확인. 단위 34/34, 브라우저 점검 8/8. 폰은 여전히 Tesseract.js

## [2026-11-25] develop | Vite 설정 경고 제거
- 코드: vite.config.ts(가져오기 경로에 .ts 확장자), server/ocr-middleware.ts(`__dirname` → `import.meta.dirname`), tsconfig.json(allowImportingTsExtensions)
- 메모: 사용자 문의 — 서버 없이 localhost:8080이 열리는 것은 서비스 워커 오프라인 캐시 때문(정상). 이때는 맥 인식 엔진 사용 불가

## [2026-11-25] lint | frontmatter를 Obsidian 속성 형식으로 수정
- 변경: wiki 페이지 21개, templates 11개 (llmwiki_template 템플릿 11개 포함), 두 폴더의 AGENTS.md 4.2
- 메모: `related: [[a]], [[b]]` → 따옴표 목록, `{{title}}`/`{{date}}` → 따옴표. YAML 검사 49개 모두 통과
