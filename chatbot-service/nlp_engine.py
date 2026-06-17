"""Rule-based NLP engine for event planning queries.

Replace `generate_llm_response()` with OpenAI / AWS Bedrock calls when ready.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ChatResponse:
    reply: str
    intent: str
    confidence: float
    suggestions: list[str]


INTENT_PATTERNS: dict[str, list[str]] = {
    "venue": [
        r"\bvenue\b",
        r"\blocation\b",
        r"\bwhere\b.*\b(event|host|hold)\b",
        r"\bballroom\b",
        r"\bresort\b",
        r"\bhotel\b",
        r"\bplace\b.*\b(book|rent)\b",
    ],
    "booking_policy": [
        r"\bcancel\b",
        r"\brefund\b",
        r"\bdeposit\b",
        r"\bpolicy\b",
        r"\bterms\b",
        r"\bcontract\b",
        r"\bbooking\b.*\b(process|policy|rule)\b",
    ],
    "budget": [
        r"\bbudget\b",
        r"\bcost\b",
        r"\bprice\b",
        r"\bhow much\b",
        r"\bafford\b",
        r"\bexpensive\b",
        r"\bcheap\b",
        r"\binr\b",
        r"\busd\b",
    ],
    "catering": [
        r"\bfood\b",
        r"\bcater\b",
        r"\bmenu\b",
        r"\bbuffet\b",
        r"\bdrink\b",
        r"\bbeverage\b",
        r"\bvegetarian\b",
        r"\bvegan\b",
    ],
    "decor": [
        r"\bdecor\b",
        r"\bdecoration\b",
        r"\bfloral\b",
        r"\btheme\b",
        r"\blighting\b",
        r"\bstage\b",
    ],
    "photography": [
        r"\bphoto\b",
        r"\bvideo\b",
        r"\bcamera\b",
        r"\bdrone\b",
        r"\bcinematograph\b",
    ],
    "timeline": [
        r"\btimeline\b",
        r"\bschedule\b",
        r"\bwhen\b.*\b(start|plan|book)\b",
        r"\bhow long\b",
        r"\bdeadline\b",
        r"\bweeks?\s+before\b",
    ],
    "greeting": [
        r"^(hi|hello|hey|good\s+(morning|afternoon|evening))\b",
        r"\bhow are you\b",
    ],
    "thanks": [
        r"\bthank(s| you)\b",
        r"\bappreciate\b",
    ],
}

RESPONSE_MATRIX: dict[str, str] = {
    "venue": (
        "We partner with venues across three tiers: budget-friendly community halls, "
        "premium hotel ballrooms, and exclusive 5-star resorts. Share your city, guest count, "
        "and event type — I'll help narrow the best options. Most venues require a 30–50% "
        "deposit to hold your date."
    ),
    "booking_policy": (
        "Our standard booking policy: 40% deposit to confirm, 40% due 30 days before the event, "
        "and the balance 7 days prior. Cancellations 60+ days out receive an 80% refund; "
        "30–59 days receive 50%; within 30 days deposits are non-refundable. "
        "All terms are outlined in your signed service agreement."
    ),
    "budget": (
        "Budget tiers guide our packages: Low (up to $5K / ₹4.15L) uses standard venues and decor; "
        "Medium ($5K–$25K / ₹4.15L–₹20.75L) adds premium catering and photography; "
        "High/Luxury ($25K+ / ₹20.75L+) includes 5-star venues, celebrity hosts, and drone coverage. "
        "Use the Estimate form on this page for a personalized breakdown!"
    ),
    "catering": (
        "Catering scales with your tier: standard buffets for budget events, live multi-cuisine "
        "counters for mid-tier, and celebrity chef-curated menus for luxury celebrations. "
        "We accommodate vegetarian, vegan, halal, and allergy-specific menus — just note "
        "requirements in your inquiry."
    ),
    "decor": (
        "Decor packages range from elegant centerpieces and stage backdrops (standard) to "
        "immersive themed installations with LED walls and custom fabrication (luxury). "
        "We recommend locking your decor theme 8–10 weeks before the event."
    ),
    "photography": (
        "Photography options: basic event coverage (Low tier), mid-tier photo + video with "
        "a dedicated editor (Medium), and cinematic multi-camera + drone packages (High/Luxury). "
        "Book early — top photographers fill up 3–4 months ahead for peak season."
    ),
    "timeline": (
        "A typical planning timeline: 12–16 weeks for luxury events, 8–10 weeks for medium, "
        "and 6–8 weeks minimum for budget-friendly celebrations. Start with venue booking, "
        "then catering, decor, and entertainment. Submit an estimate request to get a "
        "custom week-by-week plan."
    ),
    "greeting": (
        "Hello! I'm your AI Event Assistant. I can help with venues, budgets, catering, "
        "decor, photography, booking policies, and planning timelines. What would you like to know?"
    ),
    "thanks": (
        "You're welcome! If you have more questions about your event, I'm here to help. "
        "You can also submit the inquiry form for a detailed cost estimate."
    ),
    "fallback": (
        "I'm specialized in event planning — venues, budgets, catering, decor, and timelines. "
        "Could you rephrase your question, or try asking about one of those topics? "
        "For a full personalized quote, use the Estimate form on this page."
    ),
}

FOLLOW_UP_SUGGESTIONS: dict[str, list[str]] = {
    "venue": ["What deposit is required?", "Do you have outdoor venue options?"],
    "booking_policy": ["What is the cancellation refund?", "When is the final payment due?"],
    "budget": ["What does a medium-tier wedding include?", "Can I pay in INR?"],
    "catering": ["Do you offer vegan menus?", "How many live counters in premium tier?"],
    "decor": ["How early should I finalize decor?", "Can you match a custom theme?"],
    "photography": ["Is drone coverage included in luxury?", "How many photographers for medium tier?"],
    "timeline": ["When should I book a wedding venue?", "Minimum planning time for corporate events?"],
    "greeting": ["Tell me about venue options", "What's your cancellation policy?"],
    "thanks": ["Help me plan a corporate event", "What budget tier fits $15,000?"],
    "fallback": ["Venue recommendations", "Budget breakdown", "Booking policy"],
}


def detect_intent(message: str) -> tuple[str, float]:
    text = message.lower().strip()
    best_intent = "fallback"
    best_score = 0.0

    for intent, patterns in INTENT_PATTERNS.items():
        matches = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        if matches > best_score:
            best_score = matches
            best_intent = intent

    confidence = min(0.95, 0.5 + best_score * 0.2) if best_intent != "fallback" else 0.4
    return best_intent, confidence


def generate_llm_response(message: str, context: dict[str, Any] | None = None) -> str | None:
    """Placeholder for OpenAI / AWS Bedrock integration.

    Example (OpenAI):
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
        )
        return response.choices[0].message.content

    Example (AWS Bedrock):
        import boto3
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        # InvokeModel with anthropic.claude or amazon.titan
    """
    _ = message, context
    return None


def process_message(message: str, session_context: dict[str, Any] | None = None) -> ChatResponse:
    llm_reply = generate_llm_response(message, session_context)
    if llm_reply:
        return ChatResponse(
            reply=llm_reply,
            intent="llm",
            confidence=0.99,
            suggestions=FOLLOW_UP_SUGGESTIONS.get("fallback", []),
        )

    intent, confidence = detect_intent(message)
    reply = RESPONSE_MATRIX.get(intent, RESPONSE_MATRIX["fallback"])
    suggestions = FOLLOW_UP_SUGGESTIONS.get(intent, FOLLOW_UP_SUGGESTIONS["fallback"])

    return ChatResponse(
        reply=reply,
        intent=intent,
        confidence=confidence,
        suggestions=suggestions,
    )
