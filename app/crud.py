import secrets
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user: schemas.UserCreate):
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
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
        return user
    return None


def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session):
    return db.query(models.Contact).all()


def get_contact_by_id(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


def update_contact(db: Session, contact_id: int, contact_update: schemas.ContactUpdate):
    db_contact = get_contact_by_id(db, contact_id)
    if db_contact:
        for key, value in contact_update.model_dump(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact_by_id(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, query: str):
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
