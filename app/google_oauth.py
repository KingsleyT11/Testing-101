from __future__ import annotations
from typing import Any, Dict, Optional
from authlib.integrations.starlette_client import OAuth
from os import getenv
from starlette.requests import Request


oauth = OAuth()

oauth.register(
    name="google",
    client_id=getenv("GOOGLE_CLIENT_ID"),
    client_secret=getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile https://www.googleapis.com/auth/contacts.readonly"},
)


def get_google_client() -> OAuth:
    return oauth
