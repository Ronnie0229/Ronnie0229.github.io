from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = ROOT / "assets" / "admin" / "tag-rules.json"
INVALID_TAG_CHARACTERS = re.compile(r"[,，、;；:：\n\r\t\[\]{}<>/\\|\"']")


class TagPipelineError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TagPipelineResult:
    tags: list[str]
    evidence: list[dict[str, str]]
    rules_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tags": self.tags,
            "evidence": self.evidence,
            "rules_version": self.rules_version,
        }


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or ""))).strip()


def lookup_key(value: Any) -> str:
    return normalize_text(value).lower()


def parse_manual_tags(value: str | None) -> list[str]:
    if value is None:
        return []
    return re.split(r"[,，、]", value)


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise TagPipelineError("RULES_INVALID", f"Tag rules field must be a list: {field}")
    return value


def validate_rules(rules: dict[str, Any]) -> None:
    if not isinstance(rules, dict) or rules.get("schema_version") != "1.0":
        raise TagPipelineError("RULES_INVALID", "Unsupported or missing tag rules schema_version.")
    if not normalize_text(rules.get("rules_version")):
        raise TagPipelineError("RULES_INVALID", "Tag rules_version is required.")
    limits = rules.get("limits")
    if not isinstance(limits, dict):
        raise TagPipelineError("RULES_INVALID", "Tag rules limits object is required.")
    if limits.get("min_tags") != 2 or limits.get("max_tags") != 6:
        raise TagPipelineError("RULES_INVALID", "Tag rules must enforce the approved 2-6 range.")
    if not isinstance(limits.get("max_tag_length"), int) or limits["max_tag_length"] < 1:
        raise TagPipelineError("RULES_INVALID", "Tag max_tag_length must be a positive integer.")
    _require_list(rules.get("generic_tags"), "generic_tags")
    _require_list(rules.get("ambiguous_tags"), "ambiguous_tags")
    _require_list(rules.get("admin_presets"), "admin_presets")
    books = _require_list(rules.get("books"), "books")
    tags = _require_list(rules.get("tags"), "tags")
    canonicals: set[str] = set()
    aliases: set[str] = set()
    for group_name, entries in (("books", books), ("tags", tags)):
        for entry in entries:
            if not isinstance(entry, dict):
                raise TagPipelineError("RULES_INVALID", f"Invalid {group_name} entry.")
            canonical = normalize_text(entry.get("canonical"))
            if not canonical or canonical in canonicals:
                raise TagPipelineError("RULES_INVALID", f"Missing or duplicate canonical tag: {canonical!r}")
            canonicals.add(canonical)
            for alias in [canonical, *_require_list(entry.get("aliases", []), f"{canonical}.aliases")]:
                key = lookup_key(alias)
                if not key or key in aliases:
                    raise TagPipelineError("RULES_INVALID", f"Duplicate tag alias: {alias!r}")
                aliases.add(key)
            if group_name == "tags":
                if entry.get("kind") not in {"person", "place", "event", "theme"}:
                    raise TagPipelineError("RULES_INVALID", f"Invalid tag kind for {canonical}.")
                _require_list(entry.get("inference_terms", []), f"{canonical}.inference_terms")


@lru_cache(maxsize=4)
def load_rules(path: str | Path = DEFAULT_RULES_PATH) -> dict[str, Any]:
    rules_path = Path(path)
    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TagPipelineError("RULES_INVALID", f"Unable to load tag rules: {rules_path}") from exc
    validate_rules(rules)
    return rules


def _alias_map(rules: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for entry in rules["books"]:
        canonical = normalize_text(entry["canonical"])
        aliases[lookup_key(canonical)] = canonical
    for entry in rules["tags"]:
        canonical = normalize_text(entry["canonical"])
        for value in [canonical, *entry.get("aliases", [])]:
            aliases[lookup_key(value)] = canonical
    return aliases


def _canonical_books(rules: dict[str, Any]) -> set[str]:
    return {normalize_text(entry["canonical"]) for entry in rules["books"]}


def _scripture_books(scripture: str, rules: dict[str, Any]) -> list[str]:
    haystack = lookup_key(scripture)
    matches: list[tuple[int, int, int, str]] = []
    for order, entry in enumerate(rules["books"]):
        canonical = normalize_text(entry["canonical"])
        for value in [canonical, *entry.get("aliases", [])]:
            term = lookup_key(value)
            if not term:
                continue
            for match in re.finditer(re.escape(term), haystack):
                suffix = haystack[match.end():]
                if not re.match(r"^\.?\s*第?\s*\d", suffix):
                    continue
                matches.append((match.start(), -len(term), order, canonical))
    matches.sort()
    selected: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for start, negative_length, _order, canonical in matches:
        end = start - negative_length
        if canonical in seen or any(start < used_end and end > used_start for used_start, used_end, _ in selected):
            continue
        selected.append((start, end, canonical))
        seen.add(canonical)
    selected.sort()
    return [canonical for _start, _end, canonical in selected]


def _rule_tags(title: str, subtitle: str, rules: dict[str, Any]) -> list[str]:
    haystack = lookup_key(" ".join(value for value in (title, subtitle) if value))
    if not haystack:
        return []
    generated: list[str] = []
    for entry in rules["tags"]:
        if any(lookup_key(term) in haystack for term in entry.get("inference_terms", []) if lookup_key(term)):
            generated.append(normalize_text(entry["canonical"]))
    return generated


def _validate_tag(tag: str, rules: dict[str, Any]) -> None:
    if not tag:
        raise TagPipelineError("TAG_EMPTY", "标签不能为空。")
    if len(tag) > rules["limits"]["max_tag_length"]:
        raise TagPipelineError("TAG_TOO_LONG", f"标签过长（最多 {rules['limits']['max_tag_length']} 个字符）：{tag}")
    if INVALID_TAG_CHARACTERS.search(tag):
        raise TagPipelineError("TAG_INVALID_CHARACTER", f"标签包含非法字符：{tag}")


def build_tags(
    *,
    title: str,
    scripture: str = "",
    manual_tags: Iterable[str] | None = None,
    subtitle: str = "",
    category: str = "",
    author: str = "",
    rules: dict[str, Any] | None = None,
) -> TagPipelineResult:
    active_rules = rules or load_rules()
    validate_rules(active_rules)
    aliases = _alias_map(active_rules)
    generic = {lookup_key(tag) for tag in active_rules["generic_tags"]}
    ambiguous = {lookup_key(tag) for tag in active_rules["ambiguous_tags"]}
    books = _canonical_books(active_rules)
    context = {
        lookup_key(aliases.get(lookup_key(value), normalize_text(value)))
        for value in (category, author)
        if normalize_text(value)
    }

    candidates: list[tuple[str, str]] = []
    candidates.extend((tag, "scripture") for tag in _scripture_books(scripture, active_rules))
    candidates.extend((tag, "rule") for tag in _rule_tags(title, subtitle, active_rules))

    for raw_tag in manual_tags or []:
        normalized = normalize_text(raw_tag)
        if not normalized:
            raise TagPipelineError("TAG_EMPTY", "人工标签不能为空。")
        key = lookup_key(normalized)
        if key in ambiguous:
            raise TagPipelineError("TAG_AMBIGUOUS", f"标签“{normalized}”存在人物、民族或国家歧义，请改用明确标签。")
        candidates.append((aliases.get(key, normalized), "manual"))

    output: list[str] = []
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_tag, source in candidates:
        normalized = normalize_text(raw_tag)
        canonical = aliases.get(lookup_key(normalized), normalized)
        _validate_tag(canonical, active_rules)
        key = lookup_key(canonical)
        if key in generic:
            raise TagPipelineError("TAG_GENERIC", f"请移除通用标签：{canonical}。改用核心人物、地点、事件或主题标签。")
        if key in seen:
            continue
        seen.add(key)
        output.append(canonical)
        evidence.append({"tag": canonical, "source": source})

    precise_non_book = [tag for tag in output if tag not in books and lookup_key(tag) not in context]
    context_tags = [tag for tag in output if lookup_key(tag) in context]
    if context_tags and not precise_non_book:
        raise TagPipelineError("TAG_CONTEXT_ONLY", "标签不能只由书卷、分类、内容类型或作者/讲员构成。请补充精准主题标签。")

    minimum = active_rules["limits"]["min_tags"]
    maximum = active_rules["limits"]["max_tags"]
    if len(output) < minimum:
        raise TagPipelineError(
            "TAG_COUNT_TOO_LOW",
            f"无法生成足够精准的标签：当前 {len(output)} 个，至少需要 {minimum} 个。请补充人物、地点、事件或主题标签。",
        )
    if len(output) > maximum:
        raise TagPipelineError(
            "TAG_COUNT_TOO_HIGH",
            f"标签规范化后共有 {len(output)} 个，最多允许 {maximum} 个：{'、'.join(output)}。请减少人工标签。",
        )

    return TagPipelineResult(output, evidence, normalize_text(active_rules["rules_version"]))
