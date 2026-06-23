from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .types import CastleSample, ScoredPrediction, normalize_cwe


@dataclass(frozen=True)
class Mistake:
    id: int
    sample_id: str
    code: str
    true_vulnerable: bool
    true_cwe: str | None
    true_location: str | None
    predicted_vulnerable: bool | None
    predicted_cwe: str | None
    predicted_location: str | None
    predicted_explanation: str | None
    failure_type: str
    raw_response: str
    similarity: float = 0.0


@dataclass(frozen=True)
class RagContext:
    mistakes: list[Mistake]
    text: str
    candidate_count: int


class MistakeMemory:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        schema = Path(__file__).with_name("schema.sql").read_text()
        self.conn.executescript(schema)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def add_if_mistake(self, scored: ScoredPrediction) -> bool:
        failure = scored.failure_type
        if not failure:
            return False
        p = scored.prediction
        s = scored.sample
        self.conn.execute(
            """
            INSERT INTO mistakes (
              model, sample_id, code, true_vulnerable, true_cwe, true_location,
              predicted_vulnerable, predicted_cwe, predicted_location,
              predicted_explanation, failure_type, raw_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scored.model,
                s.sample_id,
                s.code,
                int(s.vulnerable),
                s.cwe,
                s.location,
                None if p.vulnerable is None else int(p.vulnerable),
                p.cwe,
                p.location,
                p.explanation,
                failure,
                p.raw,
            ),
        )
        self.conn.commit()
        return True

    def retrieve(
        self,
        sample: CastleSample,
        model: str | None = None,
        top_k: int | None = 3,
        predicted_vulnerable: bool | None = None,
        predicted_cwe: str | None = None,
    ) -> list[Mistake]:
        query = "SELECT * FROM mistakes"
        params: list[str] = []
        if model:
            query += " WHERE model = ?"
            params.append(model)
        rows = [self._row_to_mistake(row) for row in self.conn.execute(query, params).fetchall()]
        if not rows:
            return []
        char_scores = _similarities(rows, sample.code, analyzer="char_wb", ngram_range=(3, 5))
        token_scores = _similarities(rows, sample.code, analyzer="word", token_pattern=r"(?u)\b[A-Za-z_]\w+\b")
        scores = [
            _rerank_score(row, char_score, token_score, predicted_vulnerable, predicted_cwe)
            for row, char_score, token_score in zip(rows, char_scores, token_scores)
        ]
        ranked = sorted(zip(rows, scores), key=lambda item: item[1], reverse=True)
        if top_k is not None and top_k > 0:
            ranked = ranked[:top_k]
        return [Mistake(**{**m.__dict__, "similarity": float(score)}) for m, score in ranked]

    def retrieve_rag_context(
        self,
        sample: CastleSample,
        model: str | None = None,
        candidate_k: int = 25,
        context_k: int = 6,
        predicted_vulnerable: bool | None = None,
        predicted_cwe: str | None = None,
        snippet_chars: int = 700,
    ) -> RagContext:
        candidates = self.retrieve(
            sample,
            model=model,
            top_k=candidate_k,
            predicted_vulnerable=predicted_vulnerable,
            predicted_cwe=predicted_cwe,
        )
        selected = _select_diverse(candidates, context_k)
        return RagContext(
            mistakes=selected,
            text=_format_rag_context(selected, candidates, predicted_vulnerable, predicted_cwe, snippet_chars),
            candidate_count=len(candidates),
        )

    def count(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM mistakes").fetchone()[0])

    @staticmethod
    def _row_to_mistake(row: sqlite3.Row) -> Mistake:
        return Mistake(
            id=row["id"],
            sample_id=row["sample_id"],
            code=row["code"],
            true_vulnerable=bool(row["true_vulnerable"]),
            true_cwe=row["true_cwe"],
            true_location=row["true_location"],
            predicted_vulnerable=None
            if row["predicted_vulnerable"] is None
            else bool(row["predicted_vulnerable"]),
            predicted_cwe=row["predicted_cwe"],
            predicted_location=row["predicted_location"],
            predicted_explanation=row["predicted_explanation"],
            failure_type=row["failure_type"],
            raw_response=row["raw_response"],
        )


def _similarities(rows: list[Mistake], code: str, **vectorizer_kwargs) -> list[float]:
    corpus = [m.code for m in rows] + [code]
    vectors = TfidfVectorizer(min_df=1, **vectorizer_kwargs).fit_transform(corpus)
    return [float(score) for score in cosine_similarity(vectors[-1], vectors[:-1]).ravel()]


def _rerank_score(
    mistake: Mistake,
    char_score: float,
    token_score: float,
    predicted_vulnerable: bool | None,
    predicted_cwe: str | None,
) -> float:
    score = 0.7 * char_score + 0.3 * token_score
    if predicted_vulnerable is not None and mistake.predicted_vulnerable is predicted_vulnerable:
        score += 0.04
    normalized_predicted_cwe = normalize_cwe(predicted_cwe)
    if normalized_predicted_cwe:
        if normalize_cwe(mistake.predicted_cwe) == normalized_predicted_cwe:
            score += 0.06
        if normalize_cwe(mistake.true_cwe) == normalized_predicted_cwe:
            score += 0.03
    return min(score, 1.0)


def _select_diverse(candidates: list[Mistake], context_k: int) -> list[Mistake]:
    if context_k <= 0:
        return []
    selected: list[Mistake] = []
    remaining = list(candidates)
    while remaining and len(selected) < context_k:
        if not selected:
            selected.append(remaining.pop(0))
            continue
        selected_cwes = {normalize_cwe(m.true_cwe) for m in selected if normalize_cwe(m.true_cwe)}
        selected_failures = {m.failure_type for m in selected}
        selected_samples = {m.sample_id for m in selected}

        def mmr_score(mistake: Mistake) -> float:
            normalized_cwe = normalize_cwe(mistake.true_cwe)
            cwe_diversity = 0.08 if normalized_cwe and normalized_cwe not in selected_cwes else 0.0
            failure_diversity = 0.04 if mistake.failure_type not in selected_failures else 0.0
            sample_diversity = 0.03 if mistake.sample_id not in selected_samples else 0.0
            redundancy = max(_token_jaccard(mistake.code, chosen.code) for chosen in selected)
            return mistake.similarity + cwe_diversity + failure_diversity + sample_diversity - 0.18 * redundancy

        best_index = max(range(len(remaining)), key=lambda i: mmr_score(remaining[i]))
        selected.append(remaining.pop(best_index))
    return selected


def _format_rag_context(
    selected: list[Mistake],
    candidates: list[Mistake],
    predicted_vulnerable: bool | None,
    predicted_cwe: str | None,
    snippet_chars: int,
) -> str:
    if not selected:
        return "No relevant mistake-memory evidence was retrieved."
    cwe_counts = Counter(
        normalize_cwe(m.true_cwe)
        for m in selected
        if m.true_vulnerable and normalize_cwe(m.true_cwe)
    )
    confusion_counts = Counter(
        f"{normalize_cwe(m.predicted_cwe) or 'missing'} -> {normalize_cwe(m.true_cwe) or 'unknown'}"
        for m in selected
        if normalize_cwe(m.predicted_cwe) != normalize_cwe(m.true_cwe)
    )
    cwe_signal = _format_counter(cwe_counts)
    confusion_signal = _format_counter(confusion_counts)
    strongest = max((m.similarity for m in candidates), default=0.0)
    parts = [
        "RAG context from SQLite mistake memory.",
        f"Candidates considered: {len(candidates)}; selected evidence rows: {len(selected)}; strongest similarity: {strongest:.3f}.",
        f"Baseline prediction for retrieval: vulnerable={predicted_vulnerable}, cwe={normalize_cwe(predicted_cwe)}.",
        f"CWE signal among selected vulnerable mistakes: {cwe_signal}.",
        f"Observed repeated confusions: {confusion_signal}.",
        "Use these rows as retrieved evidence. Prefer patterns that match the new code; ignore rows that only share names or syntax.",
        "",
        "Selected evidence:",
    ]
    for index, mistake in enumerate(selected, 1):
        parts.append(_format_rag_evidence(mistake, index, snippet_chars))
    return "\n".join(parts)


def _format_counter(counter: Counter) -> str:
    if not counter:
        return "none"
    return ", ".join(f"{key} ({count})" for key, count in counter.most_common(4))


def _format_rag_evidence(mistake: Mistake, index: int, snippet_chars: int) -> str:
    return f"""Evidence {index}: sample={mistake.sample_id}, similarity={mistake.similarity:.3f}, failure={mistake.failure_type}
True: vulnerable={mistake.true_vulnerable}, cwe={normalize_cwe(mistake.true_cwe)}, location={mistake.true_location}
Wrong prediction: vulnerable={mistake.predicted_vulnerable}, cwe={normalize_cwe(mistake.predicted_cwe)}, location={mistake.predicted_location}
Relevant code excerpt:
```c
{_compact_code(mistake.code, snippet_chars)}
```"""


def _compact_code(code: str, limit: int) -> str:
    if len(code) <= limit:
        return code
    keywords = (
        "strcpy",
        "strncpy",
        "sprintf",
        "snprintf",
        "gets",
        "scanf",
        "printf",
        "system",
        "fopen",
        "realpath",
        "malloc",
        "free",
        "memcpy",
        "memmove",
        "assert",
        "mysql",
        "sqlite",
        "select",
        "while",
    )
    lines = code.splitlines()
    chosen_indexes: set[int] = set()
    for i, line in enumerate(lines):
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            chosen_indexes.update(range(max(0, i - 1), min(len(lines), i + 2)))
    if not chosen_indexes:
        return code[:limit].rstrip()
    excerpt_lines: list[str] = []
    total = 0
    previous = -2
    for i in sorted(chosen_indexes):
        line = lines[i]
        prefix = "...\n" if i > previous + 1 and excerpt_lines else ""
        addition = f"{prefix}{i + 1}: {line}"
        if total + len(addition) + 1 > limit:
            break
        excerpt_lines.append(addition)
        total += len(addition) + 1
        previous = i
    return "\n".join(excerpt_lines).rstrip()


def _token_jaccard(left: str, right: str) -> float:
    left_tokens = set(_code_tokens(left))
    right_tokens = set(_code_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _code_tokens(code: str) -> list[str]:
    token = []
    tokens = []
    for ch in code:
        if ch.isalnum() or ch == "_":
            token.append(ch.lower())
        elif token:
            tokens.append("".join(token))
            token = []
    if token:
        tokens.append("".join(token))
    return tokens
