import frappe
from frappe.utils import (flt)
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType
from salary_slip_component_base.events.salary_slip_events.custom_rent_repayment import (
    get_rent_payments,
    delete_custom_rent_repayment,
    update_rent_payment_schedules_paid,
    update_rent_payment_schedules_unpaid,
)
from salary_slip_component_base.events.salary_slip_events.custom_loan_repayment import (
    get_loan_payments,
    delete_custom_loan_repayment,
    update_loan_payment_schedules_paid,
    update_loan_payment_schedules_unpaid,
)


def on_trash(doc, event):
    if doc.custom_loan_repayment and doc.custom_rent_repayment:
        delete_custom_loan_repayment(doc)
        delete_custom_rent_repayment(doc)


def before_cancel(doc, event):
    if doc.custom_loan_repayment and doc.custom_rent_repayment:
        update_loan_payment_schedules_unpaid(doc)
        delete_custom_loan_repayment(doc)
        update_rent_payment_schedules_unpaid(doc)
        delete_custom_rent_repayment(doc)


def on_submit(doc, event):
    update_loan_payment_schedules_paid(doc)
    update_rent_payment_schedules_paid(doc)


def on_update(doc, event):
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True
    get_loan_payments(doc)
    get_rent_payments(doc)
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
