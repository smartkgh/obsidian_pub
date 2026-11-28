---
type: log
title: Log
---

# Log

작업 기록. 새 기록은 맨 아래에 추가하고 기존 기록은 고치지 않는다.

## [2026-11-26] decision | 위키 템플릿 생성
- 변경: AGENTS.md, README.md, wiki/index.md, wiki/overview.md, templates/

## [2026-11-26] ingest | raw/assets 전체 10개 자료 수집 및 위키 구축
- 변경: `wiki/sources/` 10건, `wiki/entities/` 8건, `wiki/concepts/` 9건, `wiki/index.md`, `wiki/overview.md`
- 메모: `my_skplanet_업무히스토리1.pdf`(2014.07~2022.12)와 `my_skplanet_업무히스토리2.pdf`(2023.01~2026.09) 반영. 민감정보는 최종 결과물에 그대로 노출하기로 사용자 확인.

## [2026-11-26] analysis | 경력기술서 양식 2종 비교 분석
- 변경: `wiki/analysis/양식-2종-비교-분석.md`
- 메모: 역순 연대기식과 혼합형 2가지 형태 모두 제작하기 위한 구조·강점·구성 전략 정리.

## [2026-11-26] brief | 이력서 및 경력기술서 2종 요청(brief.md) 초안 작성
- 변경: `outputs/2026-11-26-이력서-경력기술서/brief.md`
- 메모: SK 플래닛 입·퇴사일, 직책/부서/역할 범위, 정량 성과 등 확인 사항 정리 후 승인 대기.

## [2026-11-28] decision | D-0001 작성 방침 및 경력 산정 기준 확정
- 변경: `wiki/decisions/D-0001-작성-방침-및-경력-기준.md`, `wiki/concepts/ai-development-workflow.md`, `wiki/entities/강기훈.md`, `wiki/entities/sk-플래닛.md`, `wiki/entities/kt알파.md`, `wiki/index.md`, `wiki/overview.md`
- 메모: SK 플래닛 재직(2013.11~2026.10.31, Syrup개발팀 매니저), 정량 성과(크래시율 0.01% 유지, HTTP(S) 전환 커뮤니케이션 비용 30% 감소, Kotlin 전환 크래시율 20% 감소), AI 활용 역량, ZipMaker 제외(총 25년 6개월), 푸딩카메라 기간(2012.11~2013.02), 풀스택 포지셔닝 확정.

## [2026-11-28] outline | 이력서 및 경력기술서 2종 개요(outline.md) 작성
- 변경: `outputs/2026-11-26-이력서-경력기술서/brief.md` (확정), `outputs/2026-11-26-이력서-경력기술서/outline.md`
- 메모: 이력서(양식1), 경력기술서 역순 연대기식, 경력기술서 혼합형 3개 결과물 목차 및 근거 매핑 완료. 사용자 승인 대기.

## [2026-11-28] draft | 이력서 및 경력기술서 2종 초안(draft-v1.md) 작성
- 변경: `outputs/2026-11-26-이력서-경력기술서/outline.md` (확정), `outputs/2026-11-26-이력서-경력기술서/draft-v1.md`
- 메모: 이력서(자기소개서 포함)·경력기술서 역순 연대기식·경력기술서 혼합형 3종 초안 작성 및 문장별 출처 기재.

## [2026-11-28] review | 초안 v1 사실 대조 검토(review-v1.md) 완료
- 변경: `outputs/2026-11-26-이력서-경력기술서/review-v1.md`, `outputs/2026-11-26-이력서-경력기술서/draft-v1.md` (표현 4건 정제), `wiki/index.md`, `wiki/overview.md`
- 메모: 34개 사실 대조 완료(30건 일치, 4건 원본 미기재·과장 우려 표현 즉시 수정). 사용자 승인 후 ⑤ 최종 DOCX 변환 진행 예정.

## [2026-11-28] final | 이력서 및 경력기술서 2종 최종 DOCX 생성 완료
- 변경: `outputs/2026-11-26-이력서-경력기술서/이력서-강기훈-final-v1.docx`, `경력기술서-역순연대기식-강기훈-final-v1.docx`, `경력기술서-혼합형-강기훈-final-v1.docx`, `wiki/index.md`, `wiki/overview.md`
- 메모: 참고 양식 3종 기반 XML 생성 및 `~/my_projects/my_carrer/` 저장. 인라인 근거 주석 제거 및 전체 텍스트 검증 완료.

