from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from .database import get_db
from .models import User
from .auth import authenticate_user, create_access_token
from .security import get_current_user_or_redirect

import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.get("/auth/login-form", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request})


@router.post("/auth/login-html")
def login_html(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response = RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request, current_user: User = Depends(get_current_user_or_redirect)
):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": current_user}
    )


@router.get("/logout")
def logout(
    request: Request, current_user: User = Depends(get_current_user_or_redirect)
):
    response = RedirectResponse("/auth/login-form", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
