"""Auth request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1, max_length=128)


class AuthUser(BaseModel):
    username: str
    display_name: str
    role: str
    unit: str = "SCRB"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUser


class MeResponse(BaseModel):
    user: AuthUser
    authenticated: bool = True
