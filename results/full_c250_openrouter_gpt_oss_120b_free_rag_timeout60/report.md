# ErrorLock Benchmark Report

Model: `openai/gpt-oss-120b:free`

Dataset: `data/CASTLE-C250.min.json`

Samples: 250 total, 100 memory-build train, 150 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.593 | 0.831 | 0.490 | 0.616 | 0.207 | 0.433 |
| ErrorLock | 0.667 | 0.847 | 0.610 | 0.709 | 0.053 | 0.520 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: True.
