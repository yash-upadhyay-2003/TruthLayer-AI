CLAIM_EXTRACTION_PROMPT = """You are a fact-checking assistant. Extract ALL verifiable factual statements from the text.

Include every statement that contains: a number, date, year, percentage, financial figure, statistic, named entity with an attributed fact, market claim, geographic fact, or measurable comparison.
Do NOT filter by importance or specificity. Do NOT skip a claim because it seems minor or obvious.
Extract every qualifying statement you find, up to {max_claims} total.
Return ONLY a valid JSON object with a single key "claims" containing an array of strings. No markdown, no explanation.

TEXT:
{text}"""


VERIFICATION_PROMPT = """You are a deterministic fact-checking engine. You must follow these rules exactly and in order. Do not use personal judgement.

CLAIM: {claim}

EVIDENCE:
{evidence}

STEP 1 — CHECK FOR EVIDENCE
If the evidence contains zero sentences relevant to the claim topic, output verdict=Unverifiable, confidence=0, correct_fact="", and stop.

STEP 2 — CHECK FOR DIRECT CONTRADICTION
If at least one evidence source states a fact that directly and explicitly conflicts with a specific number, date, name, or assertion in the claim, output verdict=False.
Rule: Use False ONLY when the evidence explicitly states the opposite or a conflicting specific value. Example: claim says "X is 15%", evidence says "X is 8%" → False.

STEP 3 — CHECK FOR NUMERIC OR FACTUAL ERROR
If the evidence confirms the general topic but the claim contains a specific number, percentage, date, or named figure that differs from what the evidence states by any amount, output verdict=Inaccurate.
Rule: Use Inaccurate when the claim direction is correct but a specific value is wrong or outdated. Example: claim says "revenue grew 40%", evidence says "revenue grew 22%" → Inaccurate.
Rule: Use Inaccurate when the evidence is more than 2 years older than the claim's implied timeframe.

STEP 4 — CHECK FOR MISSING CRITICAL CONTEXT
If the claim is factually accurate as stated but the evidence reveals a critical qualifier that changes the meaning — such as the figure applying only to a subset, a reversal occurring shortly after, or a condition that was not met — output verdict=Misleading.
Rule: Use Misleading ONLY when the omitted context would cause a reasonable reader to reach a materially wrong conclusion. If the omission is minor, use Verified instead.

STEP 5 — VERIFY
If at least two independent evidence sources confirm the claim's specific values, dates, and assertions without contradiction, output verdict=Verified.
If only one source confirms it and no source contradicts it, output verdict=Verified with confidence capped at 82.
If the evidence is relevant but neither confirms nor contradicts the specific claim values, output verdict=Unverifiable.

PRIORITY ORDER (apply the first matching step):
Unverifiable (no relevant evidence) → False (explicit contradiction) → Inaccurate (wrong value) → Misleading (missing critical context) → Verified (confirmed)

CONFIDENCE RULES:
- Two or more sources confirm: 83-97
- One source confirms, none contradict: 65-82
- Evidence is relevant but inconclusive: 45-64
- Evidence contradicts: 70-97 (high confidence in the False/Inaccurate verdict)
- No relevant evidence: 0-30
Never return 100. Never return a value above 97.

correct_fact rules:
- If Verified: return empty string ""
- If False or Inaccurate: return ONE sentence stating the correct value from the evidence (max 15 words). Example: "Tesla sold ~1.8M vehicles in 2023."
- If Misleading: return ONE sentence stating the missing context (max 15 words).
- Never write multiple sentences. Never use CAGR formulas. Never explain.

Reasoning rules:
- Write exactly 2 sentences.
- Sentence 1: state what the evidence says about the claim.
- Sentence 2: state why that evidence leads to this specific verdict.
- Do not repeat the claim text. Do not speculate.

Respond ONLY with valid JSON. No markdown. No explanation outside the JSON.
{{
  "verdict": "Verified" | "Inaccurate" | "Misleading" | "False" | "Unverifiable",
  "confidence": <integer 0-97>,
  "correct_fact": "<one short sentence or empty string>",
  "reasoning": "<exactly 2 sentences>"
}}"""


SUMMARY_PROMPT = """You are an AI analyst. Generate a concise document trust summary.

VERIFICATION RESULTS:
{results_summary}

Write a 2-3 sentence professional summary covering what the document claims, how many were verified vs false, and overall reliability. Be direct. Output plain text only."""
