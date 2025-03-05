from pydantic import BaseModel, ValidationError, field_validator


class User(BaseModel):
    email: str
    password: str


class UserLogin(User):
    pass


class UserRegister(User):
    username: str
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str):
        import re
        if not re.fullmatch(r"^\+\d{2}\d{10}$", value):
            raise ValueError(
                "El número de teléfono debe comenzar con '+' seguido de 2 dígitos (código de país) y 10 dígitos más.")
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str):

        if len(value) < 6:
            raise ValueError(
                "La contraseña debe tener al menos 6 caracteres.")

        return value


class UserPayload(UserRegister):
    exp: int
    rol: str
