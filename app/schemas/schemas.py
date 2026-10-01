from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal
from app.models.models import (
    UserRole,
    EmploymentType,
    LeaveType,
    LeaveStatus,
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["Employee", "HR", "Admin"] = "Employee"


class DepartmentCreate(BaseModel):
    department_name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=150)
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str
    department_id: int
    designation: str
    salary: float = Field(gt=0)
    date_of_joining: date
    employment_type: EmploymentType
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        return value

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError("Date of joining cannot be in the future")
        return value


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    salary: Optional[float] = Field(default=None, gt=0)
    date_of_joining: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeCreate):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(min_length=1)


class LeaveReject(BaseModel):
    rejection_reason: str = Field(min_length=1)


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: str
    status: LeaveStatus
    approved_by: Optional[int]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)