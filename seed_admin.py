from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models.models import User
from app.auth.security import hash_password


db = SessionLocal()

try:
    email = input("Admin email: ").strip()
    name = input("Admin name: ").strip()
    password = getpass("Admin password: ")

    existing = db.scalar(
        select(User).where(User.email == email)
    )

    if existing:
        print("User already exists.")
    else:

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="Admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

finally:
    db.close()