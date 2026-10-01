# Employee-Leave-Management-System-FastAPI

A complete backend REST API built with **FastAPI** for managing employees, departments, users, and employee leave requests.

The system includes **JWT authentication, role-based access control, MySQL database integration, SQLAlchemy ORM, Alembic migrations, validation, leave business rules, pagination, filtering, sorting, and HR reports**.

---

## 1. Project Overview

The Employee & Leave Management System provides APIs for an organization's HR operations.

### Main Modules

* User Authentication
* JWT Authentication
* Role-Based Access Control
* Department Management
* Employee Management
* Leave Management
* Leave Balance Management
* Employee Search and Filtering
* Pagination and Sorting
* HR Dashboard
* Leave Reports
* MySQL Database
* Alembic Database Migrations

---

## 2. Technology Stack

| Technology    | Purpose                     |
| ------------- | --------------------------- |
| Python 3.9+   | Programming language        |
| FastAPI       | REST API framework          |
| Pydantic      | Request/response validation |
| SQLAlchemy    | ORM                         |
| MySQL         | Database                    |
| Alembic       | Database migrations         |
| JWT           | Authentication              |
| Passlib       | Password hashing            |
| bcrypt        | Secure password hashing     |
| Uvicorn       | ASGI server                 |
| python-dotenv | Environment configuration   |

---

# 3. Project Structure

```text
employee_leave_management/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── departments.py
│   │   ├── employees.py
│   │   ├── leaves.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── leave_service.py
│   │
│   └── auth/
│       ├── __init__.py
│       ├── security.py
│       └── dependencies.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── alembic.ini
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── seed_admin.py
└── README.md
```

---

# 4. Database Design

The application uses MySQL.

### Relationships

```text
Department
     |
     | 1
     |
     | Many
     v
Employees
     |
     | 1
     |
     | Many
     v
Leave Requests
```

Users are associated with employee records:

```text
User
  |
  | 1
  |
  | 0..1
  v
Employee
```

---

# 5. Database Tables

## Users

Stores authentication information.

| Field         | Description           |
| ------------- | --------------------- |
| id            | User ID               |
| name          | User name             |
| email         | Unique email          |
| password_hash | Hashed password       |
| role          | Admin / HR / Employee |
| is_active     | User active status    |
| employee_id   | Linked employee       |
| created_at    | Creation timestamp    |
| updated_at    | Last update timestamp |

---

## Departments

| Field           | Description            |
| --------------- | ---------------------- |
| id              | Department ID          |
| department_name | Unique department name |
| location        | Department location    |
| is_active       | Active/inactive        |
| created_at      | Creation timestamp     |
| updated_at      | Last update timestamp  |

---

## Employees

| Field           | Description                               |
| --------------- | ----------------------------------------- |
| id              | Employee ID                               |
| employee_code   | Unique employee code                      |
| name            | Employee name                             |
| email           | Unique employee email                     |
| phone           | 10-digit phone                            |
| department_id   | Department reference                      |
| designation     | Job designation                           |
| salary          | Employee salary                           |
| date_of_joining | Joining date                              |
| employment_type | Full-Time / Part-Time / Intern / Contract |
| is_active       | Employee status                           |
| created_at      | Creation timestamp                        |
| updated_at      | Last update timestamp                     |

---

## Leave Requests

| Field            | Description                               |
| ---------------- | ----------------------------------------- |
| id               | Leave ID                                  |
| employee_id      | Employee reference                        |
| leave_type       | Sick / Casual / Earned                    |
| start_date       | Leave start date                          |
| end_date         | Leave end date                            |
| total_days       | Working days                              |
| reason           | Leave reason                              |
| status           | Pending / Approved / Rejected / Cancelled |
| approved_by      | Approving user                            |
| rejection_reason | Reason for rejection                      |
| created_at       | Creation timestamp                        |
| updated_at       | Last update timestamp                     |

---

# 6. User Roles

The system has three roles.

## Admin

Admin has full access.

```text
Admin
├── Users
├── Departments
├── Employees
├── Leaves
└── Reports
```

## HR

HR can:

* Manage employees
* View departments
* Approve leaves
* Reject leaves
* View reports

## Employee

Employees can:

* View their own profile
* Apply for their own leave
* View their own leaves
* Cancel their own pending leave
* View their leave balance

---

# 7. Authentication

The API uses JWT authentication.

### Authentication Flow

```text
Register
   |
   v
Password hashed with bcrypt
   |
   v
User stored in MySQL
   |
   v
Login
   |
   v
JWT generated
   |
   v
Client sends JWT
   |
   v
API validates JWT
   |
   v
Role checked
   |
   v
Request allowed/denied
```

JWT tokens expire after **30 minutes**.

