from pathlib import Path

from errorlock.memory import MistakeMemory
from errorlock.types import CastleSample, Prediction, ScoredPrediction


def test_memory_inserts_and_retrieves(tmp_path: Path):
    db = MistakeMemory(tmp_path / "m.sqlite")
    sample = CastleSample("a", "void f(){strcpy(a,b);}", True, "CWE-120", "line 1")
    pred = Prediction(False, raw='{"vulnerable": false}')
    scored = ScoredPrediction(sample, pred, "mock", "baseline")
    assert db.add_if_mistake(scored)
    assert db.count() == 1
    retrieved = db.retrieve(CastleSample("b", "void g(){strcpy(x,y);}", True), model="mock")
    assert len(retrieved) == 1
    assert retrieved[0].failure_type == "wrong_binary_label"
    db.close()


def test_rag_context_selects_compact_evidence(tmp_path: Path):
    db = MistakeMemory(tmp_path / "m.sqlite")
    samples = [
        CastleSample("a", "void f(){strcpy(dst,src);}", True, "CWE-120", "strcpy"),
        CastleSample("b", "int main(){system(user);}", True, "CWE-78", "system"),
        CastleSample("c", "FILE *f=fopen(path,\"r\");", True, "CWE-22", "fopen"),
    ]
    for sample in samples:
        pred = Prediction(False, raw='{"vulnerable": false}')
        db.add_if_mistake(ScoredPrediction(sample, pred, "mock", "baseline"))

    context = db.retrieve_rag_context(
        CastleSample("q", "void g(){strcpy(a,b); system(cmd);}", True),
        model="mock",
        candidate_k=3,
        context_k=2,
        snippet_chars=120,
    )

    assert context.candidate_count == 3
    assert len(context.mistakes) == 2
    assert "RAG context from SQLite mistake memory" in context.text
    assert "Selected evidence" in context.text
    db.close()
