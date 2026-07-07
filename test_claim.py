import sys
import os

# Add the project root to the path
sys.path.append(os.path.abspath('.'))

from core.utils.helpers import is_valid_claim

claims = [
    "Revenue grew 40% in Q1.",
    "The company generated $5 million in revenue.",
    "Apple employs 100,000 people.",
    "Tesla sold 1.8M vehicles.",
    "The building costs $50M.",
    "Revenue was $10M.",
    "It costs $5."
]

for c in claims:
    print(f"{c!r}: {is_valid_claim(c)}")
