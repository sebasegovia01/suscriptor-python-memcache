from pydantic import BaseModel, Field


class headerRequestDto(BaseModel):
    ConsumerSysCode: str = Field(default=None, example="Según el canal")
