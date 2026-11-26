# AGENTS.md

이 파일은 이 위키에서 일하는 모든 AI 에이전트(Claude Code, Codex, Cursor, Gemini 등)가 따르는 규칙이다.
작업을 시작하기 전에 이 파일 전체와 `wiki/index.md`를 먼저 읽는다.

---

## 0. 프로젝트 설정

> 새 프로젝트에 이 템플릿을 복사하면 이 섹션만 채운다.

- **프로젝트 이름**: (예: my_career)
- **주제/목적**: (이 위키가 다루는 내용을 한두 문장으로)
- **외부 코드 경로**: (예: `~/my_projects/my_career` — 없으면 "없음")
  - 코드는 ③ 개발 단계에서만 작성한다. 위키나 `raw/`에는 코드를 복사하지 않고 경로와 파일명으로 링크한다.
  - 에이전트가 이 경로를 읽으려면 실행 시 해당 폴더 접근을 허용해야 한다. (예: `claude --add-dir ~/my_projects/my_app`)
- **현재 버전**: v1
- **위키 언어**: 한국어

---

## 1. 폴더 구조

```
raw/                원본 자료 — 추가만 가능, 수정/삭제 금지
  research/         ① 조사 원본: 기사, 논문, 공식 문서
  chats/            중요한 대화 원문 (선택)
  test-logs/        ④ 테스트 실행 원본 로그
  assets/           이미지, 첨부파일

wiki/               에이전트가 쓰고 고치는 지식 페이지
  index.md          전체 목차 (진입점)
  log.md            작업 기록 (추가만)
  overview.md       프로젝트 요약
  research/         ① 조사 정리: 자료별 요약, 비교
  concepts/         ① 개념, 용어
  architecture/     ② 설계 — 항상 최신 상태
  decisions/        ② 설계 결정 기록 (ADR) — 누적
  modules/          ③ 구현된 모듈 설명 — 항상 최신 상태
  queries/          질문과 답변 정리
  versions/vN/      버전별 작업 문서
    requirements.md   요구사항 (REQ-)
    plan.md           ② 설계/계획
    tasks.md          ③ 개발 작업 목록 (TASK-)
    test-plan.md      ④ 검증 계획 (TEST-)
    verification.md   ④ 검증 결과
    result.md         ⑤ 결과 보고서

templates/          문서 양식 — 새 문서는 반드시 여기서 복사해서 시작
```

---

## 2. 핵심 원칙

1. **원본과 정리를 나눈다.** `raw/`의 파일은 사람과 에이전트 모두 추가할 수 있지만, 한 번 들어간 파일은 누구도 수정하거나 삭제하지 않는다. 요약, 해석, 결론은 모두 `wiki/`에 쓴다.
2. **현재 상태와 이력을 나눈다.** `architecture/`, `modules/`, `concepts/`는 항상 최신 상태만 담는다. 무엇이 언제 왜 바뀌었는지는 `versions/`, `decisions/`, `log.md`에 남긴다. 버전마다 위키 전체를 복사하지 않는다.
3. **근거를 남긴다.** 모든 주장에는 출처를 단다. 위키 페이지는 `[[페이지명]]`, 원본은 `raw/...` 경로, 코드는 `외부코드경로/파일:줄` 형식으로 쓴다.
4. **단계를 섞지 않는다.** ① 조사 → ② 설계 → ③ 개발 → ④ 검증 → ⑤ 보고 순서로 진행하고, 각 단계가 끝나면 사용자 승인 후 다음 단계로 넘어간다.
5. **추측하지 않는다.** 근거가 없거나 자료끼리 모순되면 멈추고 사용자에게 묻는다.

---

## 3. 작업 흐름

### 3.1 자료 넣기 (Ingest)

`raw/`에 새 자료가 들어오거나 사용자가 자료를 주면:

1. 원본이 `raw/`에 없으면 알맞은 하위 폴더에 저장한다. (웹 자료는 본문을 Markdown으로 저장하고 출처 URL과 수집일을 맨 위에 적는다.)
2. `templates/research.md`로 `wiki/research/`에 요약 페이지를 만든다. (원본 1개 = 요약 1개)
3. 등장하는 개념/용어는 `wiki/concepts/` 페이지를 만들거나 갱신한다.
4. 기존 페이지와 모순되는 내용이 있으면 양쪽 페이지에 표시하고 사용자에게 알린다.
5. `wiki/index.md`와 `wiki/log.md`를 갱신한다.

### 3.2 질문하기 (Query)

1. `wiki/index.md`를 먼저 읽고 관련 페이지를 찾아 답한다. 위키에 없으면 `raw/`와 외부 코드를 확인한다.
2. 답변에는 참고한 페이지와 경로를 밝힌다.
3. 답변이 다시 쓸 만하면 **"위키에 저장할까요?"라고 묻고**, 승인받으면 `templates/query.md`로 `wiki/queries/`에 저장한다.
4. 답변 중 설계 결정이 나오면 `decisions/`에, 요구사항 변경이 나오면 현재 버전의 `requirements.md`에 반영한다. (사용자 승인 후)
5. `wiki/log.md`에 기록한다.

### 3.3 점검하기 (Lint)

사용자가 요청하면 다음을 찾아 보고하고, 승인받은 항목만 고친다.

- 끊긴 `[[링크]]`, 어디에서도 링크되지 않은 페이지
- `index.md`에 빠진 페이지
- 페이지끼리 모순되는 내용, 오래된 내용
- 추적이 끊긴 ID (TASK가 없는 REQ, TEST가 없는 REQ 등)

