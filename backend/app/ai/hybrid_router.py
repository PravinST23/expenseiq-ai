"""
Hybrid Router Middleware

Author: Pravin Shanmugavel
Project: ExpenseIQ

Decides which AI vision engine processes a given receipt:

- Sensitive receipts always stay on-device (Ollama / LLaVA) so
  confidential financial data never leaves the network - satisfies
  the RFP's "offline processing for sensitive expense data"
  requirement.
- Non-sensitive receipts are routed to Gemini 2.5 Flash (cloud) for
  best extraction quality.
- If the cloud call fails - free-tier rate limit, quota exhaustion,
  network error - the router transparently falls back to the local
  Ollama model instead of failing the whole pipeline.
"""

from app.ai.gemini_service import gemini_service
from app.ai.ollama_service import ollama_service

RATE_LIMIT_MARKERS = (
    "429",
    "rate limit",
    "quota",
    "resource_exhausted",
    "resource exhausted",
)


class HybridRouter:
    """
    Routes receipt extraction requests to Gemini or Ollama.
    """

    def route(
        self,
        image_path: str,
        is_sensitive: bool,
    ) -> dict:
        """
        Extract a receipt through the correct engine.

        Returns the raw AI JSON result annotated with:
          - _engine: "gemini" or "ollama"
          - _fallback: whether the cloud call failed and Ollama
            was used as a fallback
          - _fallback_reason: human readable reason (or None)
        """

        if is_sensitive:

            return self._run_ollama(
                image_path,
                fallback_reason=None,
            )

        try:

            result = gemini_service.extract_receipt(
                image_path,
            )

            result["_engine"] = "gemini"
            result["_fallback"] = False
            result["_fallback_reason"] = None

            return result

        except Exception as ex:

            message = str(ex).lower()

            is_rate_limited = any(
                marker in message
                for marker in RATE_LIMIT_MARKERS
            )

            if is_rate_limited:
                reason = (
                    "Gemini rate limit / quota exceeded - "
                    "routed to local Ollama fallback."
                )
            else:
                reason = (
                    f"Gemini extraction failed ({ex}) - "
                    "routed to local Ollama fallback."
                )

            print(f"[HybridRouter] {reason}")

            try:

                return self._run_ollama(
                    image_path,
                    fallback_reason=reason,
                )

            except Exception as ollama_ex:

                # Both engines failed - the Gemini failure (usually
                # the actually actionable one, e.g. quota exhaustion)
                # must not get silently replaced by the Ollama
                # connection error just because it happened second.
                # Surface both.
                raise RuntimeError(
                    f"{reason} Ollama fallback also failed: "
                    f"{ollama_ex}"
                ) from ollama_ex

    def _run_ollama(
        self,
        image_path: str,
        fallback_reason: str | None,
    ) -> dict:

        result = ollama_service.extract_receipt(
            image_path,
        )

        result["_engine"] = "ollama"
        result["_fallback"] = fallback_reason is not None
        result["_fallback_reason"] = fallback_reason

        return result


hybrid_router = HybridRouter()
