# ErrorLock Aggregate Analysis

## api_gemini_2_5_flash_lite_limit8

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini-2.5-flash-lite | baseline | 5 | 0.600 | 1.000 | 0.500 | 0.667 | 0.400 | 0.400 |
| gemini-2.5-flash-lite | errorlock | 5 | 0.800 | 1.000 | 0.750 | 0.857 | 0.400 | 0.600 |

## api_gemini_2_5_flash_lite_limit8_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini-2.5-flash-lite | baseline | 5 | 0.600 | 0.750 | 0.750 | 0.750 | 0.000 | 0.600 |
| gemini-2.5-flash-lite | errorlock | 5 | 0.600 | 0.750 | 0.750 | 0.750 | 0.000 | 0.600 |

## api_openrouter_gpt_oss_120b_free_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-oss-120b:free | baseline | 12 | 0.833 | 1.000 | 0.750 | 0.857 | 0.333 | 0.500 |
| openai/gpt-oss-120b:free | errorlock | 12 | 0.750 | 1.000 | 0.625 | 0.769 | 0.083 | 0.583 |

## api_openrouter_gpt_oss_120b_free_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-oss-120b:free | baseline | 12 | 0.833 | 1.000 | 0.750 | 0.857 | 0.333 | 0.583 |
| openai/gpt-oss-120b:free | errorlock | 12 | 0.917 | 1.000 | 0.875 | 0.933 | 0.083 | 0.750 |

## api_openrouter_gpt_oss_20b_free_limit10

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-oss-20b:free | baseline | 6 | 0.667 | 1.000 | 0.500 | 0.667 | 0.333 | 0.333 |
| openai/gpt-oss-20b:free | errorlock | 6 | 0.833 | 1.000 | 0.750 | 0.857 | 0.167 | 0.667 |

## api_openrouter_gpt_oss_20b_free_limit10_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-oss-20b:free | baseline | 6 | 0.667 | 1.000 | 0.500 | 0.667 | 0.000 | 0.333 |
| openai/gpt-oss-20b:free | errorlock | 6 | 0.667 | 1.000 | 0.500 | 0.667 | 0.000 | 0.333 |

## castle_mock_limit12

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mock-rule-detector | baseline | 8 | 0.750 | 0.800 | 0.800 | 0.800 | 0.000 | 0.250 |
| mock-rule-detector | errorlock | 8 | 0.750 | 0.800 | 0.800 | 0.800 | 0.000 | 0.250 |

## deepseek_coder_1_3b_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder:1.3b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.083 | 0.000 |
| deepseek-coder:1.3b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.000 |

## full_c250_deepseek_coder_1_3b_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder:1.3b | baseline | 150 | 0.647 | 0.664 | 0.950 | 0.782 | 0.040 | 0.000 |
| deepseek-coder:1.3b | errorlock | 150 | 0.647 | 0.672 | 0.920 | 0.776 | 0.080 | 0.020 |

## full_c250_deepseek_coder_1_3b_smart_safe_gated_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder:1.3b | baseline | 150 | 0.647 | 0.664 | 0.950 | 0.782 | 0.040 | 0.000 |
| deepseek-coder:1.3b | errorlock | 150 | 0.647 | 0.660 | 0.970 | 0.785 | 0.013 | 0.020 |

## full_c250_llama3_2_1b_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:1b | baseline | 150 | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |
| llama3.2:1b | errorlock | 150 | 0.453 | 0.673 | 0.350 | 0.461 | 0.007 | 0.220 |

## full_c250_llama3_2_1b_smart_safe_gated_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:1b | baseline | 150 | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |
| llama3.2:1b | errorlock | 150 | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |

## full_c250_openrouter_gpt_oss_120b_free_rag_timeout60

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-oss-120b:free | baseline | 150 | 0.593 | 0.831 | 0.490 | 0.616 | 0.207 | 0.433 |
| openai/gpt-oss-120b:free | errorlock | 150 | 0.667 | 0.847 | 0.610 | 0.709 | 0.053 | 0.520 |

