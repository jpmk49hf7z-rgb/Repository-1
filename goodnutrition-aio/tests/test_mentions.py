"""Tests for brand mention/citation detection.

Focused on the cases that silently corrupt headline numbers: ambiguous
brand names, substring collisions, possessives, and citation-only presence.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aio.models import Answer, Brand, Intent
from aio.mentions import analyse_answer, find_brand, normalise_host


def answer(text: str, sources: list[str] | None = None) -> Answer:
    return Answer(
        prompt_id="p1",
        prompt_text="best software?",
        intent=Intent.DISCOVERY,
        engine="test",
        text=text,
        sources=sources or [],
    )


JOBBER = Brand("Jobber", "jobber.com", is_client=True)
NOTION = Brand("Notion", "notion.so", ambiguous=True)
RAMP = Brand("Ramp", "ramp.com", ambiguous=True)
MONDAY = Brand("monday.com", "monday.com", aliases=("Monday",), ambiguous=True)


class TestPlainMatching(unittest.TestCase):
    def test_simple_mention(self):
        self.assertTrue(find_brand(answer("Jobber is popular."), JOBBER).mentioned)

    def test_case_insensitive_for_unambiguous_brand(self):
        self.assertTrue(find_brand(answer("we like jobber a lot"), JOBBER).mentioned)

    def test_possessive_counts(self):
        self.assertTrue(find_brand(answer("Jobber's pricing is fair."), JOBBER).mentioned)

    def test_curly_possessive_counts(self):
        self.assertTrue(find_brand(answer("Jobber’s pricing."), JOBBER).mentioned)

    def test_absent_brand_not_reported(self):
        self.assertFalse(find_brand(answer("ServiceTitan only."), JOBBER).mentioned)

    def test_substring_is_not_a_match(self):
        """'Ramp' must not match inside 'Rampart' — the classic false positive."""
        self.assertFalse(find_brand(answer("Rampart Systems Inc."), RAMP).mentioned)

    def test_hyphen_prefix_is_not_a_match(self):
        pilot = Brand("Pilot", "pilot.com", ambiguous=True)
        self.assertFalse(find_brand(answer("Uses a co-pilot feature."), pilot).mentioned)


class TestAmbiguousNames(unittest.TestCase):
    def test_lowercase_common_word_alone_is_rejected(self):
        """'a notion of scheduling' is English, not a vendor."""
        hit = find_brand(answer("They had no notion of what to buy."), NOTION)
        self.assertFalse(hit.mentioned)

    def test_capitalised_common_word_is_accepted(self):
        self.assertTrue(find_brand(answer("Notion is worth a look."), NOTION).mentioned)

    def test_lowercase_rescued_by_nearby_product_word(self):
        hit = find_brand(answer("the notion platform is cheap"), NOTION)
        self.assertTrue(hit.mentioned)

    def test_lowercase_rescued_by_domain_in_text(self):
        hit = find_brand(answer("try notion, see notion.so for details"), NOTION)
        self.assertTrue(hit.mentioned)

    def test_distant_product_word_does_not_rescue(self):
        text = "no notion at all. " + "filler " * 40 + "software"
        self.assertFalse(find_brand(answer(text), NOTION).mentioned)

    def test_alias_with_dot_matches(self):
        self.assertTrue(find_brand(answer("We use monday.com daily."), MONDAY).mentioned)

    def test_ambiguous_alias_lowercase_weekday_rejected(self):
        """'on monday we ship' must not read as the vendor."""
        self.assertFalse(find_brand(answer("we ship on monday and rest"), MONDAY).mentioned)


class TestCitations(unittest.TestCase):
    def test_citation_detected_from_sources(self):
        hit = find_brand(answer("No names given.", ["https://www.jobber.com/x"]), JOBBER)
        self.assertTrue(hit.cited)
        self.assertFalse(hit.mentioned)
        self.assertTrue(hit.present)

    def test_subdomain_counts_as_citation(self):
        hit = find_brand(answer("x", ["https://help.jobber.com/a"]), JOBBER)
        self.assertTrue(hit.cited)

    def test_lookalike_domain_is_not_a_citation(self):
        hit = find_brand(answer("x", ["https://notjobber.com/a"]), JOBBER)
        self.assertFalse(hit.cited)

    def test_bare_domain_in_prose_is_a_mention(self):
        brand = Brand("Acme Field", "acmefield.io")
        hit = find_brand(answer("Look at acmefield.io for this."), brand)
        self.assertTrue(hit.mentioned)

    def test_normalise_host_strips_www_and_scheme(self):
        self.assertEqual(normalise_host("https://www.Jobber.com/pricing"), "jobber.com")
        self.assertEqual(normalise_host("jobber.com"), "jobber.com")


class TestRanking(unittest.TestCase):
    def test_rank_follows_order_of_first_mention(self):
        text = "ServiceTitan leads, then Jobber, then Housecall Pro."
        hits = analyse_answer(
            answer(text),
            [JOBBER, Brand("ServiceTitan", "servicetitan.com"),
             Brand("Housecall Pro", "housecallpro.com")],
        )
        by_name = {h.brand: h for h in hits}
        self.assertEqual(by_name["ServiceTitan"].rank, 1)
        self.assertEqual(by_name["Jobber"].rank, 2)
        self.assertEqual(by_name["Housecall Pro"].rank, 3)

    def test_unmentioned_brand_has_no_rank(self):
        hits = analyse_answer(answer("Only Jobber here."), [JOBBER, NOTION])
        self.assertIsNone({h.brand: h for h in hits}["Notion"].rank)

    def test_citation_only_brand_is_unranked_but_present(self):
        hits = analyse_answer(answer("Nothing named.", ["https://jobber.com"]), [JOBBER])
        self.assertIsNone(hits[0].rank)
        self.assertTrue(hits[0].present)

    def test_evidence_snippet_is_captured(self):
        hit = find_brand(answer("For contractors, Jobber is strong."), JOBBER)
        self.assertIn("Jobber", hit.evidence)


if __name__ == "__main__":
    unittest.main(verbosity=2)
