---
title: Obsidian → Quartz → Surge 파이프라인 구축
tags: [quartz, obsidian, surge, 정적사이트, 배포]
created: 2026-08-05
---

# Obsidian → Quartz → Surge 파이프라인 구축

Obsidian vault를 Quartz로 변환하여 Surge에 배포하는 과정 정리. 기존 Hugo 파이프라인과 병행/대체 검토용.

---

## 1. Quartz 기본 개념

Quartz는 Obsidian 노트를 정적 웹사이트(디지털 가든)로 변환하는 도구.

### Hugo 대비 장점
- **검색**: FlexSearch 기반 클라이언트 사이드 전문 검색이 기본 내장 (Hugo는 lunr.js/Algolia 별도 연동 필요)
- **카테고리/태그 목록**: frontmatter의 `tags`만 넣으면 `/tags/태그명`, `/tags` 전체 인덱스 자동 생성. Hugo의 taxonomy 설정 불필요
- **폴더 목록**: 폴더별 인덱스 페이지 자동 생성, `Explorer` 컴포넌트로 사이드바 폴더 트리 기본 제공

### 한계
- **PlantUML 미지원**: Quartz는 Mermaid만 네이티브 지원. PlantUML은 Obsidian 플러그인이 빌드 단계에 관여하지 않아 별도 처리 필요
- **노트별 개별 스타일링 불가**: 전역 테마 + 컴포넌트 커스터마이징 방식 (Notion처럼 페이지별 자유 스타일 불가)

---

## 2. 설치 (Quartz v5 기준)

### 사전 요구사항
```bash
node -v   # v22 이상
npm -v    # 10.9.2 이상
git -v
```

### 설치 순서
```bash
# 1. GitHub 템플릿으로 리포지토리 생성 후 클론
git clone https://github.com/[본인계정]/quartz.git
cd quartz

# 2. 의존성 설치
npm i

# 3. 초기화 마법사
npx quartz create
# → 템플릿: obsidian 선택
# → 콘텐츠 방식: symlink (원본 vault 유지) 권장
# → base URL: 예) mynotes.surge.sh (https:// 제외)

# 4. 플러그인 설치
npx quartz plugin install --from-config

# 5. 로컬 미리보기
npx quartz build --serve
# → localhost:8080
```

---

## 3. 콘텐츠 폴더 구조 (symlink)

### 문제 상황
Obsidian vault 구조:
```
MyVault/
├── surge_public/      ← 게시용 노트 폴더 (직접 정의)
│   └── index.md
└── images/             ← surge_public 밖에 있던 이미지 폴더
```

`content`를 `surge_public`으로만 symlink하면 `images/`가 빠져서 이미지가 안 보임.

### 해결 — vault 루트 대신 필요한 폴더만 개별 symlink
```bash
mkdir content
ln -s "/절대경로/MyVault/surge_public" content    # 최종적으로 이 폴더 자체를 content로
```

**주의**: `content`가 symlink 상태에서는 `content/images`처럼 내부에 새 symlink를 못 만듦.
`content`를 실제 디렉토리로 두고 그 안에 여러 개 symlink 거는 방식도 가능:
```bash
mkdir content
ln -s "/경로/Notes" content/Notes
ln -s "/경로/images" content/images
```

### index.md 규칙
- `content/index.md`만 루트(`/`)로 매핑됨
- `content/surge_public/index.md`는 `/surge_public`로 매핑 (루트 아님)
- 루트에 뭔가 보여주려면 `content` 최상위에 `index.md` 필요 (없어도 빌드는 되지만 `/` 접속 시 404)

---

## 4. 이미지가 안 보이는 문제

### 원인
1. symlink 범위 밖에 이미지 폴더가 있음
2. `ObsidianFlavoredMarkdown` 트랜스포머의 `wikilinks: true` 옵션 미설정 시 `![[image.png]]` 변환 안 됨

### Obsidian 설정으로 해결 (플러그인 불필요)
**설정 → 파일 및 링크 → 새 첨부 파일 저장 위치 → "In subfolder under current folder"**, 하위 폴더명 `images` 지정

→ 노트가 있는 폴더 기준 상대 경로로 자동 저장됨:
```
surge_public/note1.md → surge_public/images/ 에 저장
```

### 폴더별로 다른 규칙이 필요할 때 (커뮤니티 플러그인)
- **obsidian-attachment-rules**: 폴더 경로별 첨부파일 목적지 규칙 정의
- **obsidian-attachment-management**: `${notepath}` 등 변수 기반 유연한 제어, override로 특정 폴더 예외 규칙

---

## 5. PlantUML 지원 — Quartz 빌드 타임 트랜스포머

Obsidian 노트에는 PlantUML 코드블록을 그대로 두고, **Quartz 빌드 시점에 이미지로 변환**하는 방식.

### 구조
```
quartz/plugins/transformers/plantuml.ts   ← 새로 작성
quartz/plugins/transformers/index.ts       ← export 추가
quartz.config.ts                            ← 플러그인 등록
```

### 설치
```bash
npm install plantuml-encoder
npm install -D @types/mdast unist-util-visit
```

