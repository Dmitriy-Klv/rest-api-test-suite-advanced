from pydantic import BaseModel, EmailStr, Field


class LoginResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: str
    image: str
    token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")

    model_config = {"populate_by_name": True}
