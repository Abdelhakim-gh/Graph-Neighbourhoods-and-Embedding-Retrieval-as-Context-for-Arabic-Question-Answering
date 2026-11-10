"""Covers the parts of src/llm/model_runner.py that need no live Ollama call.

The rest of the module is a thin wrapper over ollama.Client.chat and is not
worth faking. hit_token_cap is tested because it is what makes truncated
answers visible in the results.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm.model_runner import DEFAULT_NUM_CTX, GenerationResult  # noqa: E402


def test_default_num_ctx_matches_studies_2_and_3():
    # Ollama silently falls back to 2048 when the request omits
    # options.num_ctx, so this constant keeps runs at the intended window.
    assert DEFAULT_NUM_CTX == 8192


@pytest.mark.parametrize(
    "tokens_out,max_tokens,expected",
    [
        (30, 256, False),   # finished on its own, well under budget
        (255, 256, False),  # one short of the cap is still a real stop
        (256, 256, True),   # stopped because it ran out of budget
        (64, 64, True),     # a short cap reached exactly
        (300, 256, True),   # over the cap, should never happen, still counts
    ],
)
def test_hit_token_cap(tokens_out, max_tokens, expected):
    gen = GenerationResult("x", tokens_in=400, tokens_out=tokens_out, _max_tokens=max_tokens)
    assert gen.hit_token_cap is expected


def test_hit_token_cap_is_false_when_no_budget_recorded():
    # A GenerationResult built without _max_tokens must not report
    # truncation it cannot know about. False here means "unknown".
    gen = GenerationResult("x", tokens_in=400, tokens_out=99999)
    assert gen.hit_token_cap is False
