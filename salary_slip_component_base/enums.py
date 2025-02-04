from enum import Enum


class PaymentType(Enum):
    MANUAL = "Manual"
    SALARY = "Salary Deduction"


class PaymentScheduleStatus(Enum):
    PAID = "Paid"
    UNPAYED = "Unpaid"


class ApplicationsStatus(Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    PAID = "Paid"
    UNPAIED = "Unpaid"


class VehicleOwnershipType(Enum):
    RENTED = "Rental"
    LTO = "LTO"


class VehicleStatus(Enum):
    SERVICED = "Serviced"
    NOTIFIED = "Notified"
    UPCOMING = "Upcoming"
    UNCHECKED = "Unchecked"


class AvailabilityStatus(Enum):
    ON_ROAD = "On Road"
    IN_GARAGE = "In Garage"
    AVAILABLE = "Available"
