from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import (
    get_current_user,
    require_roles
)
from app.database import get_db
from app.models.models import (
    User,
    UserRole,
    Employee,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
)
from app.schemas.schemas import (
    LeaveCreate,
    LeaveReject,
    LeaveResponse,
)
from app.services.leave_service import (
    calculate_working_days,
    get_leave_balance,
    check_overlap,
)


router = APIRouter(
    prefix="/leaves",
    tags=["Leave Management"]
)


@router.post(
    "",
    response_model=LeaveResponse,
    status_code=201
)
def apply_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.employee is None:
        raise HTTPException(
            status_code=400,
            detail="User does not have an employee profile"
        )

    employee = current_user.employee

    if not employee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive employees cannot apply for leave"
        )

    if data.end_date < data.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    if data.start_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Leave cannot be applied for past dates"
        )

    total_days = calculate_working_days(
        data.start_date,
        data.end_date
    )

    if total_days == 0:
        raise HTTPException(
            status_code=400,
            detail="Leave must contain at least one working day"
        )

    overlapping = check_overlap(
        db,
        employee.id,
        data.start_date,
        data.end_date
    )

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail="Leave dates overlap with an existing leave"
        )

    balance = get_leave_balance(
        db,
        employee.id,
        data.start_date.year
    )

    if balance[data.leave_type.value] < total_days:
        raise HTTPException(
            status_code=400,
            detail="Insufficient leave balance"
        )

    leave = LeaveRequest(
        employee_id=employee.id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        total_days=total_days,
        reason=data.reason,
        status=LeaveStatus.PENDING
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return leave


@router.get(
    "",
    response_model=list[LeaveResponse]
)
def get_leaves(
    status: LeaveStatus | None = None,
    leave_type: LeaveType | None = None,
    employee_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = select(LeaveRequest)

    if current_user.role == UserRole.EMPLOYEE:

        if current_user.employee is None:
            return []

        query = query.where(
            LeaveRequest.employee_id
            == current_user.employee.id
        )

    elif employee_id:
        query = query.where(
            LeaveRequest.employee_id
            == employee_id
        )

    if status:
        query = query.where(
            LeaveRequest.status == status
        )

    if leave_type:
        query = query.where(
            LeaveRequest.leave_type == leave_type
        )

    if from_date:
        query = query.where(
            LeaveRequest.start_date >= from_date
        )

    if to_date:
        query = query.where(
            LeaveRequest.end_date <= to_date
        )

    return db.scalars(
        query
        .order_by(LeaveRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()


@router.get(
    "/{leave_id}",
    response_model=LeaveResponse
)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    leave = db.get(
        LeaveRequest,
        leave_id
    )

    if leave is None:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if current_user.role == UserRole.EMPLOYEE:

        if (
            current_user.employee is None
            or leave.employee_id
            != current_user.employee.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can view only your own leaves"
            )

    return leave


@router.put(
    "/{leave_id}/approve",
    response_model=LeaveResponse
)
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    leave = db.get(
        LeaveRequest,
        leave_id
    )

    if leave is None:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be approved"
        )

    if (
        current_user.role == UserRole.HR
        and current_user.employee
        and leave.employee_id
        == current_user.employee.id
    ):
        raise HTTPException(
            status_code=403,
            detail="HR cannot approve their own leave"
        )

    leave.status = LeaveStatus.APPROVED
    leave.approved_by = current_user.id

    db.commit()
    db.refresh(leave)

    return leave


@router.put(
    "/{leave_id}/reject",
    response_model=LeaveResponse
)
def reject_leave(
    leave_id: int,
    data: LeaveReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    leave = db.get(
        LeaveRequest,
        leave_id
    )

    if leave is None:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be rejected"
        )

    if (
        current_user.role == UserRole.HR
        and current_user.employee
        and leave.employee_id
        == current_user.employee.id
    ):
        raise HTTPException(
            status_code=403,
            detail="HR cannot reject their own leave"
        )

    leave.status = LeaveStatus.REJECTED
    leave.rejection_reason = data.rejection_reason
    leave.approved_by = current_user.id

    db.commit()
    db.refresh(leave)

    return leave


@router.put(
    "/{leave_id}/cancel",
    response_model=LeaveResponse
)
def cancel_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    leave = db.get(
        LeaveRequest,
        leave_id
    )

    if leave is None:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if current_user.employee is None:
        raise HTTPException(
            status_code=403,
            detail="No employee profile"
        )

    if leave.employee_id != current_user.employee.id:
        raise HTTPException(
            status_code=403,
            detail="You can cancel only your own leave"
        )

    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be cancelled"
        )

    leave.status = LeaveStatus.CANCELLED

    db.commit()
    db.refresh(leave)

    return leave