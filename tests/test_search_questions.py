"""Question-bank validation and local retrieval tests; no network required."""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "university-review" / "scripts" / "search_questions.py"
EXAMPLE_BANK = ROOT / "skills" / "university-review" / "examples" / "question-bank.json"
SPEC = importlib.util.spec_from_file_location("search_questions", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(search)


def question(qid: str, text: str = "求积分 x dx", **changes):
    record = {
        "id": qid,
        "course": "高等数学",
        "question": text,
        "knowledge_ids": ["CALC.INT.PARTS"],
        "method": "分部积分法",
        "difficulty": "基础",
        "answer": "演示答案",
        "explanation": "演示解析",
        "source": "测试自编题",
    }
    record.update(changes)
    return record


class QuestionSearchTests(unittest.TestCase):
    def test_course_is_exact_and_excludes_other_courses(self):
        bank = [question("a"), question("b", "其他题", course="线性代数")]
        result = search.search_questions(bank, course="高等数学")
        self.assertEqual([row["id"] for row in result["results"]], ["a"])
        self.assertEqual(search.search_questions(bank, course="高等")['total_matches'], 0)

    def test_knowledge_filter_matches_any_requested_tag(self):
        bank = [
            question("a"),
            question("b", "换元题", knowledge_ids=["CALC.INT.SUBSTITUTION"]),
            question("c", "特征值题", knowledge_ids=["LINALG.EIGEN"]),
        ]
        result = search.search_questions(bank, knowledge_ids=["CALC.INT.PARTS", "CALC.INT.SUBSTITUTION"])
        self.assertEqual([row["id"] for row in result["results"]], ["a", "b"])

    def test_deduplicates_question_whitespace_but_preserves_case(self):
        bank = [question("a", "x + X"), question("b", "x\t+\nX"), question("c", "x + x")]
        result = search.search_questions(bank, course="高等数学")
        self.assertEqual([row["id"] for row in result["results"]], ["a", "c"])
        self.assertEqual(result["total_matches"], 2)
        self.assertTrue(result["warnings"])

    def test_exclusions_happen_before_deduplication(self):
        bank = [question("original"), question("copy"), question("third", "不同题")]
        result = search.search_questions(bank, course="高等数学", exclude_ids=["original", "third"])
        self.assertEqual([row["id"] for row in result["results"]], ["copy"])

    def test_chinese_search_ranks_hits_and_keeps_stable_ties(self):
        bank = [
            question("a", "求积分", method="换元"),
            question("b", "求积分，说明分部方法"),
            question("c", "计算积分，使用分部方法"),
            question("d", "求极限", method="夹逼"),
        ]
        result = search.search_questions(bank, query="积分 分部")
        self.assertEqual([row["id"] for row in result["results"]], ["b", "c", "a"])
        self.assertEqual(result["warnings"], [])

    def test_query_matches_method_and_casefolded_tags(self):
        bank = [question("a", "某道题"), question("b", "另一题", method="换元", knowledge_ids=["OTHER"])]
        self.assertEqual(search.search_questions(bank, query="分部")['total_matches'], 1)
        self.assertEqual(search.search_questions(bank, query="calc.int.parts")['total_matches'], 1)

    def test_no_query_keeps_bank_order_and_total_counts_before_limit(self):
        bank = [question(str(index), f"题目{index}") for index in range(4)]
        result = search.search_questions(bank, course="高等数学", limit=2)
        self.assertEqual([row["id"] for row in result["results"]], ["0", "1"])
        self.assertEqual(result["total_matches"], 4)

    def test_no_matches_is_success_with_warning(self):
        result = search.search_questions([question("a")], query="不存在的词")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["total_matches"], 0)
        self.assertTrue(result["warnings"])

    def test_does_not_mutate_bank_or_execute_strings(self):
        bank = [question("a", "__import__('os').system('do-not-execute')")]
        original = copy.deepcopy(bank)
        result = search.search_questions(bank, course="高等数学")
        self.assertEqual(bank, original)
        self.assertEqual(result["results"][0]["question"], original[0]["question"])


