import frappe
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType
from salary_slip_component_base.events.salary_slip_events.salary_slip import get_loan_payments
from frappe.utils import (flt, now)


def on_trash(doc, event):
    delete_custom_loan_repayment(doc)


def before_cancel(doc, event):
    update_loan_payment_schedules_unpaid(doc)
    delete_custom_loan_repayment(doc)


def delete_custom_loan_repayment(doc):
    for ps in doc.custom_loan_repayment:
        frappe.delete_doc(
            "Salary Slip Loan Payment Schedule KA", ps.name, force=True)
    doc.custom_loan_repayment = []


def update_loan_payment_schedules_unpaid(doc):
    for ps in doc.custom_loan_repayment:
        ps.loan_app = ""
        loan_payment_schedule = frappe.get_doc(
            "Loan Payment Schedule KA", ps.loan_payemnt_schedule)
        loan_payment_schedule.status = PaymentScheduleStatus.UNPAYED.value
        loan_payment_schedule.payment_type = PaymentType.SALARY.value
        loan_payment_schedule.deducted_from = ""
        loan_payment_schedule.paid_at = ""
        loan_payment_schedule.save()
        loan_payment_schedule.reload()


def on_submit(doc, event):
    update_loan_payment_schedules_paid(doc)


def update_loan_payment_schedules_paid(doc):
    for ps in doc.custom_loan_repayment:
        loan_payment_schedule = frappe.get_doc(
            "Loan Payment Schedule KA", ps.loan_payemnt_schedule)
        loan_payment_schedule.status = PaymentScheduleStatus.PAID.value
        loan_payment_schedule.payment_type = PaymentType.SALARY.value
        loan_payment_schedule.deducted_from = doc.name
        loan_payment_schedule.paid_at = now()
        loan_payment_schedule.save()


def on_update(doc, event):
    # TODO: change to before save
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True
    get_loan_payments(doc)
    calculate_component_amount_based_on_custom_base(doc)
    doc.save()


def calculate_component_amount_based_on_custom_base(doc):
    for sd in doc.earnings + doc.deductions:
        salary_component = frappe.get_doc(
            "Salary Component", sd.salary_component)
        # skip if not custom
        if not salary_component.custom_is_calculated_on_salary_slip:
            continue

        if not sd.custom_component_base_rate:
            sd.custom_component_base_rate = salary_component.custom_component_base_rate
        if not sd.custom_component_base:
            sd.custom_component_base = salary_component.custom_component_base

        # Timesheet Component
        for ts in doc.timesheets:
            # print(f"\n\n\n ts:{ts.custom_salary_component} sd:{sd.salary_component}\n\n\n")
            if ts.custom_salary_component == sd.salary_component:
                #  print(f"\n\n\n in --------------------------------------------- \n\n\n")
                sd.custom_component_base = ts.custom_salary_component_base

        sd.amount = flt(sd.custom_component_base_rate *
                        sd.custom_component_base, precision=3)

    doc.set_totals()
    # print(doc.as_dict())
    # print("\n\n\nI ran MF\n\n\n")
