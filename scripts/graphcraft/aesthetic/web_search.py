"""Lightweight web search for aesthetic research (stdlib-first)."""

from __future__ import annotations

import html
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable, Iterable

USER_AGENT = "GraphCraft/2.2 (+https://github.com/MertCapkin/GraphCraft; aesthetic-research)"


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    query: str = ""


_OFFLINE_FIXTURES: dict[str, list[SearchResult]] = {
    "mobile": [
        SearchResult(
            title="Mobile UI card layout patterns",
            url="https://example.com/mobile-card-layout",
            snippet="Card grids, bottom navigation, and safe-area padding improve scanability.",
            query="mobile",
        ),
        SearchResult(
            title="Typography hierarchy for mobile apps",
            url="https://example.com/mobile-typography",
            snippet="Use clear heading scale, 16px body minimum, and high contrast text.",
            query="mobile",
        ),
        SearchResult(
            title="Warm minimal color palettes",
            url="https://example.com/warm-palettes",
            snippet="Friendly warm accents with neutral backgrounds balance marketing and readability.",
            query="mobile",
        ),
    ],
}


def _offline_results(query: str, max_results: int) -> list[SearchResult]:
    base = _OFFLINE_FIXTURES.get("mobile", [])
    out: list[SearchResult] = []
    for item in base[:max_results]:
        out.append(
            SearchResult(
                title=item.title,
                url=item.url,
                snippet=item.snippet,
                query=query,
            )
        )
    return out


def _strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def parse_ddg_html(html_text: str, query: str, *, max_results: int = 3) -> list[SearchResult]:
    """Parse DuckDuckGo HTML lite results page."""
    results: list[SearchResult] = []
    blocks = re.split(r'<div class="result\s+results_links[^"]*">', html_text)
    for block in blocks[1:]:
        link_match = re.search(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            block,
            re.DOTALL,
        )
        if not link_match:
            continue
        url = html.unescape(link_match.group(1))
        title = _strip_tags(link_match.group(2))
        snippet_match = re.search(
            r'class="result__snippet"[^>]*>(.*?)</(?:a|td|div)>',
            block,
            re.DOTALL,
        )
        snippet = _strip_tags(snippet_match.group(1)) if snippet_match else ""
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=snippet, query=query))
        if len(results) >= max_results:
            break
    return results


def search_duckduckgo(query: str, *, max_results: int = 3, timeout: float = 15.0) -> list[SearchResult]:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return parse_ddg_html(body, query, max_results=max_results)


def search_web(
    query: str,
    *,
    max_results: int = 3,
    offline: bool = False,
    provider: Callable[[str, int], list[SearchResult]] | None = None,
) -> list[SearchResult]:
    if offline or os.environ.get("GRAPHCRAFT_RESEARCH_OFFLINE") == "1":
        return _offline_results(query, max_results)
    if provider is not None:
        return provider(query, max_results)
    try:
        return search_duckduckgo(query, max_results=max_results)
    except (urllib.error.URLError, TimeoutError, OSError):
        return []


def search_queries(
    queries: Iterable[str],
    *,
    max_results_per_query: int = 3,
    offline: bool = False,
    provider: Callable[[str, int], list[SearchResult]] | None = None,
) -> list[SearchResult]:
    seen_urls: set[str] = set()
    combined: list[SearchResult] = []
    for query in queries:
        for item in search_web(
            query,
            max_results=max_results_per_query,
            offline=offline,
            provider=provider,
        ):
            if item.url in seen_urls:
                continue
            seen_urls.add(item.url)
            combined.append(item)
    return combined


def doctor_search(*, offline: bool = False) -> list[str]:
    issues: list[str] = []
    if offline or os.environ.get("GRAPHCRAFT_RESEARCH_OFFLINE") == "1":
        return issues
    try:
        results = search_duckduckgo("mobile ui design patterns", max_results=1, timeout=10.0)
        if not results:
            issues.append("Web search returned no results (DuckDuckGo HTML may have changed)")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        issues.append(f"Web search unreachable: {exc}")
    return issues
