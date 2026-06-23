# ErrorLock Benchmark Report

Model: `qwen2.5-coder:0.5b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 150 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.447 | 0.639 | 0.390 | 0.484 | 0.000 | 0.187 |
| ErrorLock | 0.447 | 0.639 | 0.390 | 0.484 | 0.000 | 0.233 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
