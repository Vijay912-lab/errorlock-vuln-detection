# ErrorLock Benchmark Report

Model: `qwen2.5-coder:1.5b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 150 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.127 |
| ErrorLock | 0.647 | 0.694 | 0.840 | 0.760 | 0.000 | 0.227 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
