from pydantic import BaseModel, field_validator
from typing import Optional


class TransactionCreate(BaseModel):
    date: str
    type: str
    amount: float
    description: str
    payment_mode: str
    category: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in ["Expense", "Income"]:
            raise ValueError("type must be Expense or Income")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("description is required")
        return v.strip()


class TransactionUpdate(BaseModel):
    date: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    payment_mode: Optional[str] = None
    category: Optional[str] = None


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0
    monthly_contribution: float
    target_date: Optional[str] = None


class ScenarioInput(BaseModel):
    income_change: float = 0
    expense_change: float = 0
    emi_change: float = 0
    rent_change: float = 0
    months: int = 6
    one_time_cost: float = 0


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
