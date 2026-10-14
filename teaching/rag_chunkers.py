"""Python chunkers mirroring the Chunking Lab UI (for PDF generation)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Literal

ChunkStrategy = Literal[
    "fixed-size", "overlap", "recursive", "semantic", "parent-child", "proposition"
]

SAMPLE_DOCUMENTS = [
    {
        "id": "employee_handbook",
        "title": "Employee Handbook",
        "description": "Structured policy doc with headings — best for recursive and parent–child chunking.",
        "content": """# Employee Handbook

## Remote Work Policy
Employees may work remotely up to three days per week. Managers must approve schedules by Friday. Equipment stipends are $500 per year. Security training is mandatory before VPN access is granted.

## Leave Policy
Full-time employees receive 20 days of paid leave per year. Leave requests must be submitted at least two weeks in advance. Unused leave rolls over up to five days into the next calendar year.

## Expense Reimbursement
Receipts are required for expenses over $25. Meal reimbursements are capped at $75 per day while traveling. Submit expense reports within 30 days of purchase.""",
    },
    {
        "id": "benefits_policy",
        "title": "Benefits Policy",
        "description": "Dense paragraph with multiple facts — best for proposition (atomic) chunking.",
        "content": """Acme Health Plan Summary

The Acme Plan covers dental after a six-month waiting period and vision after ninety days for full-time staff. Part-time employees are eligible for vision only after one hundred eighty days. Dental coverage is not available to part-time employees. Emergency room visits require a $150 copay. Prescription drugs are covered with a $10 generic copay.""",
    },
    {
        "id": "company_update",
        "title": "Company Update (mixed topics)",
        "description": "One article with several topics and no clear headings — compare fixed-size vs semantic.",
        "content": """Internal Company Update — March 2026

We shipped version 2.0 last week with offline sync and faster search. Customers have been asking for offline mode for over a year, and early feedback has been very positive.

Starting May 1, the Pro plan will be $29 per month instead of $39. Existing customers keep their current price until their contract renews. The Team plan pricing is unchanged at $99 per month.

We are hiring two backend engineers and one designer for the platform team. Applications close on April 15. Referrals receive a $2,000 bonus after the new hire completes 90 days.""",
    },
    {
        "id": "security_faq",
        "title": "Security FAQ (flat text)",
        "description": "Flat Q&A without headings — good for fixed-size and overlap demos.",
        "content": """Security FAQ

Q: Do I need VPN for remote work?
A: Yes. VPN is required for all remote access to internal systems. Security training must be completed before VPN credentials are issued.

Q: How often should I change my password?
A: Passwords must be rotated every 90 days. Use at least 12 characters with mixed case, numbers, and symbols.

