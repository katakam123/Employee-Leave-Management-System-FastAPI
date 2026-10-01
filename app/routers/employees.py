from app.models.models import LeaveRequest
from app.schemas.schemas import LeaveResponse
from app.services.leave_service import get_leave_balance
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
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
    Department,
)
from app.schemas.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=201
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    if db.scalar(
        select(Employee).where(
            Employee.employee_code
            == data.employee_code
        )
    ):
        raise HTTPException(
            status_code=409,
            detail="Employee code already exists"
        )

    if db.scalar(
        select(Employee).where(
            Employee.email == data.email
        )
    ):
        raise HTTPException(
            status_code=409,
            detail="Employee email already exists"
        )

    department = db.get(
        Department,
        data.department_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    employee = Employee(
        **data.model_dump()
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.get(
    "",
    response_model=list[EmployeeResponse]
)
def get_employees(
    name: str | None = None,
    department_id: int | None = None,
    designation: str | None = None,
    employment_type: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "name",
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    query = select(Employee)

    if name:
        query = query.where(
            Employee.name.ilike(f"%{name}%")
        )

    if department_id:
        query = query.where(
            Employee.department_id == department_id
        )

    if designation:
        query = query.where(
            Employee.designation.ilike(
                f"%{designation}%"
            )
        )

    if employment_type:
        query = query.where(
            Employee.employment_type
            == employment_type
        )

    if is_active is not None:
        query = query.where(
            Employee.is_active == is_active
        )

    allowed_sort_fields = {
        "name": Employee.name,
        "salary": Employee.salary,
        "date_of_joining": Employee.date_of_joining,
        "id": Employee.id,
    }

    sort_column = allowed_sort_fields.get(
        sort_by,
        Employee.name
    )

    if order.lower() == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    query = query.offset(skip).limit(limit)

    return db.scalars(query).all()


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if current_user.role == UserRole.EMPLOYEE:

        if employee.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can view only your own profile"
            )

    return employee


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    values = data.model_dump(
        exclude_unset=True
    )

    if "email" in values:

        existing = db.scalar(
            select(Employee).where(
                Employee.email == values["email"],
                Employee.id != employee_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

    if "phone" in values:

        phone = values["phone"]

        if not phone.isdigit() or len(phone) != 10:
            raise HTTPException(
                status_code=422,
                detail="Phone must contain 10 digits"
            )

    if "date_of_joining" in values:

        if values["date_of_joining"] > date.today():
            raise HTTPException(
                status_code=422,
                detail="Joining date cannot be in the future"
            )

    if "department_id" in values:

        department = db.get(
            Department,
            values["department_id"]
        )

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

    for key, value in values.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.HR
        )
    )
):

    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee.is_active = False

    if employee.user:
        employee.user.is_active = False

    db.commit()

    return {
        "message": "Employee soft deleted successfully"
    }
@router.get(
    "/{employee_id}/leaves",
    response_model=list[LeaveResponse]
)
def employee_leaves(
    employee_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role == UserRole.EMPLOYEE:

        if (
            current_user.employee is None
            or current_user.employee.id != employee_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can view only your own leaves"
            )

    employee = db.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return db.scalars(
        select(LeaveRequest)
        .where(
            LeaveRequest.employee_id == employee_id
        )
        .order_by(
            LeaveRequest.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
    ).all()


@router.get(
    "/{employee_id}/leave-balance"
)
def employee_leave_balance(
    employee_id: int,
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role == UserRole.EMPLOYEE:

        if (
            current_user.employee is None
            or current_user.employee.id != employee_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can view only your own balance"
            )

    employee = db.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if year is None:
        year = date.today().year

    balance = get_leave_balance(
        db,
        employee_id,
        year
    )

    return {
        "employee_id": employee_id,
        "year": year,
        "balance": balance
    }