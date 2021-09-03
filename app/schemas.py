"""Pydantic schemas for HTTP requests"""
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr = Field(description="EMail address")


class VerifyRequest(BaseModel):
    """Verification Request"""
    verification_hash: str