### 트랜스포머 코드 (`quartz/plugins/transformers/plantuml.ts`)
```ts
import { QuartzTransformerPlugin } from "../types"
import { visit } from "unist-util-visit"
import { encode } from "plantuml-encoder"
import type { Code, Html } from "mdast"

const PLANTUML_SERVER = "https://www.plantuml.com/plantuml/svg/"

export const PlantUML: QuartzTransformerPlugin = () => {
  return {
    name: "PlantUML",
    markdownPlugins() {
      return [
        () => (tree) => {
          visit(tree, "code", (node: Code, index, parent) => {
            if (node.lang !== "plantuml") return
            const encoded = encode(node.value)
            const url = `${PLANTUML_SERVER}${encoded}`
            const imgNode: Html = {
              type: "html",
              value: `<img src="${url}" alt="PlantUML diagram" class="plantuml-diagram" />`,
            }
            if (parent && typeof index === "number") {
              parent.children[index] = imgNode
            }
          })
        },
      ]
    },
  }
}
```

### 등록 (`quartz.config.ts`)
```ts
import { PlantUML } from "./quartz/plugins/transformers/plantuml"

plugins: {
  transformers: [
    Plugin.FrontMatter(),
    Plugin.ObsidianFlavoredMarkdown({ wikilinks: true }),
    PlantUML(),
    Plugin.SyntaxHighlighting(),
  ],
}
```

### 동작 방식 / 한계
- 빌드 시점엔 URL 문자열만 생성 (`<img src="인코딩된URL">`), 실제 렌더링은 브라우저가 PlantUML 공개 서버 호출할 때 발생
- 오프라인에서도 보이는 정적 이미지가 필요하면, 빌드 시점에 Node `fetch`로 실제 SVG를 받아 `public/`에 저장하는 방식으로 변경 필요 (빌드 속도는 느려짐)
- 민감한 다이어그램은 공개 서버 대신 자체 호스팅 PlantUML 서버(Docker) URL로 교체 권장

---

## 6. Surge 배포

### 배포 명령 — 반드시 public 폴더 기준
```bash
npx quartz build
cd public
surge
```
또는 루트에서 경로 지정:
```bash
npx quartz build
surge public --domain your-domain.surge.sh
```

### 주의
- 프로젝트 루트에서 `surge`만 실행하면 소스 폴더까지 통째로 배포됨 → 반드시 `public` 지정
- 재배포 시 `--domain` 명시 안 하면 새 랜덤 도메인 생성될 수 있음
- SPA 라우팅을 위해 `404.html`을 `200.html`로 복사해두면 서브경로 404 방지:
  ```bash
  cp public/404.html public/200.html
  ```

### baseUrl 일치 확인
`quartz.config.ts`의 `baseUrl`이 실제 Surge 도메인과 다르면 링크 깨짐 → 404처럼 보일 수 있음
```ts
configuration: {
  baseUrl: "실제도메인.surge.sh",
}
```

---

## 7. 사이드바(Explorer) 커스터마이징

`quartz.layout.ts`에서 제어.

### 완전히 없애기
```ts
export const defaultContentPageLayout: PageLayout = {
  left: [
    Component.PageTitle(),
    Component.Search(),
    Component.Darkmode(),
    // Component.Explorer(),   ← 주석 처리하면 사이드바 제거
  ],
}
```

### 폭만 줄이기
```scss
// quartz/styles/custom.scss
:root {
  --sidePanelWidth: 200px;
}
```

### 기본 접힌 상태로 시작
```ts
Component.Explorer({
  folderDefaultState: "collapsed",
  useSavedState: true,
}),
```

### 모바일에서만 숨기기
```ts
Component.DesktopOnly(Component.Explorer()),
```

---

## 8. 프로젝트 구조에 대한 참고

Quartz는 npm 전역 CLI가 아니라 **사이트마다 통째로 클론해서 커스터마이징하는 템플릿** 구조.

- 사이트별로 독립된 리포지토리 + `quartz.config.ts` + 커스텀 트랜스포머를 갖는 게 기본 설계
- 여러 사이트 운영 시: 프로젝트별 별도 클론이 일반적 (`quartz-personal/`, `quartz-work/` 등 각각 독립)
- Quartz 원본 업데이트 반영: `npx quartz upgrade`
- 직접 만든 트랜스포머(PlantUML 등)를 여러 프로젝트에서 재사용하려면 별도 npm 패키지화하거나, 보통은 파일 복사로 처리

---

## 진행 상태 체크리스트

- [x] Quartz 설치 및 로컬 미리보기 성공
- [x] content symlink 구조 정리 (surge_public 기준)
- [x] index.md 루트 매핑 문제 해결
- [x] 이미지 첨부 경로 문제 해결 (subfolder 설정)
- [ ] PlantUML 트랜스포머 실제 적용 및 테스트
- [ ] Surge 배포 확인 (baseUrl, 200.html 포함)
- [ ] Explorer 사이드바 커스터마이징 적용
- [ ] GitHub Actions 자동화 (obsidian → quartz build → surge deploy)
