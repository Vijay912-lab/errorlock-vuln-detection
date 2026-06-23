# ErrorLock Benchmark Report

Model: `qwen2.5-coder:0.5b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 20 total, 8 memory-build train, 12 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| ErrorLock | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.500 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
