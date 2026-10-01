from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.auth.security import require_roles
from app.database import get_db
from app.models.models import (
    User,
    UserRole,
    Employee,
    Department,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    total_employees = db.scalar(
        select(func.count(Employee.id))
    ) or 0

    active_employees = db.scalar(
        select(func.count(Employee.id))
        .where(Employee.is_active.is_(True))
    ) or 0

    departments = db.execute(
        select(
            Department.department_name,
            func.count(Employee.id)
        )
        .join(
            Employee,
            Employee.department_id == Department.id,
            isouter=True
        )
        .group_by(Department.id)
    ).all()

    employees_per_department = {
        name: count
        for name, count in departments
    }

    pending_leaves = db.scalar(
        select(func.count(LeaveRequest.id))
        .where(
            LeaveRequest.status
            == LeaveStatus.PENDING
        )
    ) or 0

    today = date.today()

    employees_on_leave = db.scalar(
        select(
            func.count(
                func.distinct(
                    LeaveRequest.employee_id
                )
            )
        )
        .where(
            LeaveRequest.status
            == LeaveStatus.APPROVED,
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        )
    ) or 0

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "employees_per_department":
            employees_per_department,
        "pending_leave_requests": pending_leaves,
        "employees_on_leave_today":
            employees_on_leave
    }


@router.get("/leave-summary")
def leave_summary(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    results = db.execute(
        select(
            LeaveRequest.leave_type,
            LeaveRequest.status,
            func.count(LeaveRequest.id)
        )
        .where(
            func.extract(
                "month",
                LeaveRequest.start_date
            ) == month,
            func.extract(
                "year",
                LeaveRequest.start_date
            ) == year
        )
        .group_by(
            LeaveRequest.leave_type,
            LeaveRequest.status
        )
    ).all()

    return {
        "year": year,
        "month": month,
        "summary": [
            {
                "leave_type": leave_type,
                "status": status,
                "count": count
            }
            for leave_type, status, count in results
        ]
    }