from pydantic import BaseModel, ConfigDict


class CityResponse(BaseModel):
    city_id: int
    name: str
    state: str
    is_prototype: bool

    model_config = ConfigDict(from_attributes=True)
