# ErrorLock Benchmark Report

Model: `openai/gpt-oss-120b:free`

Dataset: `data/CASTLE-C250.min.json`

Samples: 20 total, 8 memory-build train, 12 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.833 | 1.000 | 0.750 | 0.857 | 0.333 | 0.500 |
| ErrorLock | 0.750 | 1.000 | 0.625 | 0.769 | 0.083 | 0.583 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
