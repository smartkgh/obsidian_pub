---

title: Hermes 멀티에이전트 추가 방법 created: 2026-06-21 tags:

- hermes
- telegram
- multi-agent
- llm
- automation aliases:
- Hermes 멀티에이전트 설정
- Hermes DM Topics 라우터

---

# Hermes 멀티에이전트 추가 방법

> [!summary] 한 줄 요약 텔레그램과 연동된 Hermes Agent에 **DM Topics(직접 호출) + delegate_task(자동 위임)** 를 혼용하는 하이브리드 멀티에이전트를 구성한다. 토픽을 고르면 전용 에이전트, General에서 막연히 던지면 자동 위임.

---

## 1. 전체 구조 이해

Hermes에서 "멀티에이전트"는 두 가지 결이 있다.

|메커니즘|역할|비고|
|---|---|---|
|**DM Topics + Skill Binding**|사용자가 토픽(방)을 직접 골라 전용 에이전트로 사용|수동 선택. 토픽 = 에이전트|
|**delegate_task (서브에이전트)**|메인 에이전트가 무거운/병렬 작업을 하위 에이전트에 위임|자동. 한 토픽 안에서 동작|
|**Profiles**|API 키·메모리까지 완전 격리된 별도 봇|업무/개인 완전 분리 시|

> [!important] 핵심 개념 구분
> 
> - **토픽 선택** = 내가 어느 방에 들어가느냐 (수동)
> - **delegate_task** = 메인 에이전트가 무거운 일을 하위 일꾼에게 나눠 시킴 (자동, 한 토픽 안에서)
> - "General에서 코딩 질문하면 Coding 토픽으로 자동 전환"되는 토픽 간 라우팅은 **기본 제공되지 않는다.** 라우터 스킬로 흉내 낸다.

### 채택한 구성: 라우터 + 직접 명령어 혼용

```
텔레그램 메시지
   │
   ├─ 토픽 직접 선택 (Coding / Research)  → 전용 스킬 에이전트 (직접)
   │
   └─ General 토픽 + 자연어            → general-router → 분류 → 직접 답변 or delegate_task 위임
```

---

## 2. DM Topics 활성화

### 2-1. BotFather에서 Threaded Mode 켜기 (먼저)

1. 텔레그램에서 **@BotFather** 열기
2. `/mybots` → 봇 선택
3. **Bot Settings → Threads Settings**
4. **Threaded Mode 켜기** (`has_topics_enabled`)
5. "사용자의 토픽 생성 허용"은 유지 (`allows_users_to_create_topics`)

### 2-2. `/topic` 으로 자동 활성화 (권장)

봇 DM에서 아래 입력:

```
/topic
```

- Hermes가 `getMe`로 플래그를 확인하고, 충족되면 멀티세션 모드를 켠 뒤 **System 토픽**을 생성·고정한다.
- BotFather 설정이 안 됐으면, 무엇을 토글해야 하는지 스크린샷으로 안내해준다.

> [!note] System 토픽 `/topic` 후 생기는 **System 토픽은 예약된 방**이다. 이름 변경·삭제하지 말 것. 상태 표시/시스템 명령용.

---

## 3. config.yaml 에 DM Topics 정의

### 3-1. 파일 열기

```bash
nano ~/.hermes/config.yaml
```

### 3-2. 올바른 위치와 들여쓰기 (가장 많이 틀리는 부분)

> [!warning] 함정 두 가지
> 
> 1. **위치**: `dm_topics`는 최상위 `telegram:` 블록의 `extra:` 아래여야 한다. `display:` 밑(`display.platforms.telegram.extra`)에 넣으면 **무시된다.**
> 2. **들여쓰기**: `dm_topics`는 `extra:`보다 2칸 더 안쪽. 탭(Tab) 금지, 스페이스만.

최상위 `telegram:` 블록을 이렇게 구성한다.

```yaml
telegram:
  reactions: false
  channel_prompts: {}
  allowed_chats: ''
  extra:
    rich_messages: true
    dm_topics:
      - chat_id: 8644491980        # 본인 텔레그램 user ID (@userinfobot 으로 확인)
        topics:
          - name: Coding
            skill: test-driven-development
          - name: Research
            skill: arxiv             # 설치 확인 후, 없으면 줄 삭제
          - name: General
            skill: general-router
```

들여쓰기 계층:

|키|칸 수|
|---|---|
|`extra:`|2|
|`rich_messages:`, `dm_topics:`|4|
|`- chat_id:`|6|
|`topics:`|8|
|`- name:`|10|

### 3-3. 적용

```bash
hermes gateway restart
```

게이트웨이가 config를 읽고 각 토픽을 텔레그램에 자동 생성한다. 생성된 `thread_id`는 config에 자동으로 다시 기록된다(다음 재시작 시 재생성 안 함).