## full_c250_qwen2_5_coder_0_5b_all_memory_repair_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.050 |

## full_c250_qwen2_5_coder_0_5b_errorlock_prompt_v2_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 150 | 0.447 | 0.639 | 0.390 | 0.484 | 0.000 | 0.187 |
| qwen2.5-coder:0.5b | errorlock | 150 | 0.447 | 0.639 | 0.390 | 0.484 | 0.000 | 0.233 |

## full_c250_qwen2_5_coder_0_5b_prompt_v2_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 150 | 0.413 | 0.607 | 0.340 | 0.436 | 0.013 | 0.173 |
| qwen2.5-coder:0.5b | errorlock | 150 | 0.407 | 0.596 | 0.340 | 0.433 | 0.007 | 0.213 |

## full_c250_qwen2_5_coder_0_5b_rag_memory_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |

## full_c250_qwen2_5_coder_0_5b_selective_override

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.027 |
| qwen2.5-coder:0.5b | errorlock | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.200 |

## full_c250_qwen2_5_coder_0_5b_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.027 |
| qwen2.5-coder:0.5b | errorlock | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.200 |

## full_c250_qwen2_5_coder_0_5b_smart_safe_gated_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.027 |
| qwen2.5-coder:0.5b | errorlock | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.200 |

## full_c250_qwen2_5_coder_0_5b_top3_current_prompt_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 20 | 0.650 | 0.684 | 0.929 | 0.788 | 0.000 | 0.000 |

## full_c250_qwen2_5_coder_1_5b_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 150 | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.127 |
| qwen2.5-coder:1.5b | errorlock | 150 | 0.647 | 0.694 | 0.840 | 0.760 | 0.000 | 0.227 |

## full_c250_qwen2_5_coder_1_5b_smart_safe_gated_binary_locked

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 150 | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.127 |
| qwen2.5-coder:1.5b | errorlock | 150 | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.220 |

## llama3_2_1b_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:1b | baseline | 12 | 0.750 | 0.857 | 0.750 | 0.800 | 0.000 | 0.250 |
| llama3.2:1b | errorlock | 12 | 0.750 | 0.857 | 0.750 | 0.800 | 0.000 | 0.250 |

## mock_all_memory_smoke

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mock-rule-detector | baseline | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| mock-rule-detector | errorlock | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## mock_gated_smoke

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mock-rule-detector | baseline | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| mock-rule-detector | errorlock | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## mock_rag_smoke

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mock-rule-detector | baseline | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| mock-rule-detector | errorlock | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## mock_smoke

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mock-rule-detector | baseline | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| mock-rule-detector | errorlock | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

## phi3_mini_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phi3:mini | baseline | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.000 |
| phi3:mini | errorlock | 12 | 0.750 | 0.727 | 1.000 | 0.842 | 0.000 | 0.083 |

## qwen2_5_coder_0_5b_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.500 |

## qwen2_5_coder_0_5b_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.417 |

## qwen2_5_coder_0_5b_limit20_topk1

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.583 |

## qwen2_5_coder_0_5b_limit20_topk5

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| qwen2.5-coder:0.5b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.667 |

## qwen2_5_coder_1_5b_limit20

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| qwen2.5-coder:1.5b | errorlock | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.583 |

## qwen2_5_coder_1_5b_limit20_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| qwen2.5-coder:1.5b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.417 |

## qwen2_5_coder_1_5b_limit20_smart_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| qwen2.5-coder:1.5b | errorlock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.583 |

## qwen2_5_coder_1_5b_limit20_smart_safe_gated

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| qwen2.5-coder:1.5b | errorlock | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.667 |

## qwen2_5_coder_1_5b_limit20_smart_safe_gated_rerun

| model | method | n_test | accuracy | precision | recall | f1 | parse_failure_rate | cwe_correct_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| qwen2.5-coder:1.5b | errorlock | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.667 |
