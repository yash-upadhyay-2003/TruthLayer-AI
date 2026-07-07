import sys
import os
import asyncio

sys.path.append(os.path.abspath('.'))

from core.services.groq_service import GroqService
from core.services.search_service import SearchService
from core.services.verification_service import VerificationService
from core.utils.claim_detector import detect_claims

TEXT = """
In Q3 2023, Acme Corp generated $15 million in revenue, a 20% increase from the previous year.
The company employs around 500 people globally.
Their flagship product, WidgetX, costs $50 per unit.
Acme's CEO, Jane Doe, stated that the market is expanding rapidly.
"""

async def run_repeatability_test(iterations: int = 3):
    print(f"Running repeatability test for {iterations} iterations...")
    groq = GroqService()
    search = SearchService()
    verifier = VerificationService()
    
    baseline_result = None
    
    for i in range(iterations):
        print(f"Iteration {i+1}...")
        claims = await detect_claims(TEXT, max_claims=5, groq_service=groq)
        verification_response = await verifier.verify_all(claims, document_excerpt=TEXT)
        
        current_result = {
            "claim_count": len(claims),
            "claims": claims,
            "trust_score": verification_response.trust_score,
            "verdicts": [c.verdict.value for c in verification_response.claims],
            "confidences": [c.confidence for c in verification_response.claims],
        }
        
        if baseline_result is None:
            baseline_result = current_result
            print("  Baseline established.")
        else:
            try:
                assert current_result["claim_count"] == baseline_result["claim_count"], "Claim count mismatch!"
                assert current_result["claims"] == baseline_result["claims"], "Claims mismatch!"
                assert current_result["trust_score"] == baseline_result["trust_score"], "Trust score mismatch!"
                assert current_result["verdicts"] == baseline_result["verdicts"], "Verdicts mismatch!"
                assert current_result["confidences"] == baseline_result["confidences"], "Confidences mismatch!"
                print("  Strict determinism verified.")
            except AssertionError as e:
                print(f"  FAIL: {e}")
                sys.exit(1)
                
        # Sleep to avoid rate limits
        if i < iterations - 1:
            await asyncio.sleep(5)
            
    print("ALL REPEATABILITY TESTS PASSED.")

if __name__ == "__main__":
    asyncio.run(run_repeatability_test())
