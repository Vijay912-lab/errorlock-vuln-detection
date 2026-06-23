from __future__ import annotations

import json
import os
import signal
import threading
import time
import urllib.request
from abc import ABC, abstractmethod
from contextlib import contextmanager

from .types import CastleSample


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Deterministic provider for testing the pipeline without an LLM."""

    name = "mock-rule-detector"

    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        code = sample.code if sample else prompt
        lower = code.lower()
        vulnerable = any(token in lower for token in ["strcpy(", "sprintf(", "gets(", "system("])
        cwe = None
        if vulnerable and ("strcpy(" in lower or "gets(" in lower):
            cwe = "CWE-120"
        elif vulnerable and "sprintf(" in lower:
            cwe = "CWE-89" if "select" in lower else "CWE-120"
        return json.dumps(
            {
                "vulnerable": vulnerable,
                "cwe": cwe,
                "location": "line with unsafe call" if vulnerable else None,
                "explanation": "Rule-based local mock prediction.",
            }
        )


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, host: str = "http://127.0.0.1:11434"):
        self.name = model
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        options = {
            "temperature": 0,
            "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "256")),
        }
        if os.getenv("OLLAMA_NUM_CTX"):
            options["num_ctx"] = int(os.environ["OLLAMA_NUM_CTX"])
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "keep_alive": "10m",
                "options": options,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                data = json.loads(response.read())
        except Exception as exc:
            return json.dumps(
                {
                    "vulnerable": False,
                    "cwe": None,
                    "location": None,
                    "explanation": f"Ollama error: {exc}",
                }
            )
        return data.get("response", "")


class HuggingFaceProvider(LLMProvider):
    def __init__(self, model: str, max_new_tokens: int = 256, load_in_4bit: bool = True):
        self.name = model
        self.model_name = model
        self.max_new_tokens = max_new_tokens
        self.load_in_4bit = load_in_4bit
        self._tokenizer = None
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        kwargs = {"device_map": "auto"}
        if self.load_in_4bit:
            kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
        else:
            kwargs["torch_dtype"] = torch.float16 if torch.cuda.is_available() else torch.float32
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            **kwargs,
        )

    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        self._load()
        import torch

        messages = [{"role": "user", "content": prompt}]
        if hasattr(self._tokenizer, "apply_chat_template"):
            text = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            text = prompt
        inputs = self._tokenizer(text, return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        generated = output[0][inputs["input_ids"].shape[-1] :]
        return self._tokenizer.decode(generated, skip_special_tokens=True).strip()


def build_provider(kind: str, model: str | None = None) -> LLMProvider:
    if kind == "mock":
        return MockProvider()
    if kind == "ollama":
        if not model:
            raise ValueError("--model is required for ollama provider")
        return OllamaProvider(model)
    if kind == "hf":
        if not model:
            raise ValueError("--model is required for hf provider")
        return HuggingFaceProvider(model)
    if kind == "openrouter":
        return OpenAICompatibleProvider.from_env(
            name=model or "openai/gpt-oss-120b:free",
            base_url="https://openrouter.ai/api/v1",
            env_key="OPENROUTER_API_KEY",
            json_mode=True,
            extra_headers={
                "HTTP-Referer": "https://github.com/vishalgajavelly/CS541-Course-Project-Error-Lock",
                "X-Title": "ErrorLock CASTLE Benchmark",
            },
        )
    if kind == "groq":
        return OpenAICompatibleProvider.from_env(
            name=model or "openai/gpt-oss-20b",
            base_url="https://api.groq.com/openai/v1",
            env_key="GROQ_API_KEY",
            json_mode=True,
        )
    if kind == "hf-api":
        return OpenAICompatibleProvider.from_env(
            name=model or "meta-llama/Llama-3.1-8B-Instruct",
            base_url="https://api-inference.huggingface.co/v1",
            env_key="HF_TOKEN",
            fallback_env_key="HUGGINGFACEHUB_API_TOKEN",
            json_mode=False,
        )
    if kind == "gemini":
        return GeminiProvider.from_env(model or "gemini-2.5-flash-lite")
    if kind == "openai":
        return OpenAICompatibleProvider.from_env(
            name=model or "gpt-5.4-mini",
            base_url="https://api.openai.com/v1",
            env_key="OPENAI_API_KEY",
            json_mode=True,
        )
    raise ValueError(f"unknown provider: {kind}")


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        json_mode: bool = True,
        extra_headers: dict[str, str] | None = None,
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.json_mode = json_mode
        self.extra_headers = extra_headers or {}

    @classmethod
    def from_env(
        cls,
        name: str,
        base_url: str,
        env_key: str,
        fallback_env_key: str | None = None,
        json_mode: bool = True,
        extra_headers: dict[str, str] | None = None,
    ) -> "OpenAICompatibleProvider":
        api_key = os.getenv(env_key) or (os.getenv(fallback_env_key) if fallback_env_key else None)
        if not api_key:
            keys = env_key if not fallback_env_key else f"{env_key} or {fallback_env_key}"
            raise ValueError(f"Missing API key. Set {keys}.")
        return cls(
            name=name,
            base_url=base_url,
            api_key=api_key,
            json_mode=json_mode,
            extra_headers=extra_headers,
        )

    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        body = {
            "model": self.name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 512,
        }
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}
        payload = json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers=headers,
        )
        timeout = int(os.getenv("API_TIMEOUT_SECONDS", "120"))
        attempts = max(1, int(os.getenv("API_MAX_RETRIES", "2")))
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                with _deadline(timeout):
                    with urllib.request.urlopen(request, timeout=timeout) as response:
                        data = json.loads(response.read())
                return data["choices"][0]["message"]["content"]
            except Exception as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    time.sleep(min(2 ** attempt, 10))
        return f"API_ERROR: {last_error}"


@contextmanager
def _deadline(seconds: int):
    if threading.current_thread() is not threading.main_thread() or not hasattr(signal, "SIGALRM"):
        yield
        return

    def timeout_handler(_signum, _frame):
        raise TimeoutError(f"request exceeded {seconds}s")

    previous_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


class GeminiProvider(LLMProvider):
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.api_key = api_key

    @classmethod
    def from_env(cls, name: str) -> "GeminiProvider":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY.")
        return cls(name, api_key)

    def generate(self, prompt: str, sample: CastleSample | None = None) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.name}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 512,
                "responseMimeType": "application/json",
            },
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as exc:
            return f"API_ERROR: {exc}"
