import sys
import os
import asyncio

sys.path.append(os.path.abspath('.'))

from core.services.groq_service import GroqService
from core.utils.claim_detector import detect_claims

async def main():
    text = """
    In Q3 2023, Acme Corp generated $15 million in revenue, a 20% increase from the previous year.
    The company employs around 500 people globally.
    Their flagship product, WidgetX, costs $50 per unit.
    Acme's CEO, Jane Doe, stated that the market is expanding rapidly.
    The building costs $5 million to maintain annually.
    They acquired a small startup for $2 million in cash.
    """
    
    groq = GroqService()
    claims = await detect_claims(text, max_claims=10, groq_service=groq)
    print("FINAL CLAIMS:")
    for i, c in enumerate(claims, 1):
        print(f"{i}. {c}")

if __name__ == '__main__':
    asyncio.run(main())
