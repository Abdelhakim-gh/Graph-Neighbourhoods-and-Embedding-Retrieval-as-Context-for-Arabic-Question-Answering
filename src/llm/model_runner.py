"""Shared model-calling interface. Ollama today; the interface is written so
an HF/transformers runner can be added later (for a study that needs a model
Ollama doesn't serve) without changing any caller.

`think=False` is required, not cosmetic: qwen3.5 defaults to emitting a
separate `thinking` field and, if left on, can burn the entire token budget
on it before producing any `message.content`, leaving the answer empty even
though the call "succeeded." It has no effect on non-reasoning models.

`num_ctx` must be passed explicitly on every call, not left to the model's
Modelfile default. A Modelfile's `PARAMETER num_ctx 8192` is not enough on
its own: Ollama falls back to 2048 tokens whenever the API request omits
`options.num_ctx`, whatever the Modelfile declares, and raises
`exceed_context_size_error` past that with no warning beforehand. The
contexts used here (150 fact lines plus the prompt) need more than 2048.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import ollama

logger = logging.getLogger(__name__)

DEFAULT_NUM_CTX = 8192  # what most of the roster reports via `ollama ps`


@dataclass
class GenerationResult:
    text: str
    tokens_in: int
    tokens_out: int

    @property
    def hit_token_cap(self) -> bool:
        """True when generation stopped because it ran out of budget rather
        than because the model finished. Recorded per row so truncation is
        visible next to each output (with a 64-token cap, Fanar-1-9B stopped
        at the cap on 86.2% of calls in an earlier experiment). Compared
        against the max_tokens actually passed; see
        scripts/04_run_answer_generation.py.
        """
        return self._max_tokens is not None and self.tokens_out >= self._max_tokens

    _max_tokens: int | None = None


class ModelRunner(ABC):
    @abstractmethod
    def generate(self, prompt: str, seed: int, temperature: float, max_tokens: int) -> GenerationResult: ...


class OllamaRunner(ModelRunner):
    def __init__(self, model_name: str, host: str = "http://localhost:11434", num_ctx: int = DEFAULT_NUM_CTX):
        self.model_name = model_name
        self.client = ollama.Client(host=host)
        self.num_ctx = num_ctx

    def generate(self, prompt: str, seed: int, temperature: float, max_tokens: int) -> GenerationResult:
        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, "seed": seed, "num_predict": max_tokens, "num_ctx": self.num_ctx},
            think=False,
        )
        text = response.message.content or ""
        return GenerationResult(
            text=text,
            tokens_in=response.prompt_eval_count or 0,
            tokens_out=response.eval_count or 0,
            _max_tokens=max_tokens,
        )

    def ping(self) -> bool:
        """One trivial call to confirm connectivity and correct Arabic round-tripping."""
        result = self.generate("اكتب كلمة: مرحبا", seed=1, temperature=0.0, max_tokens=16)
        ok = len(result.text.strip()) > 0
        logger.info("%s: ping %s, response=%r", self.model_name, "OK" if ok else "EMPTY", result.text)
        return ok
