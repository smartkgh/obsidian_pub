"""키워드 1개 + 한 줄 요약 생성 (LLM 1회 호출, 실패 시 휴리스틱)"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter

SYSTEM_PROMPT = (
    "너는 한국어 음성 전사문을 정리하는 도우미다. "
    "전사문은 띄어쓰기가 불완전할 수 있으니 의미로 보정해서 읽어라."
)

USER_PROMPT_TEMPLATE = """다음은 산책 중 스마트폰으로 녹음한 한국어 음성의 전사문이다.

---
{text}
---

다음을 만들어 JSON 하나로만 답하라. 설명·코드블록 없이 JSON 객체만 출력.

1) "keyword": 이 녹음의 핵심 주제를 나타내는 한국어 키워드 1개.
   - 2~12자, 명사형, 띄어쓰기 없이 붙여 쓰기 (예: 아파트재건축, 산책단상, 교회수련회준비)
   - 조사·문장부호·따옴표 금지
2) "summary": 핵심을 담은 한국어 한 문장 (40자 이내, 마침표로 끝내기)

예시 출력: {{"keyword": "아파트재건축", "summary": "재건축 추진위 구성과 주민 설명회 일정을 정리했다."}}"""

STOPWORDS = {
    "그리고", "그러니까", "근데", "그래서", "저는", "제가", "우리", "이거", "그거", "저거",
    "근데요", "있습니다", "했습니다", "합니다", "같습니다", "것같아", "이제", "다음", "오늘",
    "진짜", "너무", "정말", "그냥", "약간", "뭔가", "이런", "그런", "저런", "때문", "생각",
}

HALLUCINATIONS = re.compile(r"^(감사합니다|고맙습니다|시청해주셔서|구독과 좋아요|MBC 뉴스)")


def _clean_for_prompt(text: str, limit: int = 12000) -> str:
    body = text.strip()
    if len(body) > limit:
        body = body[:limit] + "\n…(이하 생략)"
    return body


def _post_chat(cfg, text: str) -> dict | None:
    api_key_env = str(cfg.get("keyword", "api_key_env", "DEEPSEEK_API_KEY"))
    api_key = os.environ.get(api_key_env)
    if not api_key:
        return None

    base_url = str(cfg.get("keyword", "base_url", "https://api.deepseek.com/v1")).rstrip("/")
    url = f"{base_url}/chat/completions"
    payload = {
        "model": cfg.get("keyword", "model", "deepseek-chat"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=_clean_for_prompt(text))},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    timeout = float(cfg.get("keyword", "timeout_seconds", 30))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None

    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _heuristic(text: str) -> dict:
    tokens = [
        t for t in re.findall(r"[가-힣]{2,}", text)
        if t not in STOPWORDS and not t.endswith(("습니다", "합니다", "했다", "입니다"))
    ]
    if tokens:
        counts = Counter(tokens)
        best = max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))[0]
        keyword = best[:12]
    else:
        keyword = "녹음"
    sentence = re.split(r"(?<=[.?!])\s+", text.strip())
    summary = next((s.strip() for s in sentence if len(s.strip()) > 8), text.strip()[:60])
    if summary and summary[-1] not in ".?!":
        summary += "."
    return {"keyword": keyword, "summary": summary[:80]}


def generate(text: str, cfg, log=None) -> tuple[str, str, str]:
    """(keyword, summary, provider) 반환"""
    provider = str(cfg.get("keyword", "provider", "deepseek")).lower()

    if provider in ("deepseek", "openrouter") and text.strip():
        data = _post_chat(cfg, text)
        if data and str(data.get("keyword", "")).strip():
            keyword = re.sub(r"\s+", "", str(data["keyword"]).strip())
            summary = str(data.get("summary", "")).strip()
            return keyword, summary, provider
        if log:
            log.warning("키워드 LLM 호출 실패 → 휴리스틱으로 대체")

    data = _heuristic(text)
    return data["keyword"], data["summary"], "heuristic"


def is_hallucination(text: str) -> bool:
    return bool(HALLUCINATIONS.match(text.strip()))
