"""End-to-end smoke test: FLUX ad image -> one Drex call = 100-persona swarm + compliance panel.

Run: .venv/bin/python scripts/smoke_test.py
"""
import asyncio
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pixeldrex.drex import FINANCE_MODEL, Drex, choice, image_to_b64, noul, score  # noqa: E402
from pixeldrex.llm import DeepInfra  # noqa: E402

OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

AD_PROMPT = (
    "A sleek modern bank credit card advertisement poster. Bold headline text '0% APR' in large white letters, "
    "a happy young couple holding shopping bags, metallic blue card in the foreground, clean marketing design"
)

TERMS = (
    "Terms sheet, Horizon Rewards Visa: 0% introductory APR on purchases for the first 12 months, "
    "then a variable APR of 24.99%-29.99%. Annual fee $95 (waived first year). Balance transfer fee 5%. "
    "Late fee up to $40."
)

AGES = ["22", "29", "35", "44", "53", "61", "70"]
JOBS = ["college student", "nurse", "software engineer", "small-business owner", "retired teacher",
        "gig driver", "warehouse worker", "lawyer", "stay-at-home parent", "new immigrant"]
FINANCES = ["has $8k of credit card debt", "has excellent credit and no debt", "is rebuilding credit after a default",
            "lives paycheck to paycheck", "is saving for a house"]


def personas(n: int, seed: int = 7) -> list[str]:
    rnd = random.Random(seed)
    return [f"a {rnd.choice(AGES)}-year-old {rnd.choice(JOBS)} who {rnd.choice(FINANCES)}" for _ in range(n)]


async def main() -> None:
    async with DeepInfra() as di, Drex(model=FINANCE_MODEL) as drex:
        img_path = OUT / "smoke_ad.jpg"
        if not img_path.exists():
            t0 = time.perf_counter()
            img_path.write_bytes(await di.image(AD_PROMPT))
            print(f"FLUX image: {time.perf_counter() - t0:.1f}s -> {img_path}")
        img = image_to_b64(img_path)

        people = personas(100)
        questions = {
            f"click_{i:03d}": noul(f"You are {p}. Looking at the ad in Image 1, would you click it to learn more?")
            for i, p in enumerate(people)
        }
        questions |= {
            "trust": score("How trustworthy does the ad in Image 1 look to an average consumer?",
                           ["Very untrustworthy", "Untrustworthy", "Neutral", "Trustworthy", "Very trustworthy"]),
            "apr_misleading": noul("Image 1 is an ad for the card described in the state. Does the ad advertise a "
                                   "0% APR without making clear it is only an introductory rate?"),
            "hides_fee": noul("Does the ad in Image 1 omit the annual fee stated in the terms sheet?"),
            "compliance": choice("How should a bank compliance officer handle the ad in Image 1?", {
                "approve": "Accurate and fully compliant, can run as-is",
                "revise": "Needs disclosure fixes before it can run",
                "reject": "Misleading; cannot run",
            }),
        }

        t0 = time.perf_counter()
        r = await drex.ask(TERMS, questions, images=[img])
        print(f"\nDrex ({r.model}): {len(questions)} questions in ONE call, "
              f"{r.wall_ms:.0f} ms wall, {r.eval_ms} ms model, {r.input_tokens} input tokens")

        clicks = [r.p(q) for q in questions if q.startswith("click_")]
        print(f"Swarm: mean P(click) = {sum(clicks)/len(clicks):.3f}, "
              f"{sum(c > 0.5 for c in clicks)}/100 would click")
        ranked = sorted(zip(clicks, people))
        print("  least likely:", ranked[0][1], f"{ranked[0][0]:.2f}")
        print("  most likely: ", ranked[-1][1], f"{ranked[-1][0]:.2f}")
        print(f"Trust score: {r.score('trust'):.2f} / 4")
        print(f"APR misleading: {r.p('apr_misleading'):.3f}   hides fee: {r.p('hides_fee'):.3f}")
        print(f"Compliance: {r.pick('compliance')}  {json.dumps(r.probs('compliance'))}")
        print("Drex usage:", drex.usage.summary())

        # Same compliance call with a frontier vision LLM, for the comparison panel.
        prompt = (f"{TERMS}\n\nImage 1 is an ad for this card. As a bank compliance officer, answer with JSON: "
                  '{"apr_misleading": true/false, "hides_fee": true/false, "compliance": "approve"|"revise"|"reject"}')
        t0 = time.perf_counter()
        ans = await di.chat(prompt, images=[img], max_tokens=200)
        print(f"\nVision LLM ({(time.perf_counter()-t0)*1000:.0f} ms, compliance only, no swarm): {ans.strip()[:200]}")
        print("LLM usage:", di.usage.summary())

        (OUT / "smoke_result.json").write_text(json.dumps(r.answers, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
