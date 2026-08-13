from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class MotTest(Base):
    __tablename__ = "mot_tests"

    __table_args__ = (
        UniqueConstraint(
            "vehicle_id",
            "mot_test_number",
            name="uq_mot_tests_vehicle_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    mot_test_number: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    data_source: Mapped[str | None] = mapped_column(
        String(30),
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
    )

    registration_at_time_of_test: Mapped[str | None] = (
        mapped_column(
            String(16),
        )
    )

    test_result: Mapped[str | None] = mapped_column(
        String(20),
    )

    odometer_value: Mapped[int | None] = mapped_column(
        Integer,
    )

    odometer_unit: Mapped[str | None] = mapped_column(
        String(10),
    )

    odometer_result_type: Mapped[str | None] = (
        mapped_column(
            String(30),
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vehicle: Mapped["Vehicle"] = relationship(
        back_populates="mot_tests",
    )

    defects: Mapped[list["MotDefect"]] = relationship(
        back_populates="mot_test",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MotDefect(Base):
    __tablename__ = "mot_defects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    mot_test_id: Mapped[int] = mapped_column(
        ForeignKey(
            "mot_tests.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    dangerous: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    mot_test: Mapped["MotTest"] = relationship(
        back_populates="defects",
    )