from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle import Vehicle


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    service_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    mileage: Mapped[int | None] = mapped_column(
        Integer,
    )

    garage: Mapped[str | None] = mapped_column(
        String(160),
    )

    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=10,
            scale=2,
        ),
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
    )

    receipts: Mapped[list["ServiceReceipt"]] = relationship(
        back_populates="service_record",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ServiceReceipt(Base):
    __tablename__ = "service_receipts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    service_record_id: Mapped[int] = mapped_column(
        ForeignKey(
            "service_records.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_path: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    service_record: Mapped["ServiceRecord"] = relationship(
        back_populates="receipts",
    )