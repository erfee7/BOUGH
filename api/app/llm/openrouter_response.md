This is the result from a test stream generation through OpenRouter using `curl`, saved here for analysing the response format:
```bash
: OPENROUTER PROCESSING

: OPENROUTER PROCESSING

: OPENROUTER PROCESSING

: OPENROUTER PROCESSING

: OPENROUTER PROCESSING

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":"Hello","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":",","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":" how","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":" are","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":" you","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":"?","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","choices":[{"index":0,"delta":{"content":"","role":"assistant"},"finish_reason":"stop","native_finish_reason":"stop"}]}

data: {"id":"gen-1783514921-TROS1tEcjn0rUb5bt99Q","object":"chat.completion.chunk","created":1783514921,"model":"openai/gpt-4o-mini","provider":"OpenAI","system_fingerprint":"fp_88876bec1e","service_tier":null,"choices":[{"index":0,"delta":{"content":"","role":"assistant"},"finish_reason":"stop","native_finish_reason":"stop"}],"usage":{"prompt_tokens":15,"completion_tokens":6,"total_tokens":21,"cost":0.0000057915,"is_byok":false,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0,"video_tokens":0},"cost_details":{"upstream_inference_cost":0.00000585,"upstream_inference_prompt_cost":0.00000225,"upstream_inference_completions_cost":0.0000036},"completion_tokens_details":{"reasoning_tokens":0,"image_tokens":0,"audio_tokens":0}}}

data: [DONE]
```