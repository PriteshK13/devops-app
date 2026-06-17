from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    estimates = relationship("BookingEstimate", back_populates="user")


class EventCatalog(Base):
    __tablename__ = "event_catalog"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), unique=True, nullable=False, index=True)
    base_price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BookingEstimate(Base):
    __tablename__ = "booking_estimates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    budget = Column(Float, nullable=False)
    budget_currency = Column(String(10), default="USD")
    location = Column(String(255), nullable=False)
    special_requirements = Column(Text, nullable=True)
    generated_plan = Column(Text, nullable=False)
    total_estimated_cost = Column(Float, nullable=False)
    cost_breakdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="estimates")
