#!/usr/bin/env python3
"""Validate and search a local question bank without executing its contents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence


STRING_FIELDS = (
    "id", "course", "question", "method", "difficulty", "answer",
    "explanation", "source",
)


class InputError(ValueError):
    """Invalid command-line input or invalid question-bank data."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InputError(message)


def validate_bank(data: Any) -> list[dict[str, Any]]:
    """Validate every record, including records that would not match a search."""
    if not isinstance(data, list):
        raise InputError("题库必须是 JSON 数组。")
    ids: set[str] = set()
    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            raise InputError(f"第 {index} 条题目必须是 JSON 对象。")
        for field in STRING_FIELDS:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                raise InputError(f"第 {index} 条题目的 {field} 必须是非空字符串。")
        tags = record.get("knowledge_ids")
        if (
            not isinstance(tags, list)
            or not tags
            or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
        ):
            raise InputError(f"第 {index} 条题目的 knowledge_ids 必须是非空字符串数组。")
        if record["id"] in ids:
            raise InputError(f"题库包含重复 id：{record['id']}")
        ids.add(record["id"])
    return data


def load_bank(path: str | Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"无法读取 UTF-8 JSON 题库：{exc}") from exc
    return validate_bank(data)


def search_questions(
    bank: list[dict[str, Any]],
    *,
    course: str | None = None,
    knowledge_ids: Sequence[str] = (),
    exclude_ids: Sequence[str] = (),
    query: str | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    """Filter, stably rank, and deduplicate questions in an already validated bank."""
    if not 1 <= limit <= 20:
        raise InputError("limit 必须在 1 到 20 之间。")
    if course is not None and (not isinstance(course, str) or not course.strip()):
        raise InputError("course 必须是非空字符串。")
    if query is not None and (not isinstance(query, str) or not query.strip()):
        raise InputError("query 必须是非空字符串。")
    for label, values in (("knowledge-id", knowledge_ids), ("exclude-id", exclude_ids)):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise InputError(f"{label} 必须是非空字符串。")
    if course is None and not knowledge_ids and query is None:
        raise InputError("至少提供 course、knowledge-id 或 query 之一。")

    tags = set(knowledge_ids)
    excluded = set(exclude_ids)
    tokens = set(query.casefold().split()) if query else set()
    ranked: list[tuple[int, dict[str, Any]]] = []
    for record in bank:
        if course is not None and record["course"] != course:
            continue
        if tags and not tags.intersection(record["knowledge_ids"]):
            continue
        if record["id"] in excluded:
            continue
        text = " ".join((record["question"], record["method"], *record["knowledge_ids"])).casefold()
        hits = sum(token in text for token in tokens)
        if tokens and not hits:
            continue
        ranked.append((hits, record))
    if tokens:
        ranked.sort(key=lambda item: -item[0])

    unique: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    for _, record in ranked:
        question_key = "".join(record["question"].split())
        if question_key not in seen_questions:
            seen_questions.add(question_key)
            unique.append(record)

    warnings = []
    if len(unique) < limit:
        warnings.append(f"仅找到 {len(unique)} 道匹配且题面不重复的题目，少于请求的 {limit} 道；未补凑题目。")
    return {
        "status": "ok",
        "results": unique[:limit],
        "total_matches": len(unique),
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description="检索本地 UTF-8 JSON 题库；不联网、不修改题库。")
    parser.add_argument("--bank", required=True, help="题库 JSON 文件路径")
    parser.add_argument("--course", help="精确匹配课程名称")
    parser.add_argument("--knowledge-id", action="append", default=[], help="考点编号；可重复，至少匹配一个")
    parser.add_argument("--exclude-id", action="append", default=[], help="排除题目编号；可重复")
    parser.add_argument("--query", help="按空白分词，在题面、方法与考点编号中匹配")
    parser.add_argument("--limit", type=int, default=3, help="最多返回题数，1..20，默认 3")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        bank = load_bank(args.bank)
        result = search_questions(
            bank,
            course=args.course,
            knowledge_ids=args.knowledge_id,
            exclude_ids=args.exclude_id,
            query=args.query,
            limit=args.limit,
        )
        code = 0
    except InputError as exc:
        result = {"status": "error", "error": str(exc)}
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
