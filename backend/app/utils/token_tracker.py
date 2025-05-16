from collections import defaultdict
import tiktoken

# In-memory token log: {session_id: {"prompt": X, "completion": Y, "total": Z}}
token_usage_log = defaultdict(lambda: {"prompt": 0, "completion": 0, "total": 0})


def count_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def track_tokens(
    session_id: str, prompt: str, completion: str, model: str = "gpt-4"
) -> dict:
    prompt_tokens = count_tokens(prompt, model)
    completion_tokens = count_tokens(completion, model)
    total = prompt_tokens + completion_tokens

    token_usage_log[session_id]["prompt"] += prompt_tokens
    token_usage_log[session_id]["completion"] += completion_tokens
    token_usage_log[session_id]["total"] += total

    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total,
    }


def get_token_usage(session_id: str) -> dict:
    return token_usage_log.get(session_id, {"prompt": 0, "completion": 0, "total": 0})