---

# 8. Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/employee_leave_db

JWT_SECRET_KEY=change-this-to-a-long-random-secret

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Important

Never commit `.env` to GitHub.

The `.gitignore` file should contain:

```text
.env
.venv/
__pycache__/
*.pyc
```

Use `.env.example` when sharing the project.

---

# 9. MySQL Setup

Open MySQL Workbench or MySQL command line.

Create the database:

```sql
CREATE DATABASE employee_leave_db;
```

Check the database:

```sql
SHOW DATABASES;
```

Select it:

```sql
USE employee_leave_db;
```

Tables will be created through **Alembic migrations**, not through SQLAlchemy `create_all()`.

---

# 10. Installation

## Step 1: Open the Project

Open the project folder in VS Code.

---

## Step 2: Create Virtual Environment

Open the VS Code terminal:

```bash
python -m venv .venv
```

---

## Step 3: Activate Virtual Environment

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

You should see:

```text
(.venv)
```

in the terminal.

---

# 11. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

Verify:

```bash
pip list
```

---

# 12. Configure Database

Create:

```text
.env
```

Example:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/employee_leave_db
JWT_SECRET_KEY=my-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace:

```text
password
```

with your actual MySQL password.

---

# 13. Alembic Migration

The project uses Alembic for database migrations.

## Generate Migration

After creating/updating models:

```bash
alembic revision --autogenerate -m "create employee leave tables"
```

Example output:

```text
Generating alembic/versions/xxxx_create_employee_leave_tables.py
```

---

## Apply Migration

Run:

```bash
alembic upgrade head
```

Expected:

```text
INFO  [alembic.runtime.migration] Running upgrade
```

Check MySQL:

```sql
USE employee_leave_db;

SHOW TABLES;
```

Expected tables:

```text
alembic_version
users
departments
employees
leave_requests
```

---

# 14. Create Admin User

Run:

```bash
python seed_admin.py
```

Enter:

```text
Admin email: admin@example.com
Admin name: System Admin
Admin password: Admin@123
```

Expected:

```text
Admin created successfully.
```

---

# 15. Start FastAPI

Run:

```bash
uvicorn app.main:app --reload
```

Expected output:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

# 16. Open Swagger Documentation

Open your browser:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides interactive Swagger documentation.

You will see:

```text
Authentication
Departments
Employees
Leaves
Reports
```

---

# 17. Open ReDoc

FastAPI also provides ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 18. API Endpoints

## Authentication

### Register

```http
POST /auth/register
```

Example:

```json
{
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "password": "Ravi@123"
}
```

Public registration creates an Employee account.

---

### Login

```http
POST /auth/login
```

Example:

```json
{
  "email": "admin@example.com",
  "password": "Admin@123"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Current User

```http
GET /auth/me
```

Requires JWT authentication.

---

# 19. Department APIs

## Create Department

```http
POST /departments
```

Admin only.

Example:

```json
{
  "department_name": "IT",
  "location": "Hyderabad",
  "is_active": true
}
```

---

## Get Departments

```http
GET /departments
```

Pagination:

```http
GET /departments?skip=0&limit=10
```

---

## Get Department

```http
GET /departments/{department_id}
```

Example:

```http
GET /departments/1
```

---

## Update Department

```http
PUT /departments/{department_id}
```

Admin only.

---

## Delete Department

```http
DELETE /departments/{department_id}
```

Admin only.

A department containing active employees cannot be deleted.

---

## Department Employees

```http
GET /departments/{department_id}/employees
```

---

# 20. Employee APIs

## Create Employee

```http
POST /employees
```

Admin and HR.

Example:

```json
{
  "employee_code": "EMP001",
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "phone": "9876543210",
  "department_id": 1,
  "designation": "Software Developer",
  "salary": 45000,
  "date_of_joining": "2025-06-10",
  "employment_type": "Full-Time",
  "is_active": true
}
```

---

## Get Employees

```http
GET /employees
```

Pagination:

```http
GET /employees?skip=0&limit=10
```

---

## Search Employees

Search by name:

```http
GET /employees?name=ravi
```

Department:

```http
GET /employees?department_id=1
```

Designation:

```http
GET /employees?designation=Developer
```

Employment type:

```http
GET /employees?employment_type=Full-Time
```

Active status:

```http
GET /employees?is_active=true
```

Combined:

```http
GET /employees?name=ravi&department_id=1&skip=0&limit=10
```

---

## Sort Employees

Sort by name:

```http
GET /employees?sort_by=name&order=asc
```

Sort by salary:

```http
GET /employees?sort_by=salary&order=desc
```

Sort by joining date:

```http
GET /employees?sort_by=date_of_joining&order=asc
```

---

## Get Employee

```http
GET /employees/{employee_id}
```

---

## Update Employee

```http
PUT /employees/{employee_id}
```

Admin and HR.

---

## Delete Employee

```http
DELETE /employees/{employee_id}
```

The employee is **soft deleted**.

The database record is not physically removed.

Instead:

```text
is_active = false
```

---

# 21. Leave APIs

## Apply for Leave

```http
POST /leaves
```

Example:

```json
{
  "employee_id": 1,
  "leave_type": "Casual",
  "start_date": "2026-10-05",
  "end_date": "2026-10-07",
  "reason": "Personal work"
}
```

The API automatically calculates working days.

Saturday and Sunday are excluded.

---

# 22. Leave Types

The system supports:

```text
Sick
Casual
Earned
```

Annual allocation:

| Leave Type | Days |
| ---------- | ---: |
| Sick       |   12 |
| Casual     |   10 |
| Earned     |   15 |

---

# 23. Leave Status

A leave request can have:

```text
Pending
Approved
Rejected
Cancelled
```

Normal flow:

```text
Pending
   |
   ├── Approved
   |
   ├── Rejected
   |
   └── Cancelled
```

Only Pending leaves can be approved, rejected, or cancelled.

---

# 24. Get Leaves

```http
GET /leaves
```

Pagination:

```http
GET /leaves?skip=0&limit=10
```

Employees only see their own leave records.

Admin and HR can manage leave requests according to their permissions.

---

# 25. Filter Leaves

By status:

```http
GET /leaves?status=Pending
```

By leave type:

```http
GET /leaves?leave_type=Sick
```

By employee:

```http
GET /leaves?employee_id=1
```

By date range:

```http
GET /leaves?from_date=2026-10-01&to_date=2026-10-31
```

---

# 26. Get Leave

```http
GET /leaves/{leave_id}
```

Example:

```http
GET /leaves/1
```

---

# 27. Approve Leave

```http
PUT /leaves/{leave_id}/approve
```

Only:

```text
Admin
HR
```

can approve leaves.

---

# 28. Reject Leave

```http
PUT /leaves/{leave_id}/reject
```

Example:

```json
{
  "rejection_reason": "Project deadline during requested period"
}
```

A rejection reason is required.

---

# 29. Cancel Leave

```http
PUT /leaves/{leave_id}/cancel
```

Employees can cancel only their own pending leave.

---

# 30. Employee Leave History

```http
GET /employees/{employee_id}/leaves
```

---

# 31. Employee Leave Balance

```http
GET /employees/{employee_id}/leave-balance
```

Example:

```json
{
  "Sick": {
    "allocated": 12,
    "used": 2,
    "remaining": 10
  },
  "Casual": {
    "allocated": 10,
    "used": 3,
    "remaining": 7
  },
  "Earned": {
    "allocated": 15,
    "used": 0,
    "remaining": 15
  }
}
```

---

# 32. Leave Business Rules

The API validates the following rules:

1. Employees can apply only for themselves.
2. Employees can cancel only their own leave.
3. Admin and HR can approve/reject leaves.
4. HR cannot approve their own leave.
5. Leave cannot start in the past.
6. End date cannot be before start date.
7. Weekends are excluded from total leave days.
8. Leave balance must be sufficient.
9. Leave balance is consumed by approved leave.
10. Overlapping Pending/Approved leave requests are rejected.
11. Inactive employees cannot apply for leave.
12. Only Pending leaves can be approved.
13. Only Pending leaves can be rejected.
14. Only Pending leaves can be cancelled.
15. Rejection requires a rejection reason.

---

# 33. Leave Balance Calculation

Example:

Employee has:

```text
Casual Leave = 10 days
```

Already approved:

```text
3 days
```

Remaining:

```text
10 - 3 = 7 days
```

If the employee requests:

```text
5 days
```

the request can be created.

Remaining after approval:

```text
7 - 5 = 2 days
```

---

# 34. Validation

The API validates:

### Email

Must be a valid email address.

Example:

```text
ravi@example.com
```

---

### Phone

Must contain exactly 10 digits.

Valid:

```text
9876543210
```

Invalid:

```text
98765
```

---

### Salary

Salary must be greater than zero.

Valid:

```json
{
  "salary": 45000
}
```

Invalid:

```json
{
  "salary": 0
}
```

---

### Joining Date

The joining date cannot be in the future.

---

### Employee Code

Must be unique.

---

### Department Name

Must be unique.

---

### Employee Email

Must be unique.

---

# 35. HTTP Status Codes

The API uses appropriate HTTP status codes.

| Code | Meaning                               |
| ---- | ------------------------------------- |
| 200  | Successful request                    |
| 201  | Resource created                      |
| 400  | Business rule/invalid request         |
| 401  | Authentication required/invalid token |
| 403  | Insufficient permissions              |
| 404  | Resource not found                    |
| 409  | Duplicate/conflicting resource        |
| 422  | Validation error                      |

# 36. Complete Beginner Testing Order

Use Swagger in this order:

```text
1. Start MySQL
       ↓
