from enum import Enum


class PaymentType(Enum):
    MANUAL = "Manual"
    SALARY = "Salary Deduction"


class PaymentScheduleStatus(Enum):
    PAID = "Paid"
    UNPAYED = "Unpaid"
