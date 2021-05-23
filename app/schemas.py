from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(description="Unique EMail")
    password: str = Field(description="Password")
