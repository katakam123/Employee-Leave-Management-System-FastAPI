from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import require_roles
from app.database import get_db
from app.models.models import (
    User,
    UserRole,
    Department,
    Employee,
)
from app.schemas.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    EmployeeResponse,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=201
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    existing = db.scalar(
        select(Department).where(
            Department.department_name
            == data.department_name
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Department name already exists"
        )

    department = Department(**data.model_dump())

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.get(
    "",
    response_model=list[DepartmentResponse]
)
def get_departments(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends()
):

    return db.scalars(
        select(Department)
        .offset(skip)
        .limit(limit)
    ).all()


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends()
):

    department = db.get(
        Department,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse
)
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    department = db.get(
        Department,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    values = data.model_dump(
        exclude_unset=True
    )

    if "department_name" in values:

        existing = db.scalar(
            select(Department).where(
                Department.department_name
                == values["department_name"],
                Department.id != department_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Department name already exists"
            )

    for key, value in values.items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)

    return department


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    department = db.get(
        Department,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    active_employee = db.scalar(
        select(Employee).where(
            Employee.department_id == department_id,
            Employee.is_active.is_(True)
        )
    )

    if active_employee:
        raise HTTPException(
            status_code=400,
            detail=(
                "Department with active employees "
                "cannot be deleted"
            )
        )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }


@router.get(
    "/{department_id}/employees",
    response_model=list[EmployeeResponse]
)
def department_employees(
    department_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends()
):

    department = db.get(
        Department,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return db.scalars(
        select(Employee)
        .where(
            Employee.department_id == department_id
        )
        .offset(skip)
        .limit(limit)
    ).all()