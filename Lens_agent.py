"""
Install:
    pip install google-adk GoogleLens

Run:
    python lens_agent/agent.py
    python lens_agent/agent.py --url "https://example.com/image.jpg"
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from google.adk.agents import LlmAgent
from GoogleLens import GoogleLens

def google_image(url: str) -> dict[str, Any]:
    """
    Upload an image URL to Google Lens and return visual search results.

    Args:
        url: Publicly accessible image URL.

    Returns:
        Visual results dict from Google Lens.
    """
    lens = GoogleLens()
    result_url = lens.upload_image(url)
    visual_result = result_url.extract_visual_results()
    return visual_result

lens_agent = LlmAgent(
    name="LensAgent",
    model="gemini-2.5-flash",
    description=(
        "A Google Lens–powered AI agent that takes an image URL, analyzes it "
        "using visual search, and returns structured insights including object "
        "identification, key details, similar matches, and confidence level."
    ),
    instruction="""
You are an advanced visual analysis agent powered by Google Lens.
Your task is to analyze images using the provided `google_image` tool.

INSTRUCTIONS:
1. Take an image URL as input.
2. Pass the URL into the `google_image` function.
3. Carefully analyze the returned visual results.
4. Produce a structured, human-readable response.

OUTPUT FORMAT:
- Main Identification: What is the primary object or subject?
- Category: (e.g., product, landmark, person, animal, artwork, etc.)
- Key Details:
  - Important attributes (color, brand, style, context)
  - Any identifiable text or labels
- Similar Matches:
  - List 3–5 visually similar items or matches
- Confidence Level: (High / Medium / Low)
- Additional Insights:
  - Possible use cases, origin, or relevance
  - Any interesting or non-obvious observations

RULES:
- Be precise and avoid guessing if uncertain.
- If multiple interpretations exist, list them clearly.
- Prioritize the most visually confident matches.
- Keep responses concise but informative.
- Do NOT hallucinate details not supported by the results.

GOAL:
Deliver the most accurate and useful interpretation of the image using Google Lens results.
    """,
    tools=[google_image],
)

def run(url: str) -> str:
    """Run the lens agent on an image URL and return the analysis."""
    response = lens_agent.run(f"Analyze this image: {url}")
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Lens visual analysis agent")
    parser.add_argument("--url", type=str, help="Image URL to analyze")
    args = parser.parse_args()

    if args.url:
        print(run(args.url))
    else:
        # Interactive mode
        print("Lens Agent — Google Lens Visual Analysis")
        print("Type 'quit' to exit\n")
        while True:
            url = input("Image URL: ").strip()
            if url.lower() in ("quit", "exit", "q"):
                break
            if not url:
                continue
            print("\nAnalyzing...\n")
            print(run(url))
            print()