### 3.4 버전 작업 (① 조사 → ⑤ 보고)

| 단계 | 입력 | 출력 | 다음 단계로 가는 조건 |
|---|---|---|---|
| 요구사항 | 사용자 요청 | `vN/requirements.md` | 사용자 승인 |
| ① 조사 | `raw/research/`, 웹 | `research/`, `concepts/` | 요구사항별 근거 자료 정리 |
| ② 설계 | `research/`, `requirements.md` | `architecture/`, `decisions/`, `vN/plan.md`, `vN/test-plan.md` | 모든 REQ가 plan에 연결됨 + 사용자 승인 |
| ③ 개발 | `plan.md`, `architecture/` | 외부 코드, `vN/tasks.md`, `modules/` | 모든 TASK 완료 |
| ④ 검증 | `test-plan.md`, 코드 | `raw/test-logs/`, `vN/verification.md` | 모든 TEST 실행 및 기록 |
| ⑤ 보고 | `vN/` 전체 | `vN/result.md` | 사용자 승인 |

- **코드는 ② 설계가 승인되기 전에 작성하지 않는다.**
- 개발 중 설계를 바꿔야 하면 멈추고 사용자에게 알린 뒤 `decisions/`와 `plan.md`를 먼저 고친다.
- 검증이 실패하면 결과를 있는 그대로 `verification.md`에 기록한다. 실패를 숨기거나 테스트를 임의로 바꾸지 않는다.

### 3.5 새 버전 시작

1. 이전 버전 `result.md`의 status를 `done`으로 확인한다. 외부 코드가 있으면 git 태그(예: `v1.0`)를 기록한다.
2. `wiki/versions/vN/` 폴더를 만들고 `templates/requirements.md`로 요구사항을 작성한다.
3. 새 버전의 `requirements.md`에는 **이전 버전 대비 추가/변경/삭제만** 적는다.
4. 이 파일의 "0. 프로젝트 설정"의 현재 버전과 `log.md`를 갱신한다.

### 3.6 버전 완료

1. `architecture/`, `modules/`, `overview.md`를 최신 상태로 갱신한다.
2. `result.md`에 REQ → TASK → TEST → 결과 추적표를 완성한다.
3. 버전 문서의 status를 모두 `done`으로 바꾼다.
4. `index.md`, `log.md`를 갱신한다.

---

## 4. 작성 규칙

### 4.1 파일명

- kebab-case를 쓴다. 한글도 쓸 수 있다. (예: `oauth-login.md`, `소셜-로그인.md`)
- 결정 기록: `ADR-0001-제목.md` (번호는 계속 증가)
- 질문 정리: `YYYY-MM-DD-제목.md`
- 대화 원문, 테스트 로그: `YYYY-MM-DD-제목.md` / `YYYY-MM-DD-vN-TEST-xx.log`

### 4.2 Frontmatter

모든 위키 페이지는 맨 위에 frontmatter를 둔다.

```yaml
---
type: research | concept | architecture | decision | module | query | requirements | plan | tasks | test-plan | verification | result
title: 페이지 제목
status: draft | in-progress | done      # 버전 문서와 결정 기록만
version: v1                             # 버전 문서만
tags: []
sources: []                             # raw/ 경로 또는 URL
related:                                # 위키 링크는 따옴표로 감싼 목록
  - "[[연결 페이지]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

frontmatter는 Obsidian 속성(YAML)으로 읽힌다. 다음을 지킨다.
- 위키 링크는 **따옴표로 감싼 목록**으로 쓴다: `related:` 다음 줄에 `  - "[[페이지]]"`. `related: [[a]], [[b]]`처럼 쓰면 링크가 깨진다.
- `{{title}}`, `{{date}}` 같은 템플릿 자리표시는 따옴표로 감싼다: `title: "{{title}}"`.
- `:`, `#`, `[`, `{`로 시작하거나 그런 글자를 포함한 값은 따옴표로 감싼다.

### 4.3 링크

- 위키 페이지끼리는 `[[페이지명]]`으로 연결한다.
- 새 페이지를 만들면 최소 1개 이상의 기존 페이지에서 링크되게 한다.

### 4.4 ID 체계

| ID | 의미 | 위치 |
|---|---|---|
| `REQ-001` | 요구사항 — 버전이 바뀌어도 번호 유지 | `requirements.md` |
| `TASK-01` | 개발 작업 — 연결된 REQ 표시 | `tasks.md` |
| `TEST-01` | 검증 항목 — 연결된 REQ 표시 | `test-plan.md`, `verification.md` |
| `ADR-0001` | 설계 결정 | `decisions/` |

### 4.5 log.md 형식

새 기록은 맨 아래에 추가하고, 기존 기록은 고치지 않는다.

```markdown
## [YYYY-MM-DD] 종류 | 제목
- 변경: 만들거나 고친 페이지
- 메모: (선택)
```

종류: `ingest`, `query`, `lint`, `requirements`, `research`, `design`, `develop`, `verify`, `report`, `version`

---

## 5. 멈추고 사용자에게 물어야 할 때

- 단계를 넘어갈 때 (승인)
- 요구사항이 모호하거나 서로 모순될 때
- 근거 자료가 부족하거나 자료끼리 충돌할 때
- 개발 중 설계를 바꿔야 할 때
- `raw/`의 파일을 수정하거나 삭제해야 할 것 같을 때 (원칙적으로 금지)
- 위키 구조(폴더, 규칙)를 바꿔야 할 때
