# Deviations from the Approved Proposal

Documented as they happen, per the mid-term evaluator's feedback that
undisclosed deviations (not the deviations themselves) were the real
problem last time. Both changes below were forced by upstream vendor
model retirements discovered on 2026-08-26 while hardening the AI
pipeline for the final submission - not scope changes.

## 1. Gemini model: `gemini-2.5-flash` -> `gemini-3.5-flash`

**Approved:** Google AI Studio - Gemini 2.5 Flash, multimodal receipt
extraction.

**Actual:** `models/gemini-2.5-flash` now returns `404 NOT_FOUND -
"This model ... is no longer available to new users"` on this API
key. The `-latest` alias (`models/gemini-flash-latest`) is reachable
but consistently times out (30s+, `ReadTimeout`). `models/gemini-3.5-
flash` was verified working end-to-end (upload + multimodal
extraction, ~8s, correct structured JSON) and is used instead - same
tier (fast/cheap multimodal flash model), same free-tier pricing
model, same prompt contract. `app/ai/gemini_service.py` documents this
inline.

**Impact:** None on functionality or cost. `GEMINI_MODEL` is a single
constant in `gemini_service.py` - trivial to swap again if Google
retires this one too.

## 2. Groq model: `llama-3.3-70b-versatile` -> `openai/gpt-oss-120b`

**Approved:** Groq Cloud - Llama 3.3 70B, policy compliance + risk
scoring.

**Actual:** `llama-3.3-70b-versatile` was removed from Groq's model
catalog (`404 model_not_found` - confirmed via `client.models.list()`,
it's no longer listed at all). `openai/gpt-oss-120b` is the closest
current equivalent on Groq's free tier (large open-weights model,
sub-2s responses, reliable structured JSON) and is used instead.
`app/ai/groq_service.py` documents this inline.

**Impact:** None on functionality or cost (still Groq free tier).

## 3. Robustness hardening added during this pass (not a deviation, a fix)

Neither the Gemini nor Ollama client had an explicit request timeout,
so a stalled network path could hang the entire pipeline indefinitely
- and because a hang never raises an exception, it silently defeated
the Hybrid Router's fallback-to-Ollama logic (which only triggers on
an exception). Added explicit timeouts to all three AI clients
(Gemini 30s, Groq 20s, Ollama 120s) so a stuck call fails fast and the
Hybrid Router's fallback actually engages the way the proposal
describes ("Hybrid Router auto-switches to Ollama - zero downtime").
