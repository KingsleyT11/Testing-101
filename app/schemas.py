from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None


class RepairCreate(BaseModel):
    customer_id: int
    device_type: str
    repair_type: str
    price: float
    received_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None
