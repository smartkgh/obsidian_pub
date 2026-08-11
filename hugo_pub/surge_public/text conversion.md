---
title: text conversion
date: 2026-02-06
categories:
  - Tech
  - Load
draft: false
tags:
  - ai
---

local file link [[h2]]  
external url link -  [Perplexity](https://www.perplexity.ai)

==Table==

| obsidian   | githut | cloudflare |     |
| ---------- | ------ | ---------- | --- |
| git plugin | action | pages      |     |
|            |        |            |     |
![[Pasted image 20260205171925.png]]


```python
    frontmatter = {
        "title": f'"{file_path.stem}" ',
        "date": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        "draft": "false",
    }
    
    # 기존 frontmatter 추출 및 업데이트
    fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        existing_fm_str = fm_match.group(1)
        # 간단한 key: value 파싱
        for line in existing_fm_str.split('\n'):
            if ':' in line:
                key, *value = line.split(':', 1)
                key = key.strip()
                val = value[0].strip()
                if key and val:
                    frontmatter[key] = val
        # 기존 frontmatter를 내용에서 제거
        content = content[fm_match.end():]
```


```plantuml
@startuml

!theme plain

  

actor User

participant "입력 폼" as Form

participant "app.js" as App

participant "localStorage" as Storage

participant "DOM" as DOM

  

User -> Form : 단어 입력 및 제출

activate Form

  

Form -> App : submit 이벤트

activate App

  

App -> App : 입력 검증

alt 입력 유효

App -> Storage : JSON.stringify(words)

activate Storage

Storage --> App : 저장 완료

deactivate Storage

App -> App : words.push(newWord)

App -> DOM : renderCard(currentIndex)

activate DOM

DOM --> User : 카드 표시

deactivate DOM

App -> Form : 입력 필드 초기화

else 입력 무효

App -> DOM : 경고 메시지 표시

DOM --> User : 오류 표시

end

  

deactivate App

deactivate Form

  

@enduml

```