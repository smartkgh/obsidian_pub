---
title: "Claude 사용 가이드"
date: 2026-02-20T00:00:00+09:00
draft: false
description: "Claude Cowork와 Claude Code의 핵심 사용법을 정리한 가이드입니다."
tags: ["claude", "AI", "anthropic", "cowork", "claude-code", "자동화", "개발도구"]
categories: ["도구", "AI"]
author: "안녕"
weight: 1
toc: true
---

## Claude Cowork란?

**Claude Cowork**는 Anthropic의 Claude 데스크탑 앱에서 제공하는 기능으로, 개발자가 아닌 일반 사용자도 파일 및 작업 관리를 자동화할 수 있는 도구입니다.

주요 특징은 다음과 같습니다. 로컬 파일 시스템에 안전하게 접근하며, 자연어 명령으로 복잡한 작업을 수행합니다. 문서, 스프레드시트, 프레젠테이션의 생성 및 편집이 가능하고 웹 검색 및 정보 수집 자동화도 지원합니다.

---

## Claude Cowork 주요 기능

### 파일 작업

Word 문서(`.docx`), Excel 스프레드시트(`.xlsx`), PowerPoint 프레젠테이션(`.pptx`), PDF 파일의 생성 및 편집을 지원합니다.

### 웹 작업

웹 페이지 내용 검색 및 요약, 데이터 수집 및 분석, URL 내용 추출 등의 작업이 가능합니다.

### 스킬 (Skills)

Skills는 특정 작업에 최적화된 플러그인입니다.

| 스킬 이름 | 설명 |
|-----------|------|
| `xlsx` | Excel 파일 생성/편집 |
| `pptx` | PowerPoint 슬라이드 제작 |
| `docx` | Word 문서 작성 |
| `pdf` | PDF 처리 |
| `schedule-task` | 자동화 스케줄 설정 |

---

## Claude Cowork 사용법

### 기본 워크플로우

```
1. Claude 데스크탑 앱 실행
2. Cowork 모드 활성화
3. 작업할 폴더 선택 (Select Folder)
4. 자연어로 작업 지시
5. 결과 확인 및 다운로드
```

### 파일 생성 예시

Excel 파일 생성:

```
"월별 매출 데이터를 정리한 Excel 파일을 만들어줘"
```

프레젠테이션 생성:

```
"2024년 연간 보고서를 10장 슬라이드로 만들어줘"
```

문서 편집:

```
"첨부한 Word 파일의 문법 오류를 수정해줘"
```

### 폴더 접근 설정

> **중요:** Cowork가 파일에 접근하려면 반드시 **폴더 선택 권한**을 부여해야 합니다.
> `폴더 선택 → 접근 허용` 순서로 진행하세요.

---

## Claude Code란?

**Claude Code**는 개발자를 위한 CLI(Command Line Interface) 도구로, 터미널에서 직접 코딩 작업을 Claude에게 위임할 수 있습니다.

주요 특징으로는 터미널 기반 인터페이스, 코드베이스 분석 및 수정, Git 작업 자동화, 테스트 실행 및 디버깅이 있습니다.

---

## Claude Code 설치 및 설정

### 설치

```bash
# npm을 통한 설치
npm install -g @anthropic-ai/claude-code

# 설치 확인
claude --version
```

### 초기 설정

```bash
# API 키 설정
export ANTHROPIC_API_KEY="your-api-key-here"

# 또는 .env 파일에 추가
echo 'ANTHROPIC_API_KEY=your-api-key-here' >> ~/.env
```

### 프로젝트 시작

```bash
# 원하는 프로젝트 디렉토리로 이동
cd /path/to/your/project

# Claude Code 실행
claude
```

---

## Claude Code 주요 명령어

### 슬래시 명령어

| 명령어 | 기능 |
|--------|------|
| `/help` | 도움말 표시 |
| `/clear` | 대화 내용 초기화 |
| `/compact` | 대화 요약 (컨텍스트 절약) |
| `/cost` | 현재 세션 비용 확인 |
| `/doctor` | 환경 설정 진단 |
| `/init` | 프로젝트 초기화 (`CLAUDE.md` 생성) |
| `/memory` | 메모리 설정 관리 |
| `/review` | 코드 리뷰 요청 |

### 실용적인 사용 예시

코드 분석:

```bash
claude "이 프로젝트의 전체 구조를 분석하고 개선점을 알려줘"
```

버그 수정:

```bash
claude "src/app.py에서 발생하는 TypeError를 수정해줘"
```

테스트 작성:

```bash
claude "UserService 클래스에 대한 단위 테스트를 작성해줘"
```

Git 커밋:

```bash
claude "변경된 내용을 분석하고 적절한 커밋 메시지로 커밋해줘"
```

---

## Claude Code 활용 팁

### CLAUDE.md 파일 활용

프로젝트 루트에 `CLAUDE.md` 파일을 만들어 Claude가 프로젝트를 이해하도록 돕습니다.

```markdown
# 프로젝트 개요
이 프로젝트는 ...

# 주요 규칙
- 코드 스타일: PEP8 준수
- 테스트: pytest 사용
- 브랜치 전략: Git Flow

# 금지 사항
- 직접 main 브랜치에 push 금지
```

### 효율적인 프롬프팅

좋은 프롬프트 예시:

```
"src/utils/formatter.py 파일을 읽고,
 format_date() 함수가 ISO 8601 형식도 처리하도록 수정해줘.
 수정 후 기존 테스트가 모두 통과하는지 확인해줘."
```

### 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl+C` | 현재 작업 중단 |
| `Ctrl+L` | 화면 지우기 |
| `↑/↓` | 이전/다음 명령어 |

---

## Cowork vs Code 비교

| 기준 | Claude Cowork | Claude Code |
|------|--------------|-------------|
| **대상** | 일반 사용자 | 개발자 |
| **인터페이스** | GUI (데스크탑 앱) | CLI (터미널) |
| **주요 작업** | 문서, 파일 관리 | 코딩, 개발 자동화 |
| **설치** | Claude 앱 설치 | npm 패키지 설치 |
| **파일 접근** | 폴더 선택 방식 | 프로젝트 디렉토리 |
| **스킬/플러그인** | 지원 | 지원 |

---

## 관련 링크

- [Anthropic 공식 문서](https://docs.claude.com)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
- [Claude API 문서](https://docs.anthropic.com)
- [지원 페이지](https://support.claude.com)
