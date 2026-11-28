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
