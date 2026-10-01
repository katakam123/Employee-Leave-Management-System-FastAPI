from fastapi import FastAPI

from app.routers import (
    auth,
    departments,
    employees,
    leaves,
    reports,
)


app = FastAPI(
    title="Employee & Leave Management System",
    description=(
        "HR backend using FastAPI, MySQL, "
        "JWT and SQLAlchemy"
    ),
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Employee & Leave Management API is running"
    }