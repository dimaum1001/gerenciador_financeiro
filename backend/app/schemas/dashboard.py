"""
Pydantic schemas used by the dashboard endpoints.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardSummary(BaseModel):
    """Top level metrics displayed on the dashboard."""

    total_balance: float
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    income_change: float
    expenses_change: float
    current_month: int
    current_year: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_balance": 15750.5,
                "monthly_income": 5000.0,
                "monthly_expenses": 3200.0,
                "monthly_savings": 1800.0,
                "income_change": 5.2,
                "expenses_change": -3.1,
                "current_month": 1,
                "current_year": 2024,
            }
        }
    )


class MonthlyFlow(BaseModel):
    """Cash-flow aggregated by month."""

    month: int
    year: int
    month_name: str
    income: float
    expenses: float
    balance: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "month": 1,
                "year": 2024,
                "month_name": "Jan",
                "income": 4800.0,
                "expenses": 3100.0,
                "balance": 1700.0,
            }
        }
    )


class CategorySummary(BaseModel):
    """Summary grouped by category."""

    category: str
    color: Optional[str] = None
    value: float
    quantity: int
    percentage: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "Alimentacao",
                "color": "#ef4444",
                "value": 1250.0,
                "quantity": 18,
                "percentage": 24.6,
            }
        }
    )


class UpcomingExpense(BaseModel):
    """Expected recurring expense."""

    description: str
    amount: float
    category: Optional[str] = None
    due_date: date
    days_until: int
    status: str


class BudgetStatusItem(BaseModel):
    """Execution data of a single budget."""

    id: uuid.UUID
    category: str
    category_color: Optional[str] = None
    planned: float
    spent: float
    percentage: float
    remaining: float
    status: str


class BudgetStatusSummary(BaseModel):
    """Aggregated overview of the budgets module."""

    total_planned: float
    total_spent: float
    percentage: float
    remaining: float
    status_counts: dict[str, int]
    budgets: list[BudgetStatusItem]


__all__ = [
    "DashboardSummary",
    "MonthlyFlow",
    "CategorySummary",
    "UpcomingExpense",
    "BudgetStatusItem",
    "BudgetStatusSummary",
]
