import frappe
from frappe.utils import (flt, now)
from salary_slip_component_base.enums import BalanceAdjustmentType
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
    delete_custom_loan_repayment(doc)
    delete_custom_rent_repayment(doc)


def before_cancel(doc, event):
    reverse_update_emp_balance(doc)
    update_loan_payment_schedules_unpaid(doc)
    update_rent_payment_schedules_unpaid(doc)
    delete_custom_loan_repayment(doc)
    delete_custom_rent_repayment(doc)


def on_submit(doc, event):
    if doc.custom_loan_repayment:
        update_loan_payment_schedules_paid(doc)
    if doc.custom_rent_repayment:
        frappe.msgprint("custom rent repayment")
        update_rent_payment_schedules_paid(doc)


def on_update(doc, event):
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True
    get_loan_payments(doc)
    get_rent_payments(doc)
    calculate_component_amount_based_on_custom_base(doc)
    update_emp_balance(doc)
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


def reverse_update_emp_balance(doc):
    emp = frappe.get_doc("Employee", doc.employee)
    if not emp.custom_balance:
        balance = 0
    else:
        balance = emp.custom_balance
    if (doc.net_pay < 0):
        balance -= doc.net_pay
    elif (doc.net_pay > 0) and (balance < 0):
        balance -= doc.net_pay
    emp.custom_balance = balance
    emp.save()


def update_emp_balance(doc):
    emp = frappe.get_doc("Employee", doc.employee)
    # read balance
    if not emp.custom_balance:
        balance = 0
    else:
        balance = emp.custom_balance
    # only update if balance is negative or net_pay is negative
    if (emp.custom_balance >= 0 and doc.net_pay > 0) or doc.net_pay == 0:
        return
    # edit balance
    new_balance = balance + doc.net_pay
    emp.custom_balance = new_balance
    emp.save()
    # create a record
    balance_adj = frappe.get_doc({
        "doctype": "Balance Adjustments KA",
        "parent": emp.name,
        "parenttype": "Employee",
        "parentfield": "custom_balance_adjustments",
        "adj_type": BalanceAdjustmentType.SALARY.value,
        "recorded_from": doc.name,
        "recorded_at": now(),
        "balance_before": balance,
        "balance_adj": doc.net_pay,
        "balance_after": new_balance,
    })
    balance_adj.insert()
    frappe.msgprint("Balance Adjustments Created")
