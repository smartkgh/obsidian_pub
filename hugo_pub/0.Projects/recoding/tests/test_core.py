"""recoding 테스트 — 표준 라이브러리 unittest 만 사용 (외부 의존성 0)

실행: python3 run_tests.py          (구버전 파이썬이면 .venv 로 자동 재실행)
      .venv/bin/python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import logging
import subprocess
import tempfile
import unicodedata
import unittest
from pathlib import Path

from adapters.base import Segment, Transcript
from core import keyword, render, spacing
from core.config import Config
from core.ledger import Ledger
from core.pipeline import Pipeline, clean_segments, file_sha1

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"


class RenderTest(unittest.TestCase):
    def test_filename_rules(self):
        self.assertEqual(render.safe_filename('a/b:c*d?e"f<g>h|i'), "a_b_c_d_e_f_g_h_i")
        self.assertEqual(len(render.safe_filename("가" * 60, 40)), 40)
        self.assertEqual(render.safe_filename("   ", 40), "녹음")

    def test_nfc_and_tag(self):
        self.assertEqual(render.nfc(unicodedata.normalize("NFD", "음성기록")), "음성기록")
        self.assertEqual(render.safe_tag("한강 산책 #1"), "한강_산책_1")

    def test_time_format(self):
        self.assertEqual(render.fmt_duration(3725.4), "01:02:05")
        self.assertEqual(render.fmt_ts(65), "01:05")
        self.assertEqual(render.fmt_ts(3725), "1:02:05")

    def test_yaml_quote(self):
        self.assertEqual(render.yaml_str('그는 "안녕" 이라 했다'), '"그는 \\"안녕\\" 이라 했다"')

    def test_unique_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.assertEqual(render.unique_path(d, "산책").name, "산책.md")
            (d / "산책.md").touch()
            self.assertEqual(render.unique_path(d, "산책").name, "산책-2.md")
            (d / "산책-2.md").touch()
            self.assertEqual(render.unique_path(d, "산책").name, "산책-3.md")

    def test_paragraphs(self):
        segs = [Segment(0, 5, "첫 문장."), Segment(6, 9, "이어지는 문장."), Segment(30, 33, "뒤 문장.")]
        self.assertEqual(len(render.paragraphs(segs, gap=3.0)), 2)
        self.assertEqual(len(render.paragraphs(segs, gap=25.0)), 1)


class CleanTest(unittest.TestCase):
    def test_dedupe_and_hallucination(self):
        segs = [Segment(0, 1, "안녕하세요"), Segment(1, 2, "안녕하세요"), Segment(2, 3, "  "),
                Segment(3, 4, "감사합니다"), Segment(4, 5, "다음 이야기")]
        self.assertEqual([s.text for s in clean_segments(segs)], ["안녕하세요", "다음 이야기"])

    def test_single_segment_kept(self):
        self.assertEqual([s.text for s in clean_segments([Segment(0, 1, "감사합니다")])], ["감사합니다"])

    def test_keyword_heuristic(self):
        out = keyword._heuristic("오늘은 아파트 재건축 회의가 있었습니다. 아파트 재건축 결정.")
        self.assertTrue(out["keyword"])
        self.assertTrue(out["summary"].endswith("."))


class SpacingTest(unittest.TestCase):
    def setUp(self):
        self._orig_post = spacing._post

    def tearDown(self):
        spacing._post = self._orig_post

    def test_merge_keeps_characters(self):
        for orig, cand in [
            ("동의서는이번주까지걷기로했어요", "동의서는 이번 주까지 걷기로 했어요"),
            ("영향받지않을거야라고생각합니다", "영향을 받지 않을 거야라고 생각합니다"),
        ]:
            got = spacing._apply_spacing_only(orig, cand)
            self.assertEqual(spacing._non_space(got), spacing._non_space(orig))
            self.assertNotEqual(got, orig)

    def test_merge_keeps_paragraphs(self):
        orig = "첫문단입니다.두번째문장입니다.\n\n둘째문단입니다."
        got = spacing._apply_spacing_only(orig, "첫 문단입니다. 두 번째 문장입니다.\n\n둘째 문단입니다.")
        self.assertIn("\n\n", got)
        self.assertEqual(spacing._non_space(got), spacing._non_space(orig))

    def test_branches(self):
        orig = "동의서는이번주까지걷기로했어요"
        cfg = Config({"postprocess": {"spacing_fix": True, "chunk_chars": 3000}}, ROOT)

        spacing._post = lambda c, t: "동의서는 이번 주까지 걷기로 했어요"
        self.assertEqual(spacing.fix_spacing(orig, cfg), "동의서는 이번 주까지 걷기로 했어요")

        spacing._post = lambda c, t: "동의서는 이번 주까지 걸으려고 했어요"
        got = spacing.fix_spacing(orig, cfg)
        self.assertEqual(spacing._non_space(got), spacing._non_space(orig))
        self.assertNotEqual(got, orig)

        spacing._post = lambda c, t: None
        self.assertEqual(spacing.fix_spacing(orig, cfg), orig)
        self.assertEqual(spacing.fix_spacing(orig, Config({"postprocess": {"spacing_fix": False}}, ROOT)), orig)
        self.assertEqual(spacing.fix_spacing(orig, Config({"postprocess": {"spacing_fix": True,
                                                                          "max_total_chars": 3}}, ROOT)), orig)

    def test_chunks_respect_size(self):
        text = "\n\n".join(["오늘은아파트재건축추진위원회회의가있었습니다"] * 6)
        sizes = []

        def fake(cfg, t):
            sizes.append(len(spacing._non_space(t)))
            ns = spacing._non_space(t)
            return ns[:4] + " " + ns[4:]

        spacing._post = fake
        cfg = Config({"postprocess": {"spacing_fix": True, "chunk_chars": 20}}, ROOT)
        out = spacing.fix_spacing(text, cfg)
        self.assertGreaterEqual(len(sizes), 5)
        self.assertTrue(all(s <= 20 for s in sizes), sizes)
        self.assertEqual(spacing._non_space(out), spacing._non_space(text))
        self.assertGreater(out.count(" "), text.count(" "))


class LedgerTest(unittest.TestCase):
    def test_crud(self):
        with tempfile.TemporaryDirectory() as tmp:
            led = Ledger(Path(tmp) / "ledger.sqlite")
            led.insert_seen("sha-a", "음성 1.m4a", 100, 1000.0)

            def row():
                got = led.get("sha-a")
                if got is None:
                    self.fail("ledger row 없음")
                return got

            self.assertEqual(row()["status"], "new")
            led.set_status("sha-a", "transcribing", engine="apple")
            self.assertEqual(row()["engine"], "apple")
            self.assertEqual(led.count(["new", "transcribing"]), 1)
            led.set_status("sha-a", "done", keyword="산책")
            self.assertEqual(led.stats(), {"done": 1})
            self.assertEqual(led.keywords(), ["산책"])
            led.insert_seen("sha-a", "다른이름.m4a", 999, 999.0)
            self.assertEqual(row()["filename"], "음성 1.m4a")
            led.delete("sha-a")
            self.assertIsNone(led.get("sha-a"))
            led.close()


class ConfigTest(unittest.TestCase):
    def test_dotted_sections_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "config.toml"
            path.write_text('[paths]\nincoming = "~/x"\n'
                            '[asr.apple]\nhelper = "platforms/macos/.build/SpeechHelper"\n',
                            encoding="utf-8")
            cfg = Config.load(path)
            self.assertEqual(cfg.sec("asr.apple")["helper"], "platforms/macos/.build/SpeechHelper")
            self.assertEqual(cfg.sec("nope"), {})
            self.assertTrue(str(cfg.path("paths", "incoming")).startswith(str(Path.home())))
            self.assertEqual(cfg.path("asr.apple", "helper"),
                             base.resolve() / "platforms/macos/.build/SpeechHelper")

    def test_shipped_config(self):
        cfg = Config.load(ROOT / "config.toml")
        self.assertEqual(cfg.get("asr", "engine"), "apple")
        self.assertEqual(cfg.get("postprocess", "chunk_chars"), 3000)
        self.assertEqual(cfg.get("postprocess", "max_total_chars"), 100000)
        self.assertNotEqual(cfg.path("archive", "done_dir"), cfg.path("paths", "incoming") / "_done")
        self.assertNotIn("recoding/_done", str(cfg.path("archive", "done_dir")))


class MainGuardTest(unittest.TestCase):
    def test_guard_precedes_core_imports(self):
        src = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("os.execv", src)
        self.assertLess(src.index("_ensure_interpreter()"), src.index("from core."))

    def test_runs_with_venv_python(self):
        out = subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "main.py"), "doctor"],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(out.returncode, 0, out.stderr[:300])
        self.assertIn("asr engine", out.stdout)


class LockTest(unittest.TestCase):
    def test_single_instance(self):
        from core.lock import LockBusy, single_instance

        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "lock"
            with single_instance(lock):
                with self.assertRaises(LockBusy):
                    with single_instance(lock):
                        pass
            with single_instance(lock):        # 해제 후 재획득 가능
                self.assertTrue(lock.exists())


class FakeAdapter:
    needs_wav = False

    def transcribe(self, audio):
        return Transcript([Segment(0, 1, "첫문장입니다."), Segment(1, 2, "둘째문장입니다.")],
                          engine="fake", lang="ko", duration=2.0)

    def describe(self):
        return "fake"


@unittest.skipUnless(Path(FFMPEG).exists(), "ffmpeg 없음")
class PipelineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.incoming = self.tmp / "incoming"
        self.incoming.mkdir()
        cfg_path = self.tmp / "c.toml"
        cfg_path.write_text(f'''
[paths]
incoming = "{self.incoming}"
output   = "{self.tmp / 'result'}"
state    = "{self.tmp / 'state'}"
[asr]
engine = "apple"
min_duration = 0.5
settle_seconds = 0
[audio]
ffmpeg = "{FFMPEG}"
ffprobe = "{FFPROBE}"
[output]
include_summary = false
[keyword]
provider = "heuristic"
[archive]
move_originals = true
done_dir = "{self.tmp / 'done'}"
failed_dir = "{self.tmp / 'failed'}"
[postprocess]
spacing_fix = false
''', encoding="utf-8")
        self._orig_factory = Pipeline.__init__.__globals__["make_adapter"]
        Pipeline.__init__.__globals__["make_adapter"] = lambda cfg: FakeAdapter()
        self.addCleanup(self._restore_factory)
        quiet = logging.getLogger("recoding.test")
        quiet.handlers, quiet.propagate = [logging.NullHandler()], False
        self.pipe = Pipeline(Config.load(cfg_path), quiet)

    def _restore_factory(self):
        Pipeline.__init__.__globals__["make_adapter"] = self._orig_factory

    def _status(self, sha: str) -> str:
        row = self.pipe.ledger.get(sha)
        if row is None:
            self.fail(f"ledger row 없음: {sha}")
        return row["status"]

    def _tone(self, name: str, seconds: float) -> Path:
        path = self.incoming / name
        subprocess.run([FFMPEG, "-nostdin", "-y", "-loglevel", "error",
                        "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
                        "-c:a", "aac", str(path)], check=True)
        return path

    def test_process_flow(self):
        audio = self._tone("음성 111111_000000.m4a", 2)
        self.assertEqual(self.pipe.run_once(), [])                    # 등록만
        self.assertEqual(self._status(file_sha1(audio)), "new")
        results = self.pipe.run_once()                                # 처리
        self.assertEqual([r.status for r in results], ["done"])
        res = results[0]
        out = res.out_path
        if out is None:
            self.fail("산출물 경로 없음")
        self.assertTrue(out.exists())
        self.assertFalse(audio.exists())
        self.assertTrue((self.tmp / "done" / audio.name).exists())
        self.assertTrue((self.tmp / "result" / "_raw" / f"{out.stem}.json").exists())
        body = out.read_text(encoding="utf-8")
        self.assertIn('engine: "fake"', body)
        self.assertIn("## 구간", body)
        self.assertEqual(self.pipe.run_once(), [])                    # 중복 없음

    def test_corrupt_and_short(self):
        bad = self.incoming / "broken.m4a"
        bad.write_bytes(b"not audio")
        bad_sha = file_sha1(bad)
        self.pipe.run_once()
        self.pipe.run_once()
        self.assertEqual(self._status(bad_sha), "failed")
        self.assertTrue((self.tmp / "failed" / "broken.m4a").exists())

        short = self._tone("short.m4a", 0.3)
        short_sha = file_sha1(short)
        self.pipe.run_once()
        self.pipe.run_once()
        self.assertEqual(self._status(short_sha), "skipped")

    def test_scan_survives_vanished_file(self):
        ghost = self.incoming / "ghost.m4a"
        ghost.write_bytes(b"x")
        import core.pipeline as P
        original = P.file_sha1
        P.file_sha1 = lambda p: (_ for _ in ()).throw(FileNotFoundError()) if p.name == "ghost.m4a" else original(p)
        try:
            self.pipe.scan()          # 예외 없이 통과해야 함
        finally:
            P.file_sha1 = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
