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
from salary_slip_component_base.enums import ApplicationsStatus, PaymentScheduleStatus, PaymentType
from salary_slip_component_base.utils.date import get_first_date
from salary_slip_component_base.utils.validation import is_empty

THRESHOLD_DAYS = 15


class RentApplicationKA(Document):
    def on_cancel(self):
        self.remove_payment_schedules()
        self.remove_from_rider_rent_applicaiton_history()

    def before_insert(self):
        if len(self.payment_schedules) > 0:
            self.payment_schedules = []

    def before_save(self):
        if self.emp:
            emp = frappe.get_doc("Employee", self.emp)
            self.emp_name = emp.employee_name
            self.emp_phone = emp.cell_number
            self.company = emp.company
            self.emp_wp = emp.custom_whatsapp_number
        self.pay_status = PaymentScheduleStatus.UNPAYED.value

    def on_submit(self):
        dt = "Loan Application KA"
        current_user = frappe.session.user
        frappe.db.set_value(
            dt, self.name, "approved_by", current_user)
        frappe.db.set_value(
            dt, self.name, "approved_at", today())
        self.create_payment_schedule()
        self.add_to_rider_rent_applicaiton_history()
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

    def prepare_for_close(self):
        """
        Prepare Rent Application for close,
        Which will prevent from creating new payment schedules,
        This will run on setting the vehicle to inactive (In Garage)
        """
        if not self.is_active:
            frappe.throw("You cannot close an inactive Rent Application")
        if not is_empty(self.end_date):
            frappe.throw("Can not close a Rent Application with end date")
        if self.status == PaymentScheduleStatus.PAID.value or \
                self.status == PaymentScheduleStatus.UNPAYED.value:
            frappe.throw(
                "You cannot close an already Paied or Unpaid Rent Application"
            )

        frappe.db.set_value("Rent Application KA",
                            self.name, "is_active", False)
        frappe.db.set_value("Rent Application KA",
                            self.name, "end_date", today())
        frappe.db.set_value("Rent Application KA", self.name,
                            "pay_status", PaymentScheduleStatus.UNPAYED.value)
        frappe.db.set_value("Rent Application KA", self.name,
                            "workflow_state", ApplicationsStatus.UNPAIED.value)

        # NOTE: this should never happens,
        """
        since KA Companies always pays January Payroll after the month ends,
        which means that the schedule that creates a new payment schedule
        already ran and created a new payment schedule for February
        """
        if self.is_all_payment_schedules_paied():
            frappe.msgprint(title="Warning", msg="Please review KA Admin,\
            All Payment Schedules are already paid, and this should not happens")
            frappe.db.set_value("Rent Application KA", self.name,
                                "pay_status", PaymentScheduleStatus.PAID.value)
            frappe.db.set_value("Rent Application KA", self.name,
                                "workflow_state", ApplicationsStatus.PAID.value)

    def close(self):
        if is_empty(self.end_date):
            frappe.throw("End date is required")
        if self.is_active:
            frappe.throw("You cannot close an active Rent Application")

        if self.is_all_payment_schedules_paied():
            frappe.db.set_value("Rent Application KA", self.name,
                                "pay_status", PaymentScheduleStatus.PAID.value)
            frappe.db.set_value("Rent Application KA", self.name,
                                "workflow_state", ApplicationsStatus.PAID.value)
        else:
            frappe.throw(
                "You cannot close this Rent Application \
                until all Payment Schedules are paid")

    def is_all_payment_schedules_paied(self):
        can_close = True
        for ps in self.payment_schedules:
            if ps.status == PaymentScheduleStatus.UNPAYED.value:
                can_close = False
                break
        return can_close

    def create_new_rent_application_with_different_vehicle(self, vehicle, rent_agr):
        new_rent_app = frappe.get_doc("Rent Application KA")
        new_rent_app.emp = self.emp
        new_rent_app.vehicle = vehicle
        new_rent_app.rent_agreement = rent_agr
        new_rent_app.start_date = today()
        new_rent_app.workflow_state = ApplicationsStatus.PENDING.value
        new_rent_app.insert()

    def add_to_rider_rent_applicaiton_history(self):
        rider_ra_history = frappe.get_doc({
            "doctype": "Rider Rent Application History KA",
            "parent": self.emp,
            "parenttype": "Employee",
            "parentfield": "custom_rent_history",
            "rent_app": self.name,
            "rider": self.emp,
            "vehicle": self.vehicle,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "pay_per_month": self.pay_per_month,
        })
        rider_ra_history.insert()

    def remove_from_rider_rent_applicaiton_history(self):
        rider = frappe.get_doc("Employee", self.emp)
        for ra_history in rider.custom_rent_history:
            if ra_history.rent_app == self.name:
                ra_history.delete()
