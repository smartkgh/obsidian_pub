---
type: architecture
title: 시스템 구조
tags: [아키텍처, PWA]
sources: []
related: [[ADR-0001-앱-형태-PWA-USB-설치]], [[ADR-0002-OCR-엔진-Tesseract-js]], [[form-layout]]
created: 2026-11-25
updated: 2026-11-25
---

# 시스템 구조

> 항상 최신 상태를 반영한다. (현재: v1 설계)

## 한눈에 보기

```
┌──────────────────────── 브라우저 (폰 크롬 / 맥 크롬) ────────────────────────┐
│                                                                              │
│  화면 (ui/)                                                                  │
│   ① 작성  ② 영수증 확인·입력  ③ 미리보기·내보내기                            │
│        │              │                     │                                │
│        ▼              ▼                     ▼                                │
│  상태 (store/) ── 결의서 데이터 ──▶ 문서 생성 (export/)                      │
│     │  ▲                              ├─ PDF  (pdf-lib + 한글 폰트)          │
│     │  │ 일자, 금액                    └─ DOCX (docx)                         │
│     │  │                                    ▲                                │
│     │  인식 (ocr/)                     레이아웃 정의 (layout/) ── 공통 사용   │
│     │   ├─ 이미지 전처리                                                     │
│     │   ├─ OcrEngine ── Tesseract.js (교체 가능)                             │
│     │   └─ 영수증 파서 (일자·금액 추출)                                      │
│     ▼                                                                        │
│  저장 (storage/) ── IndexedDB (작성 중 결의서, 영수증 이미지, 기본 정보)      │
│                                                                              │
│  서비스 워커 ── 앱 파일 전체 캐시 (오프라인 실행)                             │
└──────────────────────────────────────────────────────────────────────────────┘
        ▲ 처음 설치/업데이트 때만
        │ 폰: USB + adb reverse → localhost:8080 / 맥: localhost:8080
  맥북의 로컬 서버 (vite preview)
```

외부로 나가는 네트워크 요청은 없다. 서비스 워커가 설치된 뒤에는 서버가 꺼져 있어도 동작한다.

## 기술 선택

| 영역 | 선택 | 이유 |
|---|---|---|
| 언어/빌드 | TypeScript + Vite | 가볍고 빠름, PWA 플러그인 있음 |
| 화면 | 프레임워크 없이 TypeScript (화면 3개) | 의존성 최소화 |
| 오프라인 | vite-plugin-pwa (Workbox 사전 캐시) | 인식 엔진·폰트까지 한 번에 캐시 |
| 인식 | Tesseract.js, `kor+eng`, 로컬 경로 | [[ADR-0002-OCR-엔진-Tesseract-js]] |
| PDF | pdf-lib + @pdf-lib/fontkit + 나눔고딕(OFL) | 폰트 내장, 좌표로 원본 양식 재현 |
| DOCX | docx | 브라우저에서 생성, 표 병합·음영 지원 |
| 저장 | IndexedDB | 이미지(Blob)까지 기기 안에 저장 |
| 테스트 | Vitest (파서, 합계, 레이아웃), Playwright (화면·출력) | |

## 모듈

| 폴더 | 역할 | 관련 REQ |
|---|---|---|
| `src/ui/` | 화면 3개, 입력 폼, 영수증 추가(카메라/사진첩) | 001, 004~007, 009 |
| `src/store/` | 결의서 데이터, 합계 계산, 최대 줄 수 제한 | 008, 010 |
| `src/ocr/` | 전처리, `OcrEngine`, 영수증 파서 | 002, 003 |
| `src/layout/` | 결의서 칸 위치·크기 정의 (mm) | 010~013 |
| `src/export/` | PDF, DOCX 생성, 영수증 증빙 페이지 | 011~013 |
| `src/storage/` | IndexedDB 저장/복원, 영구 저장 요청 | 017 |
| `public/` | Tesseract 파일, 언어 데이터, 폰트 | 014 |

## 데이터 구조

```ts
type ExpenseReport = {
  committee: string;      // 위원회명
  team: string;           // 팀명
  writtenDate: string;    // 작성일 YYYY-MM-DD
  accountant: string;     // ④회계 이름
  teamLeader: string;     // ⑤팀장 이름
  lines: ExpenseLine[];   // 최대 14줄
};

type ExpenseLine = {
  id: string;
  date: { month: number; day: number } | null;  // null이면 빈칸
  category: '야유회비' | '교사 월례회의' | null; // null이면 빈칸
  summary: string;        // 적요
  amount: number | null;  // null이면 빈칸, 합계에서 제외
  note: string;           // 비고
  receiptId: string | null;
  ocr?: { dateFound: boolean; amountFound: boolean };
};
```

## 실행·설치
- 코드 위치: `~/my_projects/expense-report`
- 맥: `npm run serve` → 크롬에서 `http://localhost:8080`
- 폰: [[install-guide]] 참고 (`npm run phone` = adb reverse + serve)
