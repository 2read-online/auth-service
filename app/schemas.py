"""Pydantic schemas for HTTP requests"""
from pydantic import BaseModel, Field, validator, EmailStr


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr = Field(description="EMail address")
    password: str = Field(description="Password", min_length=1)


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(description="Unique email address")
    password: str = Field(description="Password", min_length=6)
    password_confirmation: str = Field(description="Password confirmation", min_length=6)

    @validator('password_confirmation')
    def passwords_match(cls, v, values, **kwargs):  # pylint: disable=no-self-argument,no-self-use,unused-argument
        """
        Check if password_confirmation and password match
        :param v:
        :param values:
        :param _kwargs:
        :return:
        """
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
