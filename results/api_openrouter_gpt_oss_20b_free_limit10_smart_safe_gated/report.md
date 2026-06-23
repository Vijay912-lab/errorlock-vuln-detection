# ErrorLock Benchmark Report

Model: `openai/gpt-oss-20b:free`

Dataset: `data/CASTLE-C250.min.json`

Samples: 10 total, 4 memory-build train, 6 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.667 | 1.000 | 0.500 | 0.667 | 0.000 | 0.333 |
| ErrorLock | 0.667 | 1.000 | 0.500 | 0.667 | 0.000 | 0.333 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
