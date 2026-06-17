"""Seed EventCatalog with default event types."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from shared.database import SessionLocal
from shared.models import EventCatalog

SEED_DATA = [
    {
        "event_type": "wedding",
        "base_price": 8000.0,
        "description": "Full-service wedding planning from ceremony to reception.",
    },
    {
        "event_type": "corporate",
        "base_price": 5000.0,
        "description": "Corporate conferences, product launches, and galas.",
    },
    {
        "event_type": "birthday",
        "base_price": 2000.0,
        "description": "Themed birthday celebrations for all ages.",
    },
    {
        "event_type": "anniversary",
        "base_price": 3500.0,
        "description": "Milestone anniversary parties with custom decor.",
    },
    {
        "event_type": "conference",
        "base_price": 12000.0,
        "description": "Multi-day conferences with AV, catering, and breakout sessions.",
    },
]


def seed_catalog():
    db = SessionLocal()
    try:
        for item in SEED_DATA:
            existing = (
                db.query(EventCatalog)
                .filter(EventCatalog.event_type == item["event_type"])
                .first()
            )
            if not existing:
                db.add(EventCatalog(**item))
        db.commit()
    finally:
        db.close()
