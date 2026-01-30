"""Matching utilities for vendor tagging."""

from typing import Iterable, Optional

try:
    from rapidfuzz import fuzz, process  # type: ignore

    _RAPIDFUZZ = True
except Exception:  # pragma: no cover - optional
    process = None
    fuzz = None
    _RAPIDFUZZ = False

from difflib import get_close_matches


def match_vendor(
    name: str,
    master: Iterable[str],
    threshold: int = 80,
    use_rapidfuzz: Optional[bool] = None,
) -> str:
    """Match a sheet name to the best vendor from master list.

    - If RapidFuzz is available and use_rapidfuzz is not False, uses RapidFuzz partial_ratio.
    - Otherwise falls back to difflib.get_close_matches.
    - Returns the matched vendor string or empty string if none found.
    """
    master_list = list(master)
    if not name or not master_list:
        return ""

    # Decide whether to use RapidFuzz
    if use_rapidfuzz is None:
        use_rapidfuzz = _RAPIDFUZZ

    # RapidFuzz path
    if use_rapidfuzz and process and fuzz:
        match = process.extractOne(name, master_list, scorer=fuzz.partial_ratio)
        if match and match[1] >= threshold:
            return match[0]
        return ""

    # difflib fallback
    # difflib's cutoff is between 0 and 1
    cutoff = max(0.0, min(1.0, threshold / 100.0))
    matches = get_close_matches(name, master_list, n=1, cutoff=cutoff)
    return matches[0] if matches else ""
