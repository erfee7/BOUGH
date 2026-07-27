This is the result from a test stream generation with reasoning through OpenRouter using `curl`, saved here for analysing the response format:
```bash
: OPENROUTER PROCESSING

: OPENROUTER PROCESSING

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":"The","reasoning_details":[{"type":"reasoning.text","text":"The","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" user is asking me","reasoning_details":[{"type":"reasoning.text","text":" user is asking me","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" to solve a simple","reasoning_details":[{"type":"reasoning.text","text":" to solve a simple","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" linear equation: x","reasoning_details":[{"type":"reasoning.text","text":" linear equation: x","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" + 5 =","reasoning_details":[{"type":"reasoning.text","text":" + 5 =","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" 12","reasoning_details":[{"type":"reasoning.text","text":" 12","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":". I need to","reasoning_details":[{"type":"reasoning.text","text":". I need to","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" isolate x by","reasoning_details":[{"type":"reasoning.text","text":" isolate x by","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" subtracting 5","reasoning_details":[{"type":"reasoning.text","text":" subtracting 5","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":" from both sides.","reasoning_details":[{"type":"reasoning.text","text":" from both sides.","format":"unknown","index":0}]},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"To","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" solve x +","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" 5 =","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" 12","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":", follow","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" these steps:\n","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"\n**","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"Step 1:**","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" Start","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" with the equation\n","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"x +","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" 5 =","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" 12","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"\n\n**","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"Step 2:**","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" Subtract 5","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" from both sides to","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" isolate x\nx","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" + ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"5 - ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"5 = ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"12 - ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"5\n\n","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"**Step","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" 3:**","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" Simplify\nx","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" = ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"7\n","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"\n✅","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" The","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" answer is","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":" **x = ","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"7**.","role":"assistant"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","choices":[{"index":0,"delta":{"content":"","role":"assistant","reasoning":null},"finish_reason":"stop","native_finish_reason":"stop"}]}

data: {"id":"gen-1785160442-5ORlzdIrlBsDoqBP7E7B","object":"chat.completion.chunk","created":1785160442,"model":"inclusionai/ling-3.0-flash:free","provider":"Novita","service_tier":null,"choices":[{"index":0,"delta":{"content":"","role":"assistant"},"finish_reason":"stop","native_finish_reason":"stop"}],"usage":{"prompt_tokens":40,"completion_tokens":129,"total_tokens":169,"cost":0,"is_byok":false,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0,"video_tokens":0},"cost_details":{"upstream_inference_cost":0,"upstream_inference_prompt_cost":0,"upstream_inference_completions_cost":0},"completion_tokens_details":{"reasoning_tokens":31,"image_tokens":0,"audio_tokens":0}}}

data: [DONE]
```