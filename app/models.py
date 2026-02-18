import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Peer(Base):
    __tablename__ = "peers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    private_key: Mapped[str] = mapped_column(String(64))
    public_key: Mapped[str] = mapped_column(String(64))
    preshared_key: Mapped[str] = mapped_column(String(64))
    allowed_ips: Mapped[str] = mapped_column(String(128), default="10.8.0.2/32")
    awg_jc: Mapped[int] = mapped_column(Integer, default=3)
    awg_jmin: Mapped[int] = mapped_column(Integer, default=50)
    awg_jmax: Mapped[int] = mapped_column(Integer, default=1000)
    awg_s1: Mapped[int] = mapped_column(Integer, default=20)
    awg_s2: Mapped[int] = mapped_column(Integer, default=80)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
