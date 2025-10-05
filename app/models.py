from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    repairs: list[Repair] = Relationship(back_populates="customer")  # type: ignore[name-defined]


class Repair(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    device_type: str
    repair_type: str
    price: float
    received_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None

    customer: Optional[Customer] = Relationship(back_populates="repairs")
