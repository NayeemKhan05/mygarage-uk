from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class VehicleCheckHistory(Base):
    __tablename__ = "vehicle_check_history"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "registration",
            name=(
                "uq_vehicle_check_history_"
                "user_registration"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    registration: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        index=True,
    )

    make: Mapped[str | None] = mapped_column(
        String(100),
    )

    model: Mapped[str | None] = mapped_column(
        String(100),
    )

    fuel_type: Mapped[str | None] = mapped_column(
        String(50),
    )

    colour: Mapped[str | None] = mapped_column(
        String(50),
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
    )

    first_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    check_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )