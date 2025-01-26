import frappe
from frappe.utils import (
    get_last_day,
)
from salary_slip_component_base.enums import PaymentScheduleStatus


def clean_custom_loan_repayment(doc):
    for ps in doc.custom_loan_repayment:
        payment_schedule = frappe.get_doc(
            "Salary Slip Loan Payment Schedule KA", ps.name)
        payment_schedule.delete()
    doc.custom_loan_repayment = []


def get_loan_payments(doc):
    clean_custom_loan_repayment(doc)
    emp = doc.employee
    date = get_last_day(doc.posting_date)
    company = doc.company
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
    loan_apps_list = [la["name"] for la in loan_apps]
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
