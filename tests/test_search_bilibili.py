"""Offline tests for the public search adapter. No test uses the real network."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
import uuid


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "university-review" / "scripts" / "search_bilibili.py"
SPEC = importlib.util.spec_from_file_location("search_bilibili", SCRIPT)
search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(search)


def api_response(rows=None, **extra):
    if rows is None:
        rows = [{"bvid": "BV1234567890", "title": "A <em>chain</em> rule &amp; example", "description": "<p>Derivative</p><p>practice</p>", "author": "Teacher", "duration": "12:34", "pubdate": 1700000000}]
    return json.dumps({"code": 0, "data": {"result": rows}, **extra}).encode("utf-8")


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, size):
        return self.body[:size]


class SearchTests(unittest.TestCase):
    def setUp(self):
        # A normal mkdir avoids Python's mode-0700 temporary-directory ACL,
        # which some restricted Windows runners cannot subsequently access.
        test_root = Path(__file__).resolve().parent
        self.directory = test_root / ("_search_test_" + uuid.uuid4().hex)
        self.directory.mkdir()
        self.assertEqual(self.directory.resolve().parent, test_root)
        # Default to a hard network failure so every unintended request fails.
        self.network = patch.object(search, "urlopen", side_effect=AssertionError("unexpected real network access"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.addCleanup(shutil.rmtree, self.directory)

    def run_online(self, body, query="链式法则", **kwargs):
        with patch.object(search, "urlopen", return_value=FakeResponse(body)) as request:
            result, code = search.run_search(query, cache_dir=self.directory, **kwargs)
        return result, code, request

    def test_clean_metadata_and_construct_verified_urls(self):
        result, code, request = self.run_online(api_response(), no_cache=True)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "ok")
        row = result["results"][0]
        self.assertEqual(row["title"], "A chain rule & example")
        self.assertEqual(row["description"], "Derivative practice")
        self.assertEqual(row["url"], "https://www.bilibili.com/video/BV1234567890/")
        self.assertEqual(row["published_at"], "2023-11-14T22:13:20Z")
        self.assertEqual(row["source"], "bilibili_public_search")
        self.assertIn("untrusted", result["data_notice"])
        self.assertEqual(parse_qs(urlsplit(result["search_url"]).query)["keyword"], ["链式法则"])
        call = request.call_args
        self.assertEqual(call.kwargs["timeout"], 10.0)
        actual_request = call.args[0]
        self.assertEqual(urlsplit(actual_request.full_url).path, "/x/web-interface/search/type")
        self.assertEqual(parse_qs(urlsplit(actual_request.full_url).query)["search_type"], ["video"])
        self.assertEqual(actual_request.get_header("User-agent"), search.USER_AGENT)
        self.assertIsNone(actual_request.get_header("Cookie"))
        self.assertNotIn("t=", row["url"])

    def test_invalid_bv_ids_and_duplicate_ids_are_excluded(self):
        rows = [{"bvid": value, "title": "Sample", "arcurl": "https://malicious.invalid/"} for value in ["BV1234567890", "BV1234567890", "av123", "BV123", "BV1234567890/", "BV123456789_", None]]
        result, _, _ = self.run_online(api_response(rows), no_cache=True)
        self.assertEqual([row["id"] for row in result["results"]], ["BV1234567890"])
        self.assertEqual(result["results"][0]["url"], "https://www.bilibili.com/video/BV1234567890/")
        self.assertIsNone(result["results"][0]["published_at"])

    def test_http_rejection_falls_back_without_retry_or_cache(self):
        for status in (403, 412, 429):
            with self.subTest(status=status):
                error = HTTPError("https://api.bilibili.com/", status, "denied", {}, None)
                with patch.object(search, "urlopen", side_effect=error) as request:
                    result, code = search.run_search("test", cache_dir=self.directory)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(code, 0)
                self.assertEqual(result["status"], "manual_search_required")
                self.assertEqual(result["results"], [])
                self.assertIn(str(status), result["reason"])
                self.assertEqual(list(self.directory.iterdir()), [])

    def test_api_rejection_falls_back_without_retry(self):
        result, code, request = self.run_online(json.dumps({"code": -412, "message": "blocked"}).encode())
        self.assertEqual(request.call_count, 1)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "manual_search_required")
        self.assertIn("-412", result["reason"])
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_non_json_or_missing_structure_falls_back(self):
        cases = [b"<html>captcha</html>", b"[]", b"{}", b'{"code":false}', b'{"code":0}', b'{"code":0,"data":{}}', b'{"code":0,"data":{"result":{}}}']
        for body in cases:
            with self.subTest(body=body):
                result, code, request = self.run_online(body)
                self.assertEqual(code, 0)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(result["status"], "manual_search_required")
                self.assertEqual(list(self.directory.iterdir()), [])

    def test_cache_hit_preserves_results_above_initial_limit(self):
        rows = [{"bvid": "BV" + f"{number:010d}", "title": str(number)} for number in range(6)]
        initial, _, request = self.run_online(api_response(rows), limit=1)
        self.assertEqual(len(initial["results"]), 1)
        self.assertEqual(request.call_count, 1)
        result, code = search.run_search("链式法则", cache_dir=self.directory, limit=10)
        self.assertEqual(code, 0)
        self.assertEqual(len(result["results"]), 6)
        cache = json.loads(next(self.directory.glob("*.json")).read_text())
        self.assertEqual(cache["schema_version"], 1)
        self.assertEqual(cache["query"], "链式法则")

    def test_different_query_is_not_cached(self):
        self.run_online(api_response(), query="first")
        result, _, request = self.run_online(api_response(), query="second")
        self.assertEqual(request.call_count, 1)
        self.assertEqual(result["query"], "second")
        self.assertEqual(len(list(self.directory.glob("*.json"))), 2)

    def test_expired_corrupt_or_mismatched_cache_is_replaced(self):
        for issue in ("expired", "corrupt", "query", "url", "schema"):
            with self.subTest(issue=issue):
                self.run_online(api_response())
                path = search._cache_path(self.directory, "链式法则")
                payload = json.loads(path.read_text())
                if issue == "expired":
                    payload["cached_at"] = time.time() - 100
                elif issue == "query":
                    payload["query"] = "different query"
                elif issue == "url":
                    payload["results"][0]["url"] = "https://malicious.invalid/"
                elif issue == "schema":
                    payload["schema_version"] = 999
                path.write_text("{bad" if issue == "corrupt" else json.dumps(payload), encoding="utf-8")
                result, code, request = self.run_online(api_response(), cache_ttl=10)
                self.assertEqual(code, 0)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(result["status"], "ok")

    def test_no_cache_neither_reads_nor_writes(self):
        self.run_online(api_response())
        path = search._cache_path(self.directory, "链式法则")
        previous = path.read_bytes()
        result, _, request = self.run_online(api_response([]), no_cache=True)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(result["results"], [])
        self.assertEqual(path.read_bytes(), previous)

    def test_offline_file_bypasses_network_and_cache(self):
        self.run_online(api_response())
        fixture = self.directory / "fixture.json"
        fixture.write_bytes(api_response([]))
        result, code = search.run_search("链式法则", offline_file=fixture, cache_dir=self.directory)
        self.assertEqual(code, 0)
        self.assertEqual(result["results"], [])
        self.assertEqual(len(list(self.directory.glob("*.json"))), 2)

    def test_malformed_and_missing_offline_files_are_exit_two(self):
        fixture = self.directory / "fixture.json"
        for body in (b"<html>not JSON</html>", b"{}", b"\xff"):
            fixture.write_bytes(body)
            result, code = search.run_search("test", offline_file=fixture)
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "error")
        result, code = search.run_search("test", offline_file=self.directory / "missing.json")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")

    def test_offline_api_rejection_is_valid_manual_fallback(self):
        fixture = self.directory / "rejected.json"
        fixture.write_text('{"code":-412}', encoding="utf-8")
        result, code = search.run_search("test", offline_file=fixture)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "manual_search_required")

    def test_empty_success_response_is_valid(self):
        result, code, _ = self.run_online(api_response([]), no_cache=True)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["results"], [])

    def test_cli_validation_and_json_output(self):
        for args in ([], ["--query", " "], ["--query", "x", "--limit", "0"], ["--query", "x", "--limit", "11"], ["--query", "x", "--timeout", "0"], ["--query", "x", "--cache-ttl", "nan"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    search.main(args)
                self.assertEqual(error.exception.code, 2)
        fixture = self.directory / "fixture.json"
        fixture.write_bytes(api_response())
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = search.main(["--query", "test", "--offline-file", str(fixture)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "ok")


if __name__ == "__main__":
    unittest.main()