Q: What if I lose my company laptop?
A: Report the loss to IT within one hour. IT will remotely wipe the device and issue a replacement within two business days. You may be liable for unreported losses after 24 hours.""",
    },
]

STRATEGY_INFO = {
    "fixed-size": ("Fixed-size", "Split every N characters (breaks on word boundaries)."),
    "overlap": ("Overlap", "Sliding window with shared text between adjacent chunks."),
    "recursive": ("Recursive", "Prefer headings → paragraphs → sentences → characters."),
    "semantic": ("Semantic", "Split when sentence similarity drops (TF-IDF vectors in-browser)."),
    "parent-child": (
        "Parent–child",
        "Section = parent (stored, not embedded). Sentences = children (embedded).",
    ),
    "proposition": ("Proposition", "One atomic fact per sentence, rewritten to stand alone."),
}

# UI-matching highlight colors — 40% opacity (#RRGGBB66)
CHUNK_BASE_HUES = [
    "#0f6e6a",
    "#d9b48f",
    "#6b8cae",
    "#c47d5a",
    "#7a6b9e",
    "#4a8f6a",
    "#b85c5c",
    "#5c8ab8",
    "#9e7b4a",
    "#5a7a9e",
]
CHUNK_COLORS = [f"{h}66" for h in CHUNK_BASE_HUES]

CHUNK_BORDERS = [
    "#0f6e6a",
    "#b8860b",
    "#4a6fa5",
    "#c47d5a",
    "#7a6b9e",
    "#4a8f6a",
    "#b85c5c",
    "#5c8ab8",
]

_counter = 0


@dataclass
class Chunk:
    id: str
    text: str
    start: int
    end: int
    strategy: str
    role: str | None = None
    parent_id: str | None = None
    split_level: str | None = None
    embedded: bool = True
    label: str | None = None
    similarity_to_prev: float | None = None
    char_count: int = 0


def _reset():
    global _counter
    _counter = 0


def _cid(prefix: str) -> str:
    global _counter
    _counter += 1
    return f"{prefix}_{_counter}"


def split_sentences(text: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for m in re.finditer(r"[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$", text):
        s = m.group(0)
        if s.strip():
            out.append((s, m.start(), m.end()))
    return out


def split_paragraphs(text: str) -> list[tuple[str, int, int]]:
    parts = re.split(r"(\n\s*\n+)", text)
    out: list[tuple[str, int, int]] = []
    offset = 0
    for part in parts:
        if part.strip():
            out.append((part, offset, offset + len(part)))
        offset += len(part)
    return out


def split_by_headings(text: str) -> list[tuple[str, str, int, int]]:
    matches = list(re.finditer(r"^(#{1,3}\s+.+)$", text, re.MULTILINE))
    if not matches:
        return [("", text, 0, len(text))]
    sections: list[tuple[str, str, int, int]] = []
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.append(("(intro)", preamble, 0, matches[0].start()))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        lines = block.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else block
        sections.append((heading, body, start, end))
    return sections


def fixed_size_chunks(text: str, size: int = 280) -> list[Chunk]:
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            sp = text[start:end].rfind(" ")
            if sp > size * 0.5:
                end = start + sp
        ct = text[start:end]
        if ct.strip():
            chunks.append(
                Chunk(
                    _cid("fixed"),
                    ct.strip(),
                    start,
                    end,
                    "fixed-size",
                    split_level="character",
                    char_count=len(ct.strip()),
                )
            )
        if end >= len(text):
            break
        start = end
    return chunks


def overlap_chunks(text: str, size: int = 280, overlap_pct: int = 15) -> list[Chunk]:
    overlap = int(size * overlap_pct / 100)
    step = max(size - overlap, 1)
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            sp = text[start:end].rfind(" ")
            if sp > size * 0.5:
                end = start + sp
        ct = text[start:end]
        if ct.strip():
            chunks.append(
                Chunk(
                    _cid("overlap"),
                    ct.strip(),
                    start,
                    end,
                    "overlap",
                    split_level="character",
                    label=f"overlap {overlap} chars with previous" if overlap else None,
                    char_count=len(ct.strip()),
                )
            )
        if end >= len(text):
            break
        start += step
    return chunks


def recursive_chunks(text: str, max_size: int = 280) -> list[Chunk]:
    chunks: list[Chunk] = []

    def add(ct: str, start: int, end: int, level: str, label: str | None = None):
        if not ct.strip():
            return
        if len(ct) <= max_size:
            chunks.append(
                Chunk(
                    _cid("recursive"),
                    ct.strip(),
                    start,
                    end,
                    "recursive",
                    split_level=level,
                    label=label,
                    char_count=len(ct.strip()),
                )
            )
            return
        paras = split_paragraphs(ct)
        if level != "paragraph" and len(paras) > 1:
            for p, ps, pe in paras:
                add(p, start + ps, start + pe, "paragraph")
            return
        sents = split_sentences(ct)
        if level != "sentence" and len(sents) > 1:
            for s, ss, se in sents:
                add(s, start + ss, start + se, "sentence")
            return
        for c in fixed_size_chunks(ct, max_size):
            chunks.append(
                Chunk(
                    c.id,
                    c.text,
                    start + c.start,
                    start + c.end,
                    "recursive",
                    split_level="character",
                    char_count=c.char_count,
                )
            )

    for heading, body, start, end in split_by_headings(text):
        section = f"{heading}\n{body}".strip() if heading and heading != "(intro)" else body
        add(section, start, end, "heading", heading or None)
    return chunks


STOP_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was",
    "one", "our", "out", "day", "has", "him", "his", "how", "its", "may", "new", "now",
    "this", "from", "they", "have", "been", "will", "your", "than", "them", "into",
    "only", "over", "such", "after", "most", "also", "when", "what", "were", "there",
}


def _tokenize(t: str) -> list[str]:
    return [
        w
        for w in re.sub(r"[^a-z0-9\s]", " ", t.lower()).split()
        if len(w) > 2 and w not in STOP_WORDS
    ]


def _tfidf(sentences: list[str]) -> list[dict[str, float]]:
    docs = [_tokenize(s) for s in sentences]
    df: dict[str, int] = {}
    for doc in docs:
        for w in set(doc):
            df[w] = df.get(w, 0) + 1
    n = len(docs)
    vecs: list[dict[str, float]] = []
    for doc in docs:
        tf: dict[str, int] = {}
        for w in doc:
            tf[w] = tf.get(w, 0) + 1
        vec: dict[str, float] = {}
        ln = max(len(doc), 1)
        for w, c in tf.items():
            idf = math.log((n + 1) / (df.get(w, 0) + 1)) + 1
            vec[w] = (c / ln) * idf
        vecs.append(vec)
    return vecs


def _cos(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a[k] * b[k] for k in a if k in b)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def semantic_chunks(text: str, threshold: float = 0.25) -> list[Chunk]:
    sents = split_sentences(text)
    if not sents:
        return []
    vecs = _tfidf([s[0] for s in sents])
    chunks: list[Chunk] = []
    gs = 0
    for i in range(1, len(sents) + 1):
        split = i == len(sents)
        if not split:
            split = _cos(vecs[i - 1], vecs[i]) < threshold
        if split:
            group = sents[gs:i]
            start, end = group[0][1], group[-1][2]
            ct = text[start:end]
            sim = _cos(vecs[gs - 1], vecs[gs]) if gs > 0 else None
            label = "topic start" if gs == 0 else f"topic break · sim {sim:.2f} < {threshold:.2f}"
            chunks.append(
                Chunk(
                    _cid("semantic"),
                    ct.strip(),
                    start,
                    end,
                    "semantic",
                    split_level="sentence",
                    label=label,
                    similarity_to_prev=sim,
                    char_count=len(ct.strip()),
                )
            )
            gs = i
    return chunks


def parent_child_chunks(text: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for idx, (heading, body, start, end) in enumerate(split_by_headings(text)):
        pid = f"parent_{idx + 1}"
        section = f"{heading}\n{body}".strip() if heading and heading != "(intro)" else body
        chunks.append(
            Chunk(
                pid,
                section,
                start,
                end,
                "parent-child",
                role="parent",
                parent_id=pid,
                split_level="heading",
                embedded=False,
                label=heading or "(intro)",
                char_count=len(section),
            )
        )
        body_start = start + len(heading) + 1 if heading and heading != "(intro)" else start
        for sent, ss, se in split_sentences(body or section):
            abs_s = body_start + ss if heading and heading != "(intro)" else start + ss
            abs_e = body_start + se if heading and heading != "(intro)" else start + se
            chunks.append(
                Chunk(
                    _cid("child"),
                    sent.strip(),
                    abs_s,
                    abs_e,
                    "parent-child",
                    role="child",
                    parent_id=pid,
                    split_level="sentence",
                    label=f"→ {pid}",
                    char_count=len(sent.strip()),
                )
            )
    return chunks


def proposition_chunks(text: str, subject: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for i, (sent, start, end) in enumerate(split_sentences(text)):
        st = sent.strip()
        vague = bool(re.search(r"\b(it|this|that|they|these|those|the above)\b", st, re.I))
        subj = subject.split()[0].lower()
        standalone = st
        if vague or (subj not in st.lower() and len(st) < 120):
            standalone = f"{subject}: {st[0].lower()}{st[1:]}" if st else st
        chunks.append(
            Chunk(
                _cid("prop"),
                standalone,
                start,
                end,
                "proposition",
                split_level="sentence",
                label=f"atomic fact {i + 1}",
                char_count=len(standalone),
            )
        )
    return chunks


def chunk_document(
    text: str,
    strategy: str,
    *,
    chunk_size: int = 280,
    overlap_pct: int = 15,
    similarity_threshold: float = 0.25,
    subject: str = "This policy",
) -> list[Chunk]:
    _reset()
    if strategy == "fixed-size":
        return fixed_size_chunks(text, chunk_size)
    if strategy == "overlap":
        return overlap_chunks(text, chunk_size, overlap_pct)
    if strategy == "recursive":
        return recursive_chunks(text, chunk_size)
    if strategy == "semantic":
        return semantic_chunks(text, similarity_threshold)
    if strategy == "parent-child":
        return parent_child_chunks(text)
    if strategy == "proposition":
        return proposition_chunks(text, subject)
    return []


# Shorter excerpts for printable side-by-side pages (one page per example)
PDF_EXCERPTS: dict[str, str] = {
    "employee_handbook": """## Remote Work Policy
Employees may work remotely up to three days per week. Managers must approve schedules by Friday. Equipment stipends are $500 per year. Security training is mandatory before VPN access is granted.""",
    "benefits_policy": """The Acme Plan covers dental after a six-month waiting period and vision after ninety days for full-time staff. Part-time employees are eligible for vision only after one hundred eighty days. Dental coverage is not available to part-time employees.""",
    "company_update": SAMPLE_DOCUMENTS[2]["content"],
    "security_faq": """Q: Do I need VPN for remote work?
A: Yes. VPN is required for all remote access to internal systems. Security training must be completed before VPN credentials are issued.

Q: How often should I change my password?
A: Passwords must be rotated every 90 days. Use at least 12 characters with mixed case, numbers, and symbols.""",
}
