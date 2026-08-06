---
categories:
- Tech
- Load
date: 2026-02-06
draft: false
tags:
- ai
title: text conversion
---
local file link [h2]({{< ref "h2.md" >}})  
external url link -  [Perplexity](https://www.perplexity.ai)

<mark>Table</mark>

| obsidian   | githut | cloudflare |     |
| ---------- | ------ | ---------- | --- |
| git plugin | action | pages      |     |
|            |        |            |     |
![](/images/Pasted image 20260205171925.png)

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

{{< plantuml >}}407374617274756d6c0a0a217468656d6520706c61696e0a0a6163746f7220557365720a0a7061727469636970616e742022ec9e85eba0a520ed8fbc2220617320466f726d0a0a7061727469636970616e7420226170702e6a7322206173204170700a0a7061727469636970616e7420226c6f63616c53746f72616765222061732053746f726167650a0a7061727469636970616e742022444f4d2220617320444f4d0a0a55736572202d3e20466f726d203a20eb8ba8ec96b420ec9e85eba0a520ebb08f20eca09cecb69c0a0a616374697661746520466f726d0a0a466f726d202d3e20417070203a207375626d697420ec9db4ebb2a4ed8ab80a0a6163746976617465204170700a0a417070202d3e20417070203a20ec9e85eba0a520eab280eca69d0a0a616c7420ec9e85eba0a520ec9ca0ed9aa80a0a417070202d3e2053746f72616765203a204a534f4e2e737472696e6769667928776f726473290a0a61637469766174652053746f726167650a0a53746f72616765202d2d3e20417070203a20eca080ec9ea520ec9984eba38c0a0a646561637469766174652053746f726167650a0a417070202d3e20417070203a20776f7264732e70757368286e6577576f7264290a0a417070202d3e20444f4d203a2072656e646572436172642863757272656e74496e646578290a0a616374697661746520444f4d0a0a444f4d202d2d3e2055736572203a20ecb9b4eb939c20ed919cec8b9c0a0a6465616374697661746520444f4d0a0a417070202d3e20466f726d203a20ec9e85eba0a520ed9584eb939c20ecb488eab8b0ed99940a0a656c736520ec9e85eba0a520ebacb4ed9aa80a0a417070202d3e20444f4d203a20eab2bdeab3a020eba994ec8b9ceca78020ed919cec8b9c0a0a444f4d202d2d3e2055736572203a20ec98a4eba59820ed919cec8b9c0a0a656e640a0a64656163746976617465204170700a0a6465616374697661746520466f726d0a0a40656e64756d6c{{< /plantuml >}}