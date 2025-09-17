from pydantic import BaseModel, field_validator


class RangeValue(BaseModel):
    min: float
    max: float

    @field_validator('max')
    @classmethod
    def validate_max_greater_than_min(cls, v, info):
        if 'min' in info.data and v <= info.data['min']:
            raise ValueError('max debe ser mayor que min')
        return v


class Parameter(BaseModel):
    ph: RangeValue
    tds: RangeValue
    temperature: RangeValue
    conductivity: RangeValue
    turbidity: RangeValue