class BankValidationTests(unittest.TestCase):
    def test_accepts_valid_and_empty_arrays(self):
        self.assertEqual(search.validate_bank([]), [])
        self.assertEqual(search.validate_bank([question("a")])[0]["id"], "a")

    def test_rejects_missing_empty_or_wrong_type_fields(self):
        for field in search.STRING_FIELDS:
            for value in (None, "", " \t", 1, [], True):
                with self.subTest(field=field, value=value):
                    row = question("a")
                    if value is None:
                        del row[field]
                    else:
                        row[field] = value
                    with self.assertRaises(search.InputError):
                        search.validate_bank([row])

    def test_rejects_invalid_tags_and_duplicate_ids(self):
        for tags in (None, [], [""], [" "], [1], "CALC.INT.PARTS", ["valid", None]):
            with self.subTest(tags=tags), self.assertRaises(search.InputError):
                search.validate_bank([question("a", knowledge_ids=tags)])
        with self.assertRaises(search.InputError):
            search.validate_bank([question("a"), question("a", "另一题")])

    def test_rejects_non_array_or_non_object(self):
        for data in ({}, "text", None, [None], ["text"]):
            with self.subTest(data=data), self.assertRaises(search.InputError):
                search.validate_bank(data)

    def test_bad_nonmatching_record_is_not_skipped(self):
        row = question("bad", course="线性代数")
        del row["answer"]
        with patch.object(Path, "read_text", return_value=json.dumps([question("a"), row])):
            with self.assertRaises(search.InputError):
                search.load_bank("not-read-from-disk.json")

    def test_load_errors_are_input_errors(self):
        for error in (OSError("unreadable"), UnicodeError("invalid UTF-8")):
            with patch.object(Path, "read_text", side_effect=error):
                with self.assertRaises(search.InputError):
                    search.load_bank("unused.json")
        with patch.object(Path, "read_text", return_value="{bad JSON"):
            with self.assertRaises(search.InputError):
                search.load_bank("unused.json")


class CommandLineTests(unittest.TestCase):
    def run_main(self, args, bank_text=None):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            if bank_text is None:
                code = search.main(args)
            else:
                with patch.object(Path, "read_text", return_value=bank_text):
                    code = search.main(args)
        return code, json.loads(capture.getvalue())

    def test_cli_errors_return_json_and_exit_two(self):
        cases = [
            [],
            ["--bank", "unused.json"],
            ["--bank", "unused.json", "--course", "高等数学", "--limit", "0"],
            ["--bank", "unused.json", "--course", "高等数学", "--limit", "21"],
            ["--bank", "unused.json", "--course", "高等数学", "--limit", "no"],
            ["--bank", "unused.json", "--query", "   "],
            ["--bank", "unused.json", "--knowledge-id", ""],
            ["--unknown"],
        ]
        for args in cases:
            with self.subTest(args=args):
                code, output = self.run_main(args, "[]")
                self.assertEqual(code, 2)
                self.assertEqual(output["status"], "error")

    def test_cli_invalid_bank_returns_json_and_exit_two(self):
        for bank_text in ("not json", "{}", '[{"id": "missing-fields"}]'):
            with self.subTest(bank_text=bank_text):
                code, output = self.run_main(["--bank", "unused.json", "--course", "高等数学"], bank_text)
                self.assertEqual(code, 2)
                self.assertEqual(output["status"], "error")

    def test_cli_repeated_options_and_default_limit(self):
        bank = [question("a"), question("b", "题二"), question("c", "题三"), question("d", "题四")]
        code, output = self.run_main([
            "--bank", "unused.json", "--knowledge-id", "OTHER", "--knowledge-id", "CALC.INT.PARTS",
            "--exclude-id", "a", "--exclude-id", "d",
        ], json.dumps(bank))
        self.assertEqual(code, 0)
        self.assertEqual([row["id"] for row in output["results"]], ["b", "c"])

    def test_actual_cli_success_and_process_exit_codes(self):
        success = subprocess.run([
            sys.executable, str(SCRIPT), "--bank", str(EXAMPLE_BANK),
            "--course", "高等数学", "--knowledge-id", "CALC.INT.PARTS", "--limit", "3",
        ], capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(success.returncode, 0, success.stderr)
        output = json.loads(success.stdout)
        self.assertEqual(output["status"], "ok")
        self.assertEqual(len(output["results"]), 3)
        failure = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(failure.returncode, 2)
        self.assertEqual(json.loads(failure.stdout)["status"], "error")


if __name__ == "__main__":
    unittest.main()