## [2026-11-28] draft | 이력서 및 경력기술서 2종 Claude 독립 초안(draft-v1.md) 작성
- 변경: `outputs/2026-11-이력서-경력기술서-claude/brief.md`, `outputs/2026-11-이력서-경력기술서-claude/draft-v1.md`, `wiki/index.md`
- 메모: 승인된 기존 brief·outline을 이어받아 비교용으로 따로 작성. 경력 요약·STAR 구조 추가, SK 플래닛 PROJECT 최신순 재정렬, 근거 없는 기간·역할 7건은 [확인 필요]로 표시. 주민번호는 초안에 쓰지 않음.

## [2026-11-28] ingest | 사용자 확인 답변 2 수집
- 변경: `raw/sources/2026-11-28-사용자-확인-답변-2.md`(신규), `wiki/entities/sk-플래닛.md`, `wiki/concepts/ai-development-workflow.md`
- 메모: 구조 전환 연도(HTTP(S) 2014·WebView 2017·Kotlin 2020)와 역할(제안+팀 합의), BEP 기여, 전금법 존 서버 이전, 개인 AI 자동화, 입사 직후 전면 개편·Jenkins. 기존 위키의 "주도" 표현과 다름을 sk-플래닛에 표시.

## [2026-11-28] draft | Claude 작성본 초안 v2
- 변경: `outputs/2026-11-이력서-경력기술서-claude/draft-v2.md`, `brief.md`, `wiki/index.md`
- 메모: 답변 2 반영. 혼합형 SK PROJECT 07(사내 첫 PoC 앱 전면 개편) 신설. 남은 확인 3건(BEP 표현, PoC 해석·종료 시점, 삼성증권 시기).

## [2026-11-28] ingest | 사용자 확인 답변 3 수집
- 변경: `raw/sources/2026-11-28-사용자-확인-답변-3.md`(신규), `wiki/entities/sk-플래닛.md`
- 메모: 광고 성과 = 서비스 흑자 전환 기여, "first poc app" = 회사 핵심 서비스, 삼성증권 시기 미기재 유지.

## [2026-11-28] draft | Claude 작성본 초안 v3
- 변경: `outputs/2026-11-이력서-경력기술서-claude/draft-v3.md`, `brief.md`, `wiki/index.md`
- 메모: 답변 3 반영. 남은 사항은 PROJECT 07 종료 시점(2014.07) 추정 1건.

## [2026-11-28] draft | Claude 작성본 초안 v4
- 변경: `raw/sources/2026-11-28-사용자-확인-답변-4.md`(신규), `outputs/2026-11-이력서-경력기술서-claude/draft-v4.md`, `brief.md`, `wiki/entities/sk-플래닛.md`, `wiki/index.md`
- 메모: Syrup 앱 전면 개편 기간 2013.11–2014.06 확정. 남은 확인 사항 없음.

## [2026-11-28] draft | Claude 작성본 초안 v5
- 변경: `raw/sources/2026-11-28-사용자-요청-자기소개서-비즈니스배경.md`(신규), `outputs/2026-11-이력서-경력기술서-claude/draft-v5.md`, `brief.md`, `wiki/index.md`
- 메모: 자기소개서 "풀스택 경험" 문단 기술 스택 보강 + "다양한 비즈니스 경험" 문단 신설. 새 사실 없이 기존 원본(R, P, H1, H2, U)에서만 가져옴.

## [2026-11-28] review | Claude 작성본 검토 v5
- 변경: `outputs/2026-11-이력서-경력기술서-claude/review-v5.md`, `draft-v6.md`, `brief.md`, `wiki/index.md`
- 메모: 원본(.doc·.pptx·PDF 2건) 텍스트를 직접 추출해 53개 사실 대조. 일치 43, 근거 페이지 번호 오류 7, 표현 3 → v6에서 정정. 근거 없는 사실 0건.
