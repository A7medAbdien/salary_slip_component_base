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
