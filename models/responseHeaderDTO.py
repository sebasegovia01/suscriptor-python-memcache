from pydantic import BaseModel, Field


class responseHeaderDTO(BaseModel):
    ConsumerSysCode: str = Field(default=None, example="Según el canal")
