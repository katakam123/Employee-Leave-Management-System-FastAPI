from datetime import date, timedelta

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.models import (
    Employee,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
)


LEAVE_LIMITS = {
    LeaveType.SICK: 12,
    LeaveType.CASUAL: 10,
    LeaveType.EARNED: 15,
}


def calculate_working_days(
    start_date: date,
    end_date: date
) -> int:

    total = 0
    current = start_date

    while current <= end_date:

        if current.weekday() < 5:
            total += 1

        current += timedelta(days=1)

    return total


def get_used_leave_days(
    db: Session,
    employee_id: int,
    leave_type: LeaveType,
    year: int
) -> int:

    leaves = db.scalars(
        select(LeaveRequest).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == leave_type,
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.start_date >= date(year, 1, 1),
            LeaveRequest.start_date <= date(year, 12, 31)
        )
    ).all()

    return sum(
        leave.total_days
        for leave in leaves
    )


def get_leave_balance(
    db: Session,
    employee_id: int,
    year: int
):

    result = {}

    for leave_type, limit in LEAVE_LIMITS.items():

        used = get_used_leave_days(
            db,
            employee_id,
            leave_type,
            year
        )

        result[leave_type.value] = max(
            0,
            limit - used
        )

    return result


def check_overlap(
    db: Session,
    employee_id: int,
    start_date: date,
    end_date: date
):

    overlapping = db.scalar(
        select(LeaveRequest).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_([
                LeaveStatus.PENDING,
                LeaveStatus.APPROVED
            ]),
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        )
    )

    return overlapping