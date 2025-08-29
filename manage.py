#!/usr/bin/python
import asyncio
import os
import subprocess

import typer
from sqlalchemy.exc import IntegrityError

from models import User


async def create_user(phone: str, email: str, password: str) -> User:
    try:
        user = await User.create(
            phone=phone,
            email=email,
            password=password,
            first_name="",
            last_name="",
        )

    except IntegrityError:
        user = await User.get_by_email(email)

    return user


app = typer.Typer()


@app.command()
def makemigrations(text: str):
    """Create migration with text."""
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", f'"{text}"'],
        capture_output=True,
        text=True,
    )
    print("Log:", result.stdout)
    print("Errors:", result.stderr)


@app.command()
def migrate():
    """Upgrade migration."""
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    print("Log:", result.stdout)
    print("Errors:", result.stderr)


@app.command()
def rollback(migrate_hash: str):
    """Downgrade migration."""
    result = subprocess.run(["alembic", "downgrade", migrate_hash], capture_output=True, text=True)
    print("Log:", result.stdout)
    print("Errors:", result.stderr)


@app.command()
def createsuperuser():
    """Creating super admin."""
    phone: str = os.getenv("ADMIN_PHONE")
    email: str = os.getenv("ADMIN_EMAIL")
    password: str = os.getenv("ADMIN_PASSWORD")
    loop = asyncio.get_event_loop()
    super_admin = loop.run_until_complete(create_user(phone, email, password))

    print(f'Super user "{super_admin.email}" created')


if __name__ == "__main__":
    app()