> [!tip] 토픽 이름 자동변경 끄기 Hermes는 첫 대화 후 토픽 이름을 자동으로 바꾼다. 직접 정한 이름을 고정하려면 같은 `extra:` 아래에 `disable_topic_auto_rename: true` 추가.

---

## 4. 스킬 설치

### 4-1. 핵심 사실

- Hermes에 **`software-development` 라는 단일 스킬은 없다.** 코딩 워크플로우가 여러 세분 스킬로 쪼개져 있다.
- 스킬은 **능력**이 아니라 **규율/방법론**을 더한다. 코딩 자체는 모델이 한다.
- `obra/superpowers` 묶음이 코딩 에이전트 강화용으로 가장 많이 추천됨.

### 4-2. 설치 명령

```bash
hermes skills install skills-sh/obra/superpowers/test-driven-development
hermes skills install skills-sh/obra/superpowers/requesting-code-review
hermes skills install skills-sh/obra/superpowers/subagent-driven-development
```

### 4-3. 자주 만나는 문제

> [!bug] GitHub rate limit 무인증 GitHub API는 시간당 60회 제한. 막히면:
> 
> ```bash
> gh auth login        # 한도 5,000/hr 로 상향 (권장)
> ```
> 
> 또는 `~/.hermes/.env` 에 `GITHUB_TOKEN=ghp_...` 추가.

> [!bug] 보안 스캐너 BLOCKED (DANGEROUS) 커뮤니티 스킬은 설치 시 스캔된다. `systematic-debugging`, `using-superpowers`는 **오탐으로 차단**됐다.
> 
> - `using-superpowers`: CLAUDE.md/AGENTS.md 등 **설정파일을 문서에서 언급**했다는 이유로 persistence 위험 판정 → 실제론 설명 문서일 뿐.
> - `--force`로도 dangerous 판정은 못 뚫는다.
> - **대응**: 굳이 우회하지 말고 건너뛴다. 이미 설치된 스킬로 충분.

### 4-4. 설치 확인

```bash
hermes skills list
```

---

## 5. 라우터 스킬 (general-router) 만들기

> [!info] 스킬의 한계 스킬은 **지침/프롬프트**일 뿐, 사용자를 다른 토픽으로 옮기는 시스템 제어권이 없다. 라우터 스킬은 _General 에이전트 한 명이 질문 성격을 스스로 판단해 직접 처리하거나 delegate_task로 위임하도록_ 유도하는 것.

### 5-1. 폴더·파일 생성

```bash
mkdir -p ~/.hermes/skills/routing/general-router
nano ~/.hermes/skills/routing/general-router/SKILL.md
```

> [!note] `name`은 부모 폴더명과 정확히 일치해야 함 → `name: general-router`

### 5-2. SKILL.md 내용

```markdown
---
name: general-router
description: Classify incoming requests and route them to the right specialized approach or delegate heavy parallel work to subagents. Use as the default General-topic dispatcher.
version: 1.0.0
metadata:
  hermes:
    tags: [Routing, Dispatcher, Orchestration]
---

# General Router

당신은 General 토픽의 디스패처입니다. 사용자의 요청을 분석해 가장 적합한 방식으로 처리합니다.

## When to use this
- General 토픽에 들어오는 모든 자연어 요청에 항상 적용됩니다.

## 분류 절차 (먼저 수행)
요청을 받으면 먼저 아래 카테고리 중 하나로 분류하세요:
1. 코딩/개발 — 코드 작성·디버깅·리뷰·리팩토링, 빌드/배포, 기술 아키텍처
2. 리서치/조사 — 여러 소스 조사, 논문, 비교 분석, 정보 수집
3. 일반 — 단순 질문, 잡담, 위 어디에도 안 맞는 것

## 위임 규칙 (반드시 따를 것)
다음 중 하나라도 해당하면, 직접 답하지 말고 **반드시 delegate_task를 사용**하세요:
- 서로 독립적인 조사·작업 대상이 2개 이상일 때
  (예: 여러 프레임워크/제품/옵션 비교, 여러 파일 동시 처리)
- 각 대상을 따로 깊이 조사해야 할 때
- 사용자가 "비교", "각각", "동시에", "여러" 같은 표현을 쓸 때

처리 방식:
1. 작업을 독립된 하위 작업으로 나눈다 (대상 1개당 서브에이전트 1개).
2. 각 하위 작업을 delegate_task로 병렬 위임한다.
3. 서브에이전트는 맥락을 모르므로, 각 위임에 필요한 정보를 명확히 적는다.
4. 모든 결과를 모아 사용자에게 종합 정리한다.

**중요**: "내가 직접 답할 수 있으니 위임은 생략"하지 마세요.
위 조건에 맞으면 답을 알더라도 delegate_task로 위임하는 것이 이 토픽의 규칙입니다.

### 단일·단순 작업
위 조건에 해당하지 않는 단일 질문은 직접 답하세요.

## Pitfalls
- 단순 질문에 불필요하게 위임하지 마세요. 위임은 병렬·대형 작업에만.
- 분류가 애매하면 사용자에게 한 번 되물어도 됩니다.

## Verification
- 코딩 요청에 개발자다운 구조적 답변이 나왔는가
- 다중 주제 요청에서 delegate_task 위임이 시도됐는가
```

### 5-3. 적용

```bash
hermes gateway restart
```

---

## 6. delegate_task 자동 위임 튜닝

> [!check] 진단 결과
> 
> - 도구 존재: `delegate_task` 사용 가능 ✓
> - 강제 위임("delegate_task를 사용해서..."): 정상 작동 ✓ (3개 서브에이전트 병렬 실행 확인)
> - 자발적 위임: 모델이 "직접 할 수 있다"고 판단해 위임을 생략하는 경향

### 자발적 위임이 안 될 때

1. **본문 강화** — 5-2의 "위임 규칙"처럼 `답을 알아도 위임하라`, `비교/각각/여러 표현이면 위임` 같이 구체적·강제적으로 기준 명시.
2. **모델 교체** — 약한 모델(`owl-alpha` 등)은 도구가 있어도 안 쓰려 함. 토픽 안에서 `/model`로 도구 사용 잘하는 모델로 변경.
3. **승인 설정** — `delegation.subagent_auto_approve: false`면 위임 시 승인 프롬프트가 뜬다. 매번 번거로우면 `true`로 변경 (단, 처음엔 false 권장).

> [!warning] 과도한 위임 주의 자발적 위임을 너무 공격적으로 튜닝하면 단순 질문까지 서브에이전트를 띄워 느려지고 비용이 늘어난다. **"2개 이상의 독립 대상"** 정도가 적당한 균형점. 너무 잦으면 "3개 이상" 또는 "각각 깊은 조사 필요 시"로 좁힌다.

---

## 7. 동작 확인용 테스트

### 스킬 로드 확인

- 로그(가장 확실): General 토픽에 메시지 후 `grep -iE "skill" ~/.hermes/logs/gateway.log | tail`
- 토픽에서 직접: `지금 이 세션에 로드된 스킬이 뭐야?`

### 자동 위임 확인

General 토픽에서 자연어로만:

```
React, Vue, Svelte 상태관리 비교해줘
```

→ "delegate_task" 단어 없이도 3개로 쪼개 병렬 위임하면 자발적 라우팅 완성.

### 정상 기동 로그 예시

```
[Telegram] Connected to Telegram (polling mode)
[Telegram] DM topic loaded from config: ...:Coding -> thread_id=224
[Telegram] DM topic loaded from config: ...:Research -> thread_id=226
[Telegram] DM topic loaded from config: ...:General -> thread_id=228
✓ telegram connected
Gateway running with 1 platform(s)
```

---

## 8. 트러블슈팅 빠른 참조

|증상|원인|해결|
|---|---|---|
|`Auto-skill 'X' not found`|바인딩한 스킬 미설치 / 잘못된 이름|`hermes skills list`로 정확한 이름 확인, 교체 또는 `skill:` 줄 삭제|
|토픽이 자동 생성 안 됨|`dm_topics` 위치/들여쓰기 오류|최상위 `telegram.extra` 아래, 스페이스 들여쓰기 확인|
|`The chat is not a forum`|포럼(Topics) 모드 꺼짐|`/topic` 또는 BotFather Threaded Mode|
|`Message thread not found`|thread_id 불일치 / 토픽 삭제됨|토픽 재생성. 보통 config 수정 과정의 일시적 현상|
|스킬 설치 rate limit|무인증 GitHub 60/hr|`gh auth login` 또는 `GITHUB_TOKEN`|
|스킬 BLOCKED (DANGEROUS)|보안 스캐너 (오탐 포함)|대개 건너뛰기 권장. 이미 설치된 스킬로 충분|
|delegate_task 자발적 위임 안 됨|모델이 직접 처리 판단|라우터 본문 강화 / `/model` 교체|

> [!note] 로그 시각 확인 `tail`은 파일 끝을 보여줄 뿐 "최신 재시작 이후"만이 아니다. 경고를 만나면 **로그 시각이 재시작 이후인지** 먼저 확인. 옛날 로그가 그대로 보이는 경우가 많다.

---

## 관련 노트

- [[Hermes Agent 설정]]
- [[OpenRouter 모델 비용]]
- [[Mac Mini M4 개발환경]]