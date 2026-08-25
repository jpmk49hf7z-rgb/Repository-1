"""Scoring and end-to-end pipeline tests.

Guards the arithmetic behind every headline number, plus the invariant that
matters most commercially: a failed engine call must never be counted as
evidence that a brand is absent.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aio.config import load_category
from aio.engines import build_engines
from aio.mentions import analyse_answer
from aio.models import Answer, Brand, Intent
from aio.prompts import build_prompt_set
from aio.report import render_report
from aio.scanner import run_scan
from aio.scoring import score_scan
from aio.store import Store

CLIENT = Brand("Acme Field", "acmefield.io", is_client=True)
RIVAL = Brand("Jobber", "getjobber.com")
BRANDS = [CLIENT, RIVAL]

CONFIG = Path(__file__).resolve().parents[1] / "config/categories/field-service-hvac.yaml"


def make(text, engine="e1", intent=Intent.DISCOVERY, sources=None, error=None):
    return Answer("p", "q", intent, engine, text, sources or [], error=error)


class TestScoring(unittest.TestCase):
    def _score(self, answers):
        return score_scan([(a, analyse_answer(a, BRANDS)) for a in answers], BRANDS)

    def test_mention_and_citation_rates(self):
        score = self._score([
            make("Acme Field is good.", sources=["https://acmefield.io/x"]),
            make("Jobber only."),
        ])
        client = score.brands["Acme Field"]
        self.assertEqual(client.mentions, 1)
        self.assertEqual(client.citations, 1)
        self.assertAlmostEqual(client.mention_rate, 0.5)

    def test_failed_answers_excluded_from_denominators(self):
        """A timeout is not evidence of invisibility — the core invariant."""
        score = self._score([
            make("Acme Field wins."),
            make("", error="RateLimitError: 429"),
        ])
        self.assertEqual(score.answers_scored, 1)
        self.assertEqual(score.answers_failed, 1)
        self.assertAlmostEqual(score.brands["Acme Field"].mention_rate, 1.0)

    def test_share_of_voice_sums_to_one(self):
        score = self._score([
            make("Acme Field and Jobber both."),
            make("Jobber alone."),
        ])
        total = sum(score.share_of_voice(b) for b in ("Acme Field", "Jobber"))
        self.assertAlmostEqual(total, 1.0)

    def test_discovery_intent_outweighs_problem_intent(self):
        """GoodNutrition aio-forming questions must count for more."""
        disc = self._score([make("Acme Field.", intent=Intent.DISCOVERY)])
        prob = self._score([make("Acme Field.", intent=Intent.PROBLEM)])
        self.assertGreater(
            disc.brands["Acme Field"].weighted_mentions,
            prob.brands["Acme Field"].weighted_mentions,
        )

    def test_leader_identifies_most_mentioned_brand(self):
        score = self._score([make("Jobber."), make("Jobber again."), make("Acme Field.")])
        self.assertEqual(score.leader.brand, "Jobber")

    def test_zero_mentions_gives_zero_not_error(self):
        score = self._score([make("Nobody relevant here.")])
        self.assertEqual(score.brands["Acme Field"].mentions, 0)
        self.assertEqual(score.share_of_voice("Acme Field"), 0.0)

    def test_per_engine_breakdown_is_tracked(self):
        score = self._score([
            make("Acme Field.", engine="chatgpt"),
            make("Jobber.", engine="perplexity"),
        ])
        self.assertEqual(score.brands["Acme Field"].by_engine["chatgpt"]["mentions"], 1)
        self.assertNotIn("perplexity", score.brands["Acme Field"].by_engine.get("chatgpt", {}))


class TestConfig(unittest.TestCase):
    def test_example_config_loads(self):
        spec, brands = load_category(CONFIG)
        self.assertTrue(any(b.is_client for b in brands))
        self.assertGreaterEqual(len(brands), 2)

    def test_config_without_competitors_is_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
            fh.write("slug: x\ncategory: y\naudience: z\n"
                     "client: {name: A, domain: a.com}\ncompetitors: []\n")
        with self.assertRaises(ValueError):
            load_category(fh.name)

    def test_prompt_set_is_deterministic(self):
        spec, _ = load_category(CONFIG)
        self.assertEqual(
            [p.text for p in build_prompt_set(spec)],
            [p.text for p in build_prompt_set(spec)],
        )


class TestEndToEnd(unittest.TestCase):
    def test_full_scan_produces_report_and_persists(self):
        spec, brands = load_category(CONFIG)
        prompts = build_prompt_set(spec, limit=6)
        engines = build_engines(
            ["mock"], [{"name": b.name, "domain": b.domain} for b in brands]
        )

        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "t.db")
            result = run_scan(
                prompts=prompts, brands=brands, engines=engines, store=store,
                slug=spec.slug, category=spec.category, concurrency=2,
            )
            self.assertEqual(result.score.answers_scored, len(prompts))

            totals = store.brand_totals(result.scan_id)
            self.assertEqual(
                totals[spec.client_name]["mentions"],
                result.score.brands[spec.client_name].mentions,
                "persisted totals must match in-memory score",
            )

            out = render_report(
                spec=spec, score=result.score, results=result.results,
                prompt_count=len(prompts), out_path=Path(tmp) / "r.html",
            )
            html = out.read_text()
            self.assertIn(spec.client_name, html)
            self.assertIn("Method.", html)

    def test_scan_with_no_available_engines_raises_clearly(self):
        spec, brands = load_category(CONFIG)
        engines = build_engines(["claude"], [])
        for e in engines:
            e.available = False
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                run_scan(
                    prompts=build_prompt_set(spec, limit=2), brands=brands,
                    engines=engines, store=Store(Path(tmp) / "t.db"),
                    slug=spec.slug, category=spec.category,
                )


class TestRetryPolicy(unittest.TestCase):
    def test_rate_limits_retry_but_bad_requests_do_not(self):
        from aio.engines.base import Engine
        self.assertTrue(Engine._retryable(Exception("RateLimitError: 429")))
        self.assertTrue(Engine._retryable(TimeoutError("timeout")))
        self.assertFalse(Engine._retryable(Exception("BadRequestError: bad model")))

    def test_adapter_failure_becomes_failed_answer_not_exception(self):
        from aio.engines.base import Engine
        from aio.models import Prompt

        class Broken(Engine):
            name = "broken"
            def _ask(self, prompt):
                raise ValueError("BadRequestError: nope")

        answer = Broken().ask(Prompt("x", Intent.DISCOVERY))
        self.assertFalse(answer.ok)
        self.assertIn("BadRequest", answer.error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
