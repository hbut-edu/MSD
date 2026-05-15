#!/usr/bin/env python3
"""Collect public Genshin redeem-code candidates from classroom-approved URLs.

The script is intentionally conservative:
- it only fetches URLs supplied by students or teachers;
- it does not log in, solve captchas, bypass anti-bot controls, or call private APIs;
- it treats extracted codes as candidates until a human checks the source.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


CODE_PATTERN = re.compile(r"\b[A-Z0-9]{8,20}\b")
TIME_HINT_PATTERN = re.compile(
    r"(?:有效期|生效|截止|过期|失效|兑换时间|valid|expires|until|before)[^。\n.]{0,80}",
    re.IGNORECASE,
)
CHINESE_DATE_PATTERN = re.compile(
    r"(?:(?P<year>20\d{2})\s*年)?\s*(?P<month>\d{1,2})\s*月\s*"
    r"(?P<day>\d{1,2})\s*[日号]?\s*(?:(?P<hour>\d{1,2})[:：](?P<minute>\d{2}))?"
)
ISO_DATE_PATTERN = re.compile(
    r"(?P<year>20\d{2})[-/](?P<month>\d{1,2})[-/](?P<day>\d{1,2})"
    r"(?:[ T](?P<hour>\d{1,2})[:：](?P<minute>\d{2}))?"
)
CONTEXT_KEYWORDS = ("兑换", "礼包", "激活码", "兑换码", "code", "redeem", "gift")
SOURCE_CONFIDENCE = {
    "official_site": "high",
    "official_community": "high",
    "official_social": "high",
    "third_party": "low",
}


class TextExtractor(HTMLParser):
    """Extract visible-ish text from a simple HTML page."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            cleaned = " ".join(data.split())
            if cleaned:
                self.parts.append(cleaned)

    def text(self) -> str:
        return "\n".join(self.parts)


@dataclass
class CodeRecord:
    code: str
    source_name: str
    source_type: str
    source_url: str
    published_at: str
    valid_from: str
    valid_until: str
    status: str
    confidence: str
    captured_at: str
    evidence_text: str
    time_evidence: list[str]


def fetch_text(url: str) -> str:
    """Fetch one public URL and return extracted page text."""
    request = Request(url, headers={"User-Agent": "MSD-course-skill-lab/1.0"})
    with urlopen(request, timeout=20) as response:
        raw = response.read()
        content_type = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(content_type, errors="replace")
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def evidence_window(text: str, start: int, end: int, width: int = 80) -> str:
    """Return a short text window around an extracted candidate."""
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].split())


def is_plausible_code(code: str, evidence: str) -> bool:
    """Filter obvious false positives while keeping known letter-only gift codes."""
    if len(set(code)) <= 2:
        return False
    if any(keyword.lower() in evidence.lower() for keyword in CONTEXT_KEYWORDS):
        return True
    return bool(re.search(r"\d", code)) and len(code) >= 10


def parse_date(raw: str, now: datetime) -> str:
    """Parse common Chinese or ISO-like date mentions into ISO 8601 when possible."""
    for pattern in (CHINESE_DATE_PATTERN, ISO_DATE_PATTERN):
        match = pattern.search(raw)
        if not match:
            continue
        year = int(match.group("year") or now.year)
        month = int(match.group("month"))
        day = int(match.group("day"))
        hour = int(match.group("hour") or 23)
        minute = int(match.group("minute") or 59)
        try:
            return datetime(year, month, day, hour, minute, tzinfo=now.tzinfo).isoformat()
        except ValueError:
            return "unknown"
    return "unknown"


def extract_time_mentions(text: str) -> list[str]:
    """Collect raw time-related snippets for human verification."""
    return [" ".join(match.group(0).split()) for match in TIME_HINT_PATTERN.finditer(text)]


def choose_valid_until(mentions: list[str], now: datetime) -> str:
    """Pick the first expiry-like time mention that can be parsed."""
    expiry_keywords = ("至", "截止", "过期", "失效", "前", "expires", "until", "before")
    for mention in mentions:
        if any(keyword.lower() in mention.lower() for keyword in expiry_keywords):
            parsed = parse_date(mention, now)
            if parsed != "unknown":
                return parsed
    return "unknown"


def status_from_valid_until(valid_until: str, now: datetime) -> str:
    """Classify a candidate based on its parsed expiry time."""
    if valid_until == "unknown":
        return "unknown"
    try:
        expiry = datetime.fromisoformat(valid_until)
    except ValueError:
        return "unknown"
    return "expired" if expiry < now else "active_candidate"


def extract_records(
    text: str,
    source_name: str,
    source_type: str,
    source_url: str,
    now: datetime,
) -> list[CodeRecord]:
    """Extract code candidates and attach source/time metadata."""
    mentions = extract_time_mentions(text)
    valid_until = choose_valid_until(mentions, now)
    status = status_from_valid_until(valid_until, now)
    records: list[CodeRecord] = []
    seen: set[str] = set()

    for match in CODE_PATTERN.finditer(text):
        code = match.group(0)
        evidence = evidence_window(text, match.start(), match.end())
        if code in seen or not is_plausible_code(code, evidence):
            continue
        seen.add(code)
        records.append(
            CodeRecord(
                code=code,
                source_name=source_name,
                source_type=source_type,
                source_url=source_url,
                published_at="unknown",
                valid_from="unknown",
                valid_until=valid_until,
                status=status,
                confidence=SOURCE_CONFIDENCE.get(source_type, "medium"),
                captured_at=now.isoformat(),
                evidence_text=evidence,
                time_evidence=mentions[:5],
            )
        )
    return records


def main() -> None:
    """Fetch URLs and write JSON code-candidate records."""
    parser = argparse.ArgumentParser(description="Collect public Genshin code candidates.")
    parser.add_argument("--url", action="append", required=True, help="Public URL to fetch")
    parser.add_argument("--source-name", required=True, help="Human-readable source name")
    parser.add_argument(
        "--source-type",
        default="third_party",
        choices=["official_site", "official_community", "official_social", "third_party"],
        help="Source trust category",
    )
    parser.add_argument("--output", type=Path, default=Path("crawl_result.json"))
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    args = parser.parse_args()

    now = datetime.now(timezone(timedelta(hours=8)))
    all_records: list[CodeRecord] = []
    errors: list[dict[str, str]] = []

    for index, url in enumerate(args.url):
        if index:
            time.sleep(args.delay)
        try:
            text = fetch_text(url)
            all_records.extend(
                extract_records(text, args.source_name, args.source_type, url, now)
            )
        except Exception as exc:  # noqa: BLE001 - teaching script should report all failures.
            errors.append({"url": url, "error": str(exc)})

    payload = {
        "captured_at": now.isoformat(),
        "records": [asdict(record) for record in all_records],
        "errors": errors,
        "note": "Candidates require source review before being treated as valid redeem codes.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
