from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Book Schemas ─────────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Optional[str] = None
    published_year: Optional[int] = None
    total_copies: int = 1

    @field_validator("total_copies")
    @classmethod
    def copies_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("total_copies must be at least 1")
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    total_copies: Optional[int] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    genre: Optional[str]
    published_year: Optional[int]
    total_copies: int
    available_copies: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Member Schemas ────────────────────────────────────────────────────────────

class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    membership_date: date
    is_active: bool

    model_config = {"from_attributes": True}


# ── Loan Schemas ──────────────────────────────────────────────────────────────

class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    due_date: date

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v):
        if v <= date.today():
            raise ValueError("due_date must be in the future")
        return v


class LoanResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: Optional[datetime]
    is_returned: bool
    book: Optional[BookResponse] = None
    member: Optional[MemberResponse] = None

    model_config = {"from_attributes": True}


class ReturnResponse(BaseModel):
    message: str
    loan: LoanResponse

