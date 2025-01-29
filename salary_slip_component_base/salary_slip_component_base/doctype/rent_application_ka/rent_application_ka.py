# Copyright (c) 2025, a and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
    date_diff,
    get_last_day,
    today,
    getdate,
    add_to_date,
)
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType
from salary_slip_component_base.utils.date import get_first_date

THRESHOLD_DAYS = 15


class RentApplicationKA(Document):
    def on_cancel(self):
        self.remove_payment_schedules()

    def before_save(self):
        # Borrower
        if self.emp:
            emp = frappe.get_doc("Employee", self.emp)
            self.emp_name = emp.employee_name
            self.emp_phone = emp.cell_number
            self.company = emp.company
            self.emp_wp = emp.custom_whatsapp_number

    def on_submit(self):
        dt = "Loan Application KA"
        current_user = frappe.session.user
        frappe.db.set_value(
            dt, self.name, "approved_by", current_user)
        frappe.db.set_value(
            dt, self.name, "approved_at", today())

        self.create_payment_schedule()
        self.reload()

    def create_payment_schedule(self):
        renter = self.emp
        pay_per_month = self.pay_per_month
        default_status = PaymentScheduleStatus.UNPAYED.value
        default_payment_type = PaymentType.SALARY.value
        # Calculate start and end dates
        start_date = getdate(self.start_date)
        if len(self.payment_schedules) > 0:
            prev_ps = self.payment_schedules[0]
            prev_end_date = get_last_day(getdate(prev_ps.end_date))
            start_date = add_to_date(prev_end_date, days=1)
        end_date = get_last_day(start_date)
        payment_due_date = get_last_day(start_date)
        # Calculate pay per day
        _first_day_in_month = get_first_date(start_date)
        month_days = date_diff(end_date, _first_day_in_month) + 1
        pay_per_day = pay_per_month / month_days
        # Calculate amount
        rented_days = date_diff(end_date, start_date) + 1
        amount = pay_per_day * rented_days
        # Create Payment Schedule
        ps = frappe.get_doc(
            {
                "doctype": "Rent Payment Schedule KA",
                "parent": self.name,
                "parenttype": "Rent Application KA",
                "parentfield": "payment_schedules",
                "rent_app": self.name,
                "company": self.company,
                "status": default_status,
                "payment_type": default_payment_type,
                "renter": renter,
                "start_date": start_date,
                "end_date": end_date,
                "pay_per_month": pay_per_month,
                "rented_days": rented_days,
                "month_days": month_days,
                "pay_per_day": pay_per_day,
                "amount": amount,
                "payment_due_date": payment_due_date,
            }
        )
        ps.insert()

    def remove_payment_schedules(self):
        for ps in self.payment_schedules:
            ps.delete()
