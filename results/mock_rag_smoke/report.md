# ErrorLock Benchmark Report

Model: `mock-rule-detector`

Dataset: `data/sample/sample_castle.json`

Samples: 3 total, 1 memory-build train, 2 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| ErrorLock | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
