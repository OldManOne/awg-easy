from datetime import datetime
from ipaddress import ip_interface

from pydantic import BaseModel, Field, field_validator


class PeerBase(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    allowed_ips: str = "10.8.0.2/32"
    awg_jc: int = Field(default=3, ge=1, le=10)
    awg_jmin: int = Field(default=50, ge=1, le=5000)
    awg_jmax: int = Field(default=1000, ge=1, le=5000)
    awg_s1: int = Field(default=20, ge=1, le=500)
    awg_s2: int = Field(default=80, ge=1, le=500)

    @field_validator("allowed_ips")
    @classmethod
    def validate_allowed_ips(cls, value: str) -> str:
        ip_interface(value)
        return value


class PeerCreate(PeerBase):
    pass


class PeerUpdate(PeerBase):
    pass


class PeerOut(BaseModel):
    id: int
    name: str
    public_key: str
    allowed_ips: str
    awg_jc: int
    awg_jmin: int
    awg_jmax: int
    awg_s1: int
    awg_s2: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PeerConfigOut(BaseModel):
    peer: PeerOut
    config: str
