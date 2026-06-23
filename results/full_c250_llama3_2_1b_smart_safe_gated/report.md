# ErrorLock Benchmark Report

Model: `llama3.2:1b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 150 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |
| ErrorLock | 0.453 | 0.673 | 0.350 | 0.461 | 0.007 | 0.220 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
