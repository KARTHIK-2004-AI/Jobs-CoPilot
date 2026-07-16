# Diagnosis Report — BUGFIX-001: fit_score = 0

**Defect:** All jobs get assigned `fit_score = 0` during LLM scoring.

---

## 1. Captured Error Output & Diagnosis

During diagnostic testing, we analyzed both local model (Ollama) and cloud Gemini API setups to capture exact failures.

### Failure Case A: Deprecated/Unsupported Model ID (Category B)
When configuring a model ID like `gemini-1.5-flash` or using a model ID not supported by the developer key's tier/version, both the OpenAI-compatible and Native Gemini endpoints return **HTTP 404 Not Found**:

```
2026-07-16 12:51:33,629 - INFO - LLM provider: https://generativelanguage.googleapis.com/v1beta/openai  model: qwen2.5-coder:3b
2026-07-16 12:51:34,347 - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 404 Not Found"
httpx.HTTPStatusError: Client error '404 Not Found' for url 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'
```
* **Explanation:** If the user has a model override `LLM_MODEL` defined in their environment (e.g. `qwen2.5-coder:3b` left over for local testing) but `LLM_URL` is commented out, `llm.py` propagates the local model name to the Gemini endpoint, which returns 404. Furthermore, deprecated models (like `gemini-1.5-flash` which is unavailable for this key) also fail with 404.

### Failure Case B: Gemini Free-Tier Rate Limits (Category C)
When using a valid Gemini model under the free tier, the API has a strict **15 RPM** (Requests Per Minute) limit. Running a batch score of 57 jobs sequentially sends requests faster than 15 RPM. Once request #16 is reached, Google returns **HTTP 429 Resource Exhausted**:

```
LLM request failed with status 429 using key (starts with: AQ.Ab8RN6L). Response: {
  "error": {
    "code": 429,
    "message": "Resource has been exhausted (e.g. queries per minute quota or bandwith)",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```
* **Explanation:** `llm.py` retries up to 5 times with exponential backoff (10s, 20s, 40s, 60s). However, in a large batch of 57 jobs, the backoff delays eventually exceed the total limits or time out, causing the client to crash and write the fallback score `0` to the database.

### Failure Case C: Stale Env Variable Precedence (Category A)
If the user runs their terminal in a session where `GEMINI_API_KEY` is already defined (e.g. with a stale or invalid key), Python's `load_dotenv()` without `override=True` will **not** overwrite the existing key with the correct key from `.env`. This leads to `400 API key not valid` or `401 Unauthorized` errors.

---

## 2. Real Database Path
The actual database path resolved by the application is:
`C:\Users\YS TECH CENTER\.applypilot\applypilot.db`

---

## 3. Proposed Minimal Fixes

Depending on the configuration selected by the user:

1. **Local Model (Ollama)**:
   * Tested with `qwen2.5-coder:3b` and succeeded with `SCORE: 9`.
   * **Fix:** No code changes needed, but ensure `LLM_URL` is set to route requests locally.

2. **Gemini API Model ID & Env Sync**:
   * **Fix 1 (Model ID)**: Standardize default model fallback in `llm.py` to `gemini-2.0-flash` (or newer active model from `ListModels` like `gemini-2.5-flash` or `gemini-3.5-flash`), and prevent propagating local model overrides like `qwen` to Google endpoints if `LLM_URL` is blank.
   * **Fix 2 (Env Override)**: Use `load_dotenv(override=True)` in `config.py` to ensure local `.env` variables correctly overwrite any stale environment variables in the user's active terminal session.
   * **Fix 3 (Multi-key Rotation)**: If the user wants to use Gemini API and has multiple keys, implement a clean, lightweight key rotation in `llm.py` to rotate keys upon receiving HTTP 429 (Rate Limit) or HTTP 401/400 (Invalid Key) errors.
