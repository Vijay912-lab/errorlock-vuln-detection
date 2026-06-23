# ErrorLock Benchmark Report

Model: `qwen2.5-coder:0.5b`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 20 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |
| ErrorLock | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.050 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
