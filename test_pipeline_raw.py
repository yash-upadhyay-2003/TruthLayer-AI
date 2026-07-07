import sys, os, asyncio
sys.path.append(os.path.abspath('.'))
from core.services.groq_service import GroqService
from core.utils.prompts import CLAIM_EXTRACTION_PROMPT
from core.utils.helpers import safe_json_parse

async def main():
    text = '''
    In Q3 2023, Acme Corp generated $15 million in revenue, a 20% increase from the previous year.
    The company employs around 500 people globally.
    Their flagship product, WidgetX, costs $50 per unit.
    Acme's CEO, Jane Doe, stated that the market is expanding rapidly.
    The building costs $5 million to maintain annually.
    They acquired a small startup for $2 million in cash.
    '''
    groq = GroqService()
    prompt = CLAIM_EXTRACTION_PROMPT.format(text=text, max_claims=10)
    response = await groq.complete(prompt=prompt, max_tokens=1024, temperature=0.0)
    print('RAW RESPONSE:')
    print(response)
    print('PARSED:')
    print(safe_json_parse(response))

asyncio.run(main())
