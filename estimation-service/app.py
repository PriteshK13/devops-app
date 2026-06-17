import json
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from estimate_engine import generate_estimate
from seed_catalog import seed_catalog
from shared.database import get_db, init_db
from shared.models import BookingEstimate, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_catalog()
    yield


app = FastAPI(
    title="Event Estimation & Planning Engine",
    description="Generates event planning packages based on budget and location.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EstimateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    event_type: str = Field(..., min_length=1, max_length=100)
    budget: float = Field(..., gt=0)
    budget_currency: str = Field(default="USD", pattern="^(USD|INR)$")
    location: str = Field(..., min_length=1, max_length=255)
    special_requirements: str | None = None


class EstimateResponse(BaseModel):
    Status: str
    BudgetTier: str
    Currency: str
    EstimatedCostBreakdowns: dict[str, float]
    TotalEstimatedCost: float
    SuggestedTimelinePlan: list[str]
    PackageDetails: dict
    GeneratedPlanText: str
    estimate_id: int | None = None


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "estimation-engine"}


@app.post("/api/estimate", response_model=EstimateResponse)
def create_estimate(payload: EstimateRequest, db: Session = Depends(get_db)):
    try:
        result = generate_estimate(
            event_type=payload.event_type,
            budget=payload.budget,
            location=payload.location,
            currency=payload.budget_currency,
            special_requirements=payload.special_requirements,
        )

        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            user = User(name=payload.name, email=payload.email)
            db.add(user)
            db.flush()

        estimate = BookingEstimate(
            user_id=user.id,
            event_type=payload.event_type,
            budget=payload.budget,
            budget_currency=payload.budget_currency,
            location=payload.location,
            special_requirements=payload.special_requirements,
            generated_plan=result["GeneratedPlanText"],
            total_estimated_cost=result["TotalEstimatedCost"],
            cost_breakdown=json.dumps(result["EstimatedCostBreakdowns"]),
        )
        db.add(estimate)
        db.commit()
        db.refresh(estimate)

        result["estimate_id"] = estimate.id
        return result

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/estimates/{estimate_id}")
def get_estimate(estimate_id: int, db: Session = Depends(get_db)):
    estimate = db.query(BookingEstimate).filter(BookingEstimate.id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return {
        "id": estimate.id,
        "event_type": estimate.event_type,
        "budget": estimate.budget,
        "location": estimate.location,
        "total_estimated_cost": estimate.total_estimated_cost,
        "generated_plan": estimate.generated_plan,
        "cost_breakdown": json.loads(estimate.cost_breakdown or "{}"),
        "created_at": estimate.created_at.isoformat(),
    }
