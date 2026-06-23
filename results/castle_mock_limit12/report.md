# ErrorLock Benchmark Report

Model: `mock-rule-detector`

Dataset: `data/CASTLE-C250.min.json`

Samples: 12 total, 4 memory-build train, 8 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.750 | 0.800 | 0.800 | 0.800 | 0.000 | 0.250 |
| ErrorLock | 0.750 | 0.800 | 0.800 | 0.800 | 0.000 | 0.250 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
