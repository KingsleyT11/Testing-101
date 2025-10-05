from __future__ import annotations
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from os import getenv
from datetime import datetime
from sqlmodel import select
from sqlalchemy.orm import selectinload
from .db import init_db, get_session
from .models import Customer, Repair
from .schemas import CustomerCreate, RepairCreate
from dotenv import load_dotenv
from .google_oauth import get_google_client
from .contacts import fetch_google_contacts


def create_app() -> FastAPI:
    load_dotenv()
    app = FastAPI(title="Phone Repair Tracker")

    secret_key = getenv("SECRET_KEY", "change-me")
    app.add_middleware(SessionMiddleware, secret_key=secret_key)

    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    # Customers
    @app.get("/customers", response_class=HTMLResponse)
    def list_customers(request: Request, session=Depends(get_session)):
        customers = session.exec(select(Customer).order_by(Customer.created_at.desc())).all()
        return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})

    @app.post("/customers")
    def create_customer(name: str = Form(...), email: str | None = Form(None), phone: str | None = Form(None), session=Depends(get_session)):
        customer = Customer(name=name, email=email, phone=phone)
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return RedirectResponse(url="/customers", status_code=303)

    # Repairs
    @app.get("/repairs", response_class=HTMLResponse)
    def list_repairs(request: Request, session=Depends(get_session)):
        repairs = session.exec(
            select(Repair)
            .options(selectinload(Repair.customer))
            .order_by(Repair.received_date.desc())
        ).all()
        customers = session.exec(select(Customer)).all()
        return templates.TemplateResponse("repairs.html", {"request": request, "repairs": repairs, "customers": customers})

    @app.post("/repairs")
    def create_repair(
        customer_id: int = Form(...),
        device_type: str = Form(...),
        repair_type: str = Form(...),
        price: float = Form(...),
        received_date: str | None = Form(None),
        completed_date: str | None = Form(None),
        notes: str | None = Form(None),
        session=Depends(get_session),
    ):
        parsed_received = None
        parsed_completed = None
        if received_date:
            try:
                parsed_received = datetime.fromisoformat(received_date)
            except ValueError:
                parsed_received = None
        if completed_date:
            try:
                parsed_completed = datetime.fromisoformat(completed_date)
            except ValueError:
                parsed_completed = None

        repair = Repair(
            customer_id=customer_id,
            device_type=device_type,
            repair_type=repair_type,
            price=price,
            received_date=parsed_received or datetime.utcnow(),
            completed_date=parsed_completed,
            notes=notes,
        )
        session.add(repair)
        session.commit()
        return RedirectResponse(url="/repairs", status_code=303)

    # Google Contacts OAuth
    @app.get("/auth/google/login")
    async def google_login(request: Request):
        oauth = get_google_client()
        client = oauth.create_client("google")
        if client is None:
            raise HTTPException(status_code=500, detail="Google OAuth client not configured")
        redirect_uri = getenv("OAUTH_REDIRECT_URI") or str(request.url_for("google_callback"))
        return await client.authorize_redirect(request, redirect_uri)

    @app.get("/auth/google/callback")
    async def google_callback(request: Request):
        oauth = get_google_client()
        client = oauth.create_client("google")
        if client is None:
            raise HTTPException(status_code=500, detail="Google OAuth client not configured")
        token = await client.authorize_access_token(request)
        request.session["google_token"] = token
        return RedirectResponse(url="/contacts/import", status_code=303)

    @app.get("/contacts/import")
    async def import_contacts(request: Request, session=Depends(get_session)):
        token = request.session.get("google_token")
        if not token or not token.get("access_token"):
            return RedirectResponse(url="/auth/google/login", status_code=303)

        contacts = await fetch_google_contacts(token["access_token"])
        for c in contacts:
            name = c.get("name") or "Unnamed"
            email = c.get("email")
            phone = c.get("phone")
            existing = None
            if email:
                existing = session.exec(select(Customer).where(Customer.email == email)).first()
            if not existing and phone:
                existing = session.exec(select(Customer).where(Customer.phone == phone)).first()
            if existing:
                continue
            session.add(Customer(name=name, email=email, phone=phone))
        session.commit()
        return RedirectResponse(url="/customers", status_code=303)

    return app


app = create_app()
