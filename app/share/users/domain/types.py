
from pydantic.functional_validators import PlainValidator
from typing import Annotated
import re


def phone_validator(value: str) -> str:
    if not re.fullmatch(r"^\+\d{2}\d{10}$", value):
        raise ValueError(
            "Teléfono inválido. Debe ser + seguido de 2 dígitos país y 10 dígitos.")
    return value


def password_validator(value: str) -> str:
    if len(value) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
    return value


PhoneStr = Annotated[str, PlainValidator(phone_validator)]
PasswordStr = Annotated[str, PlainValidator(password_validator)]
