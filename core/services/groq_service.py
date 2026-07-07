import logging
import asyncio
from groq import AsyncGroq, APIError, APITimeoutError
from core.config import get_groq_api_key, get_model_primary, get_model_fallback

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=get_groq_api_key())
        self.primary_model = get_model_primary()
        self.fallback_model = get_model_fallback()

    async def complete(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0, seed: int = 42, json_mode: bool = False) -> str:
        kwargs = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "seed": seed,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        for model in [self.primary_model, self.fallback_model]:
            kwargs["model"] = model
            retries = 0
            success = False
            while retries < 10:
                try:
                    response = await self.client.chat.completions.create(**kwargs)
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
                    raise ValueError("Empty response from model.")
                except APITimeoutError:
                    logger.warning("Timeout on %s, retrying...", model)
                    retries += 1
                    await asyncio.sleep(2 ** retries)
                except APIError as e:
                    if "429" in str(e) or "503" in str(e):
                        logger.warning("Rate limited on %s (attempt %d). Sleeping...", model, retries)
                        retries += 1
                        await asyncio.sleep(15 + (2 ** retries))
                    elif "model" in str(e).lower() or "decommissioned" in str(e).lower():
                        logger.warning("Model %s unavailable, trying fallback...", model)
                        break # Break while loop to try next model
                    else:
                        raise RuntimeError(f"Groq API error: {e}") from e
                except Exception as e:
                    logger.warning("Error on %s: %s", model, e)
                    break # Break while loop to try next model
            
            if model == self.fallback_model:
                raise RuntimeError("Both models failed or exhausted retries.")
        raise RuntimeError("All Groq models exhausted.")
