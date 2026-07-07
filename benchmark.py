import asyncio
import json
import time
import os
import sys

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
The building costs $5 million to maintain annually.
They acquired a small startup for $2 million in cash.
"""

async def run_benchmark(iterations: int, output_file: str):
    print(f"Running benchmark for {iterations} iterations...")
    results_list = []
    
    groq = GroqService()
    search = SearchService()
    verifier = VerificationService()
    
    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations} started...")
        start_t = time.time()
        
        claims = await detect_claims(TEXT, max_claims=10, groq_service=groq)
        verification_response = await verifier.verify_all(claims, document_excerpt=TEXT)
        
        iteration_result = {
            "iteration": i + 1,
            "claim_count": len(claims),
            "claims": claims,
            "trust_score": verification_response.trust_score,
            "verdicts": [c.verdict.value for c in verification_response.claims],
            "confidences": [c.confidence for c in verification_response.claims],
            "time_taken": time.time() - start_t
        }
        results_list.append(iteration_result)
        
        # Summary for this run
        counts = {"Verified": 0, "Inaccurate": 0, "Misleading": 0, "False": 0, "Unverifiable": 0}
        for v in iteration_result["verdicts"]:
            counts[v] = counts.get(v, 0) + 1
            
        print(f"  Iteration {i+1} completed in {iteration_result['time_taken']:.2f}s.")
        print(f"  Claims: {iteration_result['claim_count']}")
        print(f"  Trust Score: {iteration_result['trust_score']}")
        print(f"  Verdicts: {counts}")
        print("-" * 30)
        
        if i < iterations - 1:
            print("Sleeping for 10 seconds to respect Groq rate limits...")
            await asyncio.sleep(10)
        
    with open(output_file, 'w') as f:
        json.dump(results_list, f, indent=2)
        
    print(f"Saved benchmark results to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "final":
        output = "final_results.json"
    else:
        output = "baseline_results.json"
    asyncio.run(run_benchmark(5, output))
