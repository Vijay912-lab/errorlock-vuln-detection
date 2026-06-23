# ErrorLock Benchmark Report

Model: `deepseek-coder:1.3b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 150 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.647 | 0.664 | 0.950 | 0.782 | 0.040 | 0.000 |
| ErrorLock | 0.647 | 0.672 | 0.920 | 0.776 | 0.080 | 0.020 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
