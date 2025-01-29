import frappe
from frappe.utils import (
    now,
    get_last_day,
)
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType


def get_loan_payments(doc):
    clean_custom_loan_repayment(doc)
    emp = doc.employee
    date = get_last_day(doc.posting_date)
    company = doc.company
    loan_salary_component = get_loan_salary_component(company)
    if not loan_salary_component:
        frappe.msgprint(
            "Loan Module Will not be implemented,\
            Since thre is no Laon Salary Component for this company")
        return

    # Get Loan Applications
    loan_apps = frappe.db.get_list(
        "Loan Application KA",
        filters={
            "company": company,
            "emp": emp,
            "start_date": ["<=", date],
            "docstatus": 1,
            "pay_status": PaymentScheduleStatus.UNPAYED.value,
        },
    )
    if len(loan_apps) == 0:
        doc.add_comment("Comment", "Employee has no Unpaid Loan Application")
        return

    loan_apps_list = [la.name for la in loan_apps]
    pss = frappe.get_all(
        "Loan Payment Schedule KA",
        filters={
            "company": company,
            "borrower": emp,
            "payment_due_date": ["<=", date],
            "loan_app": ["in", loan_apps_list],
            "status": PaymentScheduleStatus.UNPAYED.value,
        },
        fields=["*"],
    )
    total_amount = 0
    for ps in pss:
        salary_slip_ps = frappe.get_doc(
            {
                "doctype": "Salary Slip Loan Payment Schedule KA",
                "parent": doc.name,
                "parenttype": "Salary Slip",
                "parentfield": "custom_loan_repayment",
                "loan_app": ps.loan_app,
                "loan_payemnt_schedule": ps.name,
                "salary_slip": doc.name,
                "inst_amount": ps.inst_amount,
                "inst_index": ps.inst_index,
                "balance_after_payment": ps.balance_after_payment
            }
        )
        salary_slip_ps.insert()
        doc.append("custom_loan_repayment", salary_slip_ps)
        total_amount += ps.inst_amount

    if total_amount > 0:
        for sd in doc.earnings + doc.deductions:
            if sd.salary_component == loan_salary_component.salary_component:
                sd.custom_component_base = total_amount
                sd.custom_component_base_rate = 1


def get_loan_salary_component(company):
    return frappe.get_doc("Loan Salary Component KA", company)


def clean_custom_loan_repayment(doc):
    for ps in doc.custom_loan_repayment:
        payment_schedule = frappe.get_doc(
            "Salary Slip Loan Payment Schedule KA", ps.name)
        payment_schedule.delete()
    doc.custom_loan_repayment = []


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
        if loan_payment_schedule.balance_after_payment == 0:
            frappe.db.set_value("Loan Application KA", loan_payment_schedule.parent,
                                "pay_status", PaymentScheduleStatus.UNPAYED.value)


def update_loan_payment_schedules_paid(doc):
    for ps in doc.custom_loan_repayment:
        loan_payment_schedule = frappe.get_doc(
            "Loan Payment Schedule KA", ps.loan_payemnt_schedule)
        loan_payment_schedule.status = PaymentScheduleStatus.PAID.value
        loan_payment_schedule.payment_type = PaymentType.SALARY.value
        loan_payment_schedule.deducted_from = doc.name
        loan_payment_schedule.paid_at = now()
        loan_payment_schedule.save()
        loan_payment_schedule.reload()
        if loan_payment_schedule.balance_after_payment == 0:
            frappe.db.set_value("Loan Application KA", ps.loan_app,
                                "pay_status", PaymentScheduleStatus.PAID.value)
