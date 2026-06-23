# ErrorLock Benchmark Report

Model: `gemini-2.5-flash-lite`

Dataset: `data/CASTLE-C250.min.json`

Samples: 8 total, 3 memory-build train, 5 fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.600 | 1.000 | 0.500 | 0.667 | 0.400 | 0.400 |
| ErrorLock | 0.800 | 1.000 | 0.750 | 0.857 | 0.400 | 0.600 |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
