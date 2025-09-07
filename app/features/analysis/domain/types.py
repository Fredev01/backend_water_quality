from pydantic.functional_validators import PlainValidator, BeforeValidator
from typing import Annotated


def ahead_prediction(value: int) -> int:
    if value < 10 or value > 20:
        raise ValueError(
            "La cantida a predecir debe ser mayor a 10 y menor o igual a 20"
        )
    return value


AheadPrediction = Annotated[int, PlainValidator(ahead_prediction)]
