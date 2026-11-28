---
type: concept
title: "AI 기반 개발·프로토타이핑 및 테스트 자동화"
tags:
  - concept
  - ai
  - llm
  - devops
sources:
  - "raw/assets/my_skplanet_업무히스토리2.pdf"
related:
  - "[[강기훈]]"
  - "[[sk-플래닛]]"
  - "[[syrup-wallet]]"
  - "[[android-app-development]]"
created: "2026-11-28"
updated: "2026-11-28"
---

# AI 기반 개발·프로토타이핑 및 테스트 자동화

## 정의
상용 앱 서비스 기획·개발·검증 과정에서 클라우드 AI(Vertex AI), 코딩/에이전트 CLI, LLM 위키 지식체계 및 자체 검증 도구를 결합해 프로토타이핑과 개발 생산성을 극대화하는 실무 역량이다.

## 설명
- **AI 서비스 프로토타이핑**: [[syrup-wallet]]의 '지금 할 일' 식단기록 서비스 개발 과정에서 **Google Cloud Vertex AI**를 활용한 프로토타입 구현 수행 (사용자 확인 2026-11-28, [[my-skplanet-업무히스토리-2]] p.2 `SYRUPPROD-1635` 연계).
- **LLM 위키 기반 개발 프로세스**: 개발 프로세스 전반에 **LLM 위키(LM 위키)** 구조를 도입해 요구사항·이력·문서화를 체계화하고 AI와 협업하는 워크플로우 구축 (사용자 확인 2026-11-28).
- **개발·테스트 도구 자동화**: 하이브리드 앱(WebView) 환경의 품질 검증 효율을 높이기 위해 **JS 브릿지 페이지 검증 도구** 등 내부 테스트 도구를 직접 구축해 활용 (사용자 확인 2026-11-28).
- **AI 에이전트·CLI 도구 활용**: `Gemini CLI`, `Claude CLI`, `OpenSpec`, `OpenAI`, `로컬 LLM`, `Hermes Agent` 등 다양한 AI 개발 도구를 실무에 통합 활용 (사용자 확인 2026-11-28).

## 근거가 되는 자료·대상
- 사용자 직접 확인 (2026-11-28)
- [[my-skplanet-업무히스토리-2]] — v5.8.12 식단 기록(`SYRUPPROD-1635`), v5.8.16 AI 추천 콘텐츠(`SYRUPPROD-2392`)
- [[sk-플래닛]] / [[강기훈]]

## 관련 개념
- [[android-app-development]]
- [[reward-apptech-syrup]]
