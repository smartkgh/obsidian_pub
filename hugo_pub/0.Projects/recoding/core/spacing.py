"""전사문 띄어쓰기 교정 (LLM, 청크 단위)

Apple SpeechTranscriber 는 한국어 어절 경계를 자주 붙여서 내보낸다
(예: "동의서는이번주까지걷기로했어요"). 읽기·검색 품질을 위해 공백만 교정한다.

핵심 원칙: **문자는 절대 LLM 출력을 쓰지 않는다.** 원문의 비공백 문자를 그대로 두고,
LLM 이 제안한 공백 위치만 이식한다(difflib 정렬 기반). 따라서 단어가 바뀌거나
추가·삭제될 위험이 구조적으로 0 이다.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import urllib.error
import urllib.request

SYSTEM_PROMPT = (
    "너는 한국어 띄어쓰기 교정기다. 단어를 바꾸거나 추가·삭제하지 않고 "
    "공백만 넣거나 뺀다. 문장부호와 줄바꿈 구조를 그대로 유지한다."
)

USER_TEMPLATE = """다음은 음성 인식 전사문이다. 띄어쓰기만 교정하라.

규칙:
- 비공백 글자의 순서와 내용을 절대 바꾸지 말 것 (오타 수정·단어 추가 금지)
- 문장부호 그대로, 문단 구조 유지
- 교정된 본문만 출력. 설명·머리말·코드블록 금지

전사문:
{text}"""

SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def _non_space(text: str) -> str:
    return "".join(text.split())


def _hard_split(unit: str, size: int) -> list[str]:
    """공백 기준으로 size 이하 조각으로 강제 분할 (문장이 비정상적으로 길 때)"""
    pieces: list[str] = []
    buf = ""
    for word in unit.split(" "):
        while len(word) > size:                     # 공백조차 없는 초장문
            if buf:
                pieces.append(buf)
                buf = ""
            pieces.append(word[:size])
            word = word[size:]
        if not word:
            continue
        candidate = f"{buf} {word}" if buf else word
        if len(_non_space(candidate)) > size:
            pieces.append(buf)
            buf = word
        else:
            buf = candidate
    if buf:
        pieces.append(buf)
    return pieces


def _split_chunks(text: str, size: int) -> list[str]:
    """문단 → 문장 순으로 잘게 나눈 뒤 size(비공백 기준) 이하로 묶는다."""
    units: list[str] = []
    for para in text.split("\n\n"):
        if len(_non_space(para)) <= size:
            units.append(para)
            continue
        for sentence in SENTENCE_END.split(para):
            if len(_non_space(sentence)) <= size:
                units.append(sentence)
            else:
                units.extend(_hard_split(sentence, size))

    chunks: list[str] = []
    buf = ""
    for unit in units:
        if buf and len(_non_space(buf)) + len(_non_space(unit)) > size:
            chunks.append(buf)
            buf = unit
        else:
            buf = f"{buf}\n\n{unit}" if buf else unit
    if buf:
        chunks.append(buf)
    return chunks


def _post(cfg, text: str) -> str | None:
    env_key = str(cfg.get("keyword", "api_key_env", "DEEPSEEK_API_KEY"))
    api_key = os.environ.get(env_key)
    if not api_key:
        return None

    base_url = str(cfg.get("keyword", "base_url", "https://api.deepseek.com/v1")).rstrip("/")
    payload = {
        "model": cfg.get("keyword", "model", "deepseek-chat"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(text=text)},
        ],
        "temperature": 0.0,
        "max_tokens": max(512, int(len(text) * 1.8) + 200),
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    timeout = float(cfg.get("keyword", "timeout_seconds", 30)) * 2
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError,
            IndexError, TypeError, OSError):
        return None


def _whitespace_marks(candidate: str) -> dict[int, str]:
    """후보 텍스트에서 '몇 번째 비공백 문자 앞에 어떤 공백이 오는가'를 뽑는다."""
    marks: dict[int, str] = {}
    index = 0
    run = ""
    for ch in candidate:
        if ch.isspace():
            run += ch
            continue
        if run:
            marks[index] = run if "\n" in run else " "
            run = ""
        index += 1
    return marks


def _apply_spacing_only(original: str, candidate: str) -> str:
    """원문 문자는 그대로, 후보의 공백 위치만 이식한다(정렬이 맞는 구간에 한해)."""
    source = _non_space(original)
    target = _non_space(candidate)
    marks = _whitespace_marks(candidate)

    out: list[str] = []
    matcher = difflib.SequenceMatcher(None, source, target, autojunk=False)
    for tag, i1, i2, j1, _j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                sep = marks.get(j1 + (k - i1))
                if sep and out:
                    out.append(sep)
                out.append(source[k])
        elif tag in ("replace", "delete"):
            out.append(source[i1:i2])       # 불일치 구간은 공백 없이 그대로
    return "".join(out)


def _clean_output(text: str) -> str:
    body = text.strip()
    if body.startswith("```"):
        body = body.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return body


def fix_spacing(text: str, cfg, log=None) -> str:
    """공백만 교정한 텍스트. LLM 실패·불일치 시에도 원문 문자는 보존된다."""
    if not text.strip():
        return text
    if not bool(cfg.get("postprocess", "spacing_fix", True)):
        return text

    total = len(_non_space(text))
    limit = int(cfg.get("postprocess", "max_total_chars", 100000))
    if total > limit:
        if log:
            log.info("띄어쓰기 교정 생략(총 %d자 > %d자)", total, limit)
        return text

    chunks = _split_chunks(text, int(cfg.get("postprocess", "chunk_chars", 3000)))
    out: list[str] = []
    exact = partial = 0

    for chunk in chunks:
        fixed = _clean_output(_post(cfg, chunk) or "")
        if not fixed:
            out.append(chunk)
        elif _non_space(fixed) == _non_space(chunk):
            out.append(fixed)
            exact += 1
        else:
            out.append(_apply_spacing_only(chunk, fixed))   # 문자 고정, 공백만 이식
            partial += 1

    if log:
        log.debug("띄어쓰기 교정 %d/%d 청크 (완전 %d, 부분 %d, %d자)",
                  exact + partial, len(chunks), exact, partial, total)
    return "\n\n".join(out)
