# Copyright (c) 2025, a and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import (
    month_diff,
    get_last_day,
    today
)
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType
from salary_slip_component_base.utils.date import get_last_dates_between

THRESHOLD_DAYS = 15


class LoanApplicationKA(Document):
    def before_save(self):
        # Borrower
        if self.emp:
            emp = frappe.get_doc("Employee", self.emp)
            self.emp_name = emp.employee_name
            self.phone = emp.cell_number
            self.company = emp.company
            if emp.custom_whatsapp_number:
                self.emp_wp = emp.custom_whatsapp_number
            else:
                self.emp_wp = emp.cell_number
        # End Date
        if self.end_date:
            self.end_date = get_last_day(self.end_date)

        # Total Installments and Pay Per Month
        if self.start_date and self.end_date:
            self.inst_count = month_diff(self.end_date, self.start_date)
            if isinstance(self.start_date, str):
                day = self.start_date[-2:]
            else:
                day = self.start_date.day
            if int(day) > THRESHOLD_DAYS:
                self.inst_count -= 1

            if self.inst_count and self.amount:
                self.pay_per_month = int(self.amount / self.inst_count)
                self.ppm_round_adj = self.amount - \
                    (self.pay_per_month * self.inst_count)

    def on_submit(self):
        dt = "Loan Application KA"
        current_user = frappe.session.user
        frappe.db.set_value(
            dt, self.name, "approved_by", current_user)
        frappe.db.set_value(
            dt, self.name, "approved_at", today())

        frappe.db.set_value(
            dt, self.name, "inst_remaining", self.inst_count)
        inst_paid = self.inst_count - self.inst_remaining
        frappe.db.set_value(
            dt, self.name, "inst_paid", inst_paid)

        frappe.db.set_value(
            dt, self.name, "amount_remaining", self.amount
        )
        amount_paid = self.amount - self.amount_remaining
        frappe.db.set_value(
            dt, self.name, "amount_paid", amount_paid
        )

        self.remove_payment_schedules()
        self.create_payment_schedules()
        self.reload()

        earliest_ps_name = self.get_earliest_unpaied_payment_schedule()
        earliest_ps = frappe.get_doc(
            "Loan Payment Schedule KA", earliest_ps_name)
        frappe.db.set_value(dt, self.name,
                            "pay_status", earliest_ps.status)

    def create_payment_schedules(self):
        borrower = self.emp
        inst_count = self.inst_count
        pay_per_month = self.pay_per_month
        ppm_round_adj = self.ppm_round_adj
        amount_remaining = self.amount
        default_status = PaymentScheduleStatus.UNPAYED.value
        default_payment_type = PaymentType.SALARY.value

        start_date = self.start_date
        end_date = self.end_date
        last_dates = get_last_dates_between(start_date, end_date)
        if isinstance(start_date, str):
            day = start_date[-2:]
        else:
            day = start_date.day
        if int(day) > THRESHOLD_DAYS:  # THRESHOLD_DAYS = 15
            last_dates = last_dates[1:]

        balance = amount_remaining
        for i in range(inst_count):
            ps_index = i + 1
            ps_pay = pay_per_month
            if ps_index == 1:
                ps_pay = pay_per_month + ppm_round_adj
            balance -= ps_pay
            ps = frappe.get_doc(
                {
                    "doctype": "Loan Payment Schedule KA",
                    "parent": self.name,
                    "parenttype": "Loan Application KA",
                    "parentfield": "payment_schedules",
                    "idx": ps_index,
                    "loan_app": self.name,
                    "company": self.company,
                    "borrower": borrower,
                    "inst_index": ps_index,
                    "inst_amount": ps_pay,
                    "balance_after_payment": balance,
                    "balance_before_payment": balance + ps_pay,
                    "status": default_status,
                    "payment_type": default_payment_type,
                    "payment_due_date": last_dates[i],
                }
            )
            ps.insert()

    def remove_payment_schedules(self):
        for ps in self.payment_schedules:
            ps.delete()

    def get_earliest_unpaied_payment_schedule(self):
        pss = frappe.get_all(
            "Loan Payment Schedule KA",
            filters={
                "parent": self.name,
                "status": PaymentScheduleStatus.UNPAYED.value,
            },
            order_by="payment_due_date asc",
            limit=1,
        )
        return pss[0]
