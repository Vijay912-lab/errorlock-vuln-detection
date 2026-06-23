# ErrorLock Benchmark Report

Model: `phi3:mini`

Dataset: `data/CASTLE-C250.min.json`

Samples: 20 total, 8 memory-build train, 12 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.000 |
| ErrorLock | 0.750 | 0.727 | 1.000 | 0.842 | 0.000 | 0.083 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
