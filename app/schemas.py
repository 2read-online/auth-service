from pydantic import BaseModel, Field, validator, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr= Field(description="Unique EMail")
    password: str = Field(description="Password", min_length=1)
