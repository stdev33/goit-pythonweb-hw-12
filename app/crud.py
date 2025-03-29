"""
This module contains functions for database operations related to users and contacts.

It includes user creation and email verification logic,
as well as full CRUD operations for managing contact records.
"""

import secrets
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database with a hashed password and verification token.

    Args:
        db (Session): SQLAlchemy database session.
        user (schemas.UserCreate): User creation data including username, email, and password.

    Returns:
        models.User: The newly created user.
    """
    hashed_password = pwd_context.hash(user.password)
    verification_token = secrets.token_urlsafe(32)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        verification_token=verification_token,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_email(db: Session, token: str):
    """
    Verify a user's email based on the provided verification token.

    Args:
        db (Session): SQLAlchemy database session.
        token (str): Verification token to identify the user.

    Returns:
        models.User | None: The verified user or None if verification fails.
    """
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
        return user
    return None


def create_contact(db: Session, contact: schemas.ContactCreate):
    """
    Create a new contact record in the database.

    Args:
        db (Session): SQLAlchemy database session.
        contact (schemas.ContactCreate): Data for the new contact.

    Returns:
        models.Contact: The newly created contact.
    """
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session):
    """
    Retrieve all contact records from the database.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list[models.Contact]: List of all contacts.
    """
    return db.query(models.Contact).all()


def get_contact_by_id(db: Session, contact_id: int):
    """
    Retrieve a single contact by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to retrieve.

    Returns:
        models.Contact | None: The contact if found, otherwise None.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


def update_contact(db: Session, contact_id: int, contact_update: schemas.ContactUpdate):
    """
    Update an existing contact with new data.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to update.
        contact_update (schemas.ContactUpdate): Updated data for the contact.

    Returns:
        models.Contact | None: The updated contact or None if not found.
    """
    db_contact = get_contact_by_id(db, contact_id)
    if db_contact:
        for key, value in contact_update.model_dump(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    """
    Delete a contact by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to delete.

    Returns:
        models.Contact | None: The deleted contact or None if not found.
    """
    db_contact = get_contact_by_id(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, query: str):
    """
    Search for contacts by first name, last name, or email.

    Args:
        db (Session): SQLAlchemy database session.
        query (str): Search string.

    Returns:
        list[models.Contact]: List of matching contacts.
    """
    return (
        db.query(models.Contact)
        .filter(
            (models.Contact.first_name.ilike(f"%{query}%"))
            | (models.Contact.last_name.ilike(f"%{query}%"))
            | (models.Contact.email.ilike(f"%{query}%"))
        )
        .all()
    )


def get_upcoming_birthdays(db: Session):
    """
    Get contacts with birthdays within the next 7 days.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list[models.Contact]: Contacts who have upcoming birthdays.
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    contacts = db.query(models.Contact).all()

    upcoming_birthdays = []
    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)

            if today <= birthday_this_year <= next_week:
                upcoming_birthdays.append(contact)

    return upcoming_birthdays
