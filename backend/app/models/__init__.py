from app.models.maintenance import MaintenanceItem
from app.models.mot import MotDefect, MotTest
from app.models.reminder import (
    ReminderDismissal,
    ReminderSettings,
)
from app.models.service import (
    ServiceReceipt,
    ServiceRecord,
)
from app.models.user import User
from app.models.user_vehicle import UserVehicle
from app.models.vehicle import Vehicle
from app.models.vehicle_check_history import (
    VehicleCheckHistory,
)


__all__ = [
    "Vehicle",
    "MotTest",
    "MotDefect",
    "User",
    "UserVehicle",
    "ServiceRecord",
    "ServiceReceipt",
    "MaintenanceItem",
    "VehicleCheckHistory",
    "ReminderSettings",
    "ReminderDismissal",
]