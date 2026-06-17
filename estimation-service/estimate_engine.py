"""Estimation engine: budget classification and package generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class BudgetTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CostBreakdown:
    venue: float
    food: float
    decor: float
    logistics: float

    @property
    def total(self) -> float:
        return self.venue + self.food + self.decor + self.logistics

    def to_dict(self) -> dict[str, float]:
        return {
            "Venue": round(self.venue, 2),
            "Food": round(self.food, 2),
            "Decor": round(self.decor, 2),
            "Logistics": round(self.logistics, 2),
        }


# Budget thresholds in USD (INR converted at ~83)
USD_LOW_MAX = 5000
USD_MEDIUM_MAX = 25000
INR_LOW_MAX = 415000
INR_MEDIUM_MAX = 2075000


def normalize_budget(budget: float, currency: str = "USD") -> tuple[float, str]:
    currency = currency.upper()
    if currency == "INR":
        return budget, "INR"
    return budget, "USD"


def classify_budget(budget: float, currency: str = "USD") -> BudgetTier:
    currency = currency.upper()
    if currency == "INR":
        if budget <= INR_LOW_MAX:
            return BudgetTier.LOW
        if budget <= INR_MEDIUM_MAX:
            return BudgetTier.MEDIUM
        return BudgetTier.HIGH

    if budget <= USD_LOW_MAX:
        return BudgetTier.LOW
    if budget <= USD_MEDIUM_MAX:
        return BudgetTier.MEDIUM
    return BudgetTier.HIGH


def _tier_packages(event_type: str, tier: BudgetTier, location: str) -> dict[str, Any]:
    event_label = event_type.replace("_", " ").title()
    loc = location.strip() or "your chosen city"

    packages = {
        BudgetTier.LOW: {
            "venue": "Community hall or budget-friendly banquet (150–250 guests)",
            "food": "Standard buffet with vegetarian & non-vegetarian options",
            "decor": "Floral centerpieces, stage backdrop, and ambient lighting",
            "logistics": "Local transport, basic sound system, 1 coordinator",
            "extras": [],
            "timeline": [
                f"T-8 weeks: Confirm venue availability in {loc}",
                "T-6 weeks: Finalize guest list and catering menu",
                "T-4 weeks: Book decor vendor and rehearsal slot",
                "T-2 weeks: Run-through with coordinator and vendors",
                "Event day: Setup 6 AM, guest arrival, teardown by midnight",
            ],
        },
        BudgetTier.MEDIUM: {
            "venue": "Premium hotel ballroom or heritage property",
            "food": "Multi-cuisine live counters, dessert bar, premium beverages",
            "decor": "Themed stage design, floral arches, LED wall, photo booth",
            "logistics": "Valet parking, professional AV, 2 coordinators, mid-tier photography",
            "extras": ["Mid-tier photography & videography package", "Guest welcome kits"],
            "timeline": [
                f"T-12 weeks: Site visit and venue contract in {loc}",
                "T-10 weeks: Catering tasting and menu lock-in",
                "T-8 weeks: Decor mood board approval",
                "T-4 weeks: Photography pre-shoot and vendor sync",
                "T-1 week: Final headcount and seating plan",
                "Event day: Full production crew on-site from dawn to close",
            ],
        },
        BudgetTier.HIGH: {
            "venue": "5-star resort or exclusive private estate",
            "food": "Celebrity chef-curated menu, champagne tower, molecular gastronomy station",
            "decor": "Luxury floral installations, custom stage, immersive lighting design",
            "logistics": "VIP concierge, celebrity host/MC, drone coverage, luxury transport fleet",
            "extras": [
                "Celebrity host or live band headline act",
                "Premium drone & cinematic videography",
                "Personal event concierge for every guest",
                "After-party lounge with mixologist",
            ],
            "timeline": [
                f"T-16 weeks: Private venue scouting in {loc} with luxury concierge",
                "T-14 weeks: Celebrity talent booking and rider negotiations",
                "T-10 weeks: Bespoke decor fabrication and 3D walkthrough",
                "T-6 weeks: Drone permit and aerial rehearsal",
                "T-2 weeks: VIP guest logistics and welcome experience design",
                "Event day: White-glove service, live social media team, multi-camera broadcast",
            ],
        },
    }

    pkg = packages[tier]
    return {
        "event_type": event_label,
        "tier": tier.value,
        "location": loc,
        **pkg,
    }


def _compute_breakdown(budget: float, tier: BudgetTier) -> CostBreakdown:
    ratios = {
        BudgetTier.LOW: (0.35, 0.30, 0.20, 0.15),
        BudgetTier.MEDIUM: (0.32, 0.28, 0.22, 0.18),
        BudgetTier.HIGH: (0.30, 0.25, 0.25, 0.20),
    }
    venue_r, food_r, decor_r, logistics_r = ratios[tier]
    return CostBreakdown(
        venue=budget * venue_r,
        food=budget * food_r,
        decor=budget * decor_r,
        logistics=budget * logistics_r,
    )


def generate_estimate(
    event_type: str,
    budget: float,
    location: str,
    currency: str = "USD",
    special_requirements: str | None = None,
) -> dict[str, Any]:
    budget, currency = normalize_budget(budget, currency)
    tier = classify_budget(budget, currency)
    breakdown = _compute_breakdown(budget, tier)
    package = _tier_packages(event_type, tier, location)

    plan_lines = [
        f"Event: {package['event_type']} ({tier.value.upper()} tier)",
        f"Location: {package['location']}",
        f"Budget: {currency} {budget:,.2f}",
        "",
        "Package Highlights:",
        f"  • Venue: {package['venue']}",
        f"  • Food & Beverage: {package['food']}",
        f"  • Decor: {package['decor']}",
        f"  • Logistics: {package['logistics']}",
    ]
    if package["extras"]:
        plan_lines.append("")
        plan_lines.append("Premium Add-ons:")
        for extra in package["extras"]:
            plan_lines.append(f"  • {extra}")

    if special_requirements:
        plan_lines.extend(["", f"Special Requirements Noted: {special_requirements}"])

    plan_lines.extend(["", "Suggested Timeline:"])
    for step in package["timeline"]:
        plan_lines.append(f"  • {step}")

    return {
        "Status": "Success",
        "BudgetTier": tier.value,
        "Currency": currency,
        "EstimatedCostBreakdowns": breakdown.to_dict(),
        "TotalEstimatedCost": round(breakdown.total, 2),
        "SuggestedTimelinePlan": package["timeline"],
        "PackageDetails": {
            "venue": package["venue"],
            "food": package["food"],
            "decor": package["decor"],
            "logistics": package["logistics"],
            "extras": package["extras"],
        },
        "GeneratedPlanText": "\n".join(plan_lines),
    }
