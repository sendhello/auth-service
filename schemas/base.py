from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Model(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {UUID: str}