2. Start FastAPI
       ↓
3. Open /docs
       ↓
4. Login as Admin
       ↓
5. Authorize JWT
       ↓
6. Create Department
       ↓
7. Create Employee
       ↓
8. Register/Login Employee
       ↓
9. Apply Leave
       ↓
10. View Leave
       ↓
11. Approve/Reject Leave
       ↓
12. Check Leave Balance
       ↓
13. Test Search
       ↓
14. Test Pagination
       ↓
15. Test Reports
```

---

# 37. Running the Project

Every time you want to run the project:

### Step 1

Open VS Code.

### Step 2

Open the project folder.

### Step 3

Activate virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 4

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

### Step 5

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 38. Stopping the Server

In the terminal press:

```text
CTRL + C
```

The FastAPI server will stop.

---

# 39. Updating Database Models

When a model is changed:

```bash
alembic revision --autogenerate -m "update employee model"
```

Then:

```bash
alembic upgrade head
```

Never use:

```python
Base.metadata.create_all()
```

for this project because database schema changes are managed through Alembic.

---

# 40. Useful Alembic Commands

Check current migration:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Upgrade:

```bash
alembic upgrade head
```

Downgrade one migration:

```bash
alembic downgrade -1
```

---

# 41. Useful FastAPI Commands

Start normally:

```bash
uvicorn app.main:app
```

Start with automatic reload:

```bash
uvicorn app.main:app --reload
```

Use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

---

# 42. Common Beginner Errors

## Error: `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'fastapi'
```

Solution:

```bash
pip install -r requirements.txt
```

Make sure `.venv` is activated.

---

## Error: MySQL Connection Failed

Check:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/employee_leave_db
```

Verify:

* MySQL is running.
* Username is correct.
* Password is correct.
* Database exists.
* Port is correct.

Default MySQL port:

```text
3306
```

---

## Error: `DATABASE_URL is missing`

Make sure `.env` exists in the project root:

```text
employee_leave_management/
├── .env
├── alembic.ini
├── requirements.txt
└── app/
```

---

## Error: 401 Unauthorized

Usually means:

* JWT is missing.
* JWT is expired.
* JWT is invalid.

Login again and authorize Swagger with the new token.

---

## Error: 403 Forbidden

The logged-in user's role does not have permission for that endpoint.

For example:

```text
Employee → Create Department
```

will be rejected.

---

## Error: 409 Conflict

Usually means a unique value already exists.

Examples:

```text
Employee code already exists
Email already exists
Department name already exists
```

---

## Error: 422 Validation Error

Usually means the request body contains invalid data.

Examples:

```text
Invalid email
Invalid phone
Salary <= 0
Missing required field
Invalid enum value
```

---

# 43. Security Notes

Do not commit:

```text
.env
```

Do not store plain-text passwords.

Passwords are stored as bcrypt hashes.

Use a strong JWT secret:

```env
JWT_SECRET_KEY=your-long-random-secret
```

Do not share your:

* MySQL password
* JWT secret
* Production credentials

---

# 44. Example Complete Workflow

### Admin

```text
Login
  ↓
Create IT Department
  ↓
Create Employee
  ↓
View Employees
  ↓
View Dashboard
  ↓
Review Leave
  ↓
Approve/Reject Leave
```

### Employee

```text
Login
  ↓
View Own Profile
  ↓
Apply Leave
  ↓
View Leave
  ↓
Check Leave Balance
  ↓
Cancel Pending Leave if required
```

### HR

```text
Login
  ↓
View Employees
  ↓
Create/Update Employees
  ↓
Review Leave Requests
  ↓
Approve/Reject Leave
  ↓
View Dashboard
  ↓
View Leave Summary
```

---

# 45. Project Status

This project demonstrates:

* REST API development
* FastAPI
* Pydantic validation
* SQLAlchemy ORM
* MySQL
* Alembic migrations
* JWT authentication
* Password hashing
* Role-based authorization
* CRUD operations
* Soft deletion
* Leave management
* Leave balance calculation
* Business-rule validation
* Pagination
* Searching
* Filtering
* Sorting
* HR dashboard
* Leave reports

---

# 46. Author

**Employee & Leave Management System**

Built using:

```text
Python
FastAPI
Pydantic
SQLAlchemy
MySQL
Alembic
JWT
Passlib
bcrypt
Uvicorn
```
