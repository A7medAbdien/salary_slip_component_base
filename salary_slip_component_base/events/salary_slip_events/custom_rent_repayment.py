import frappe
from frappe.utils import (
    now,
    get_last_day,
)
from salary_slip_component_base.enums import PaymentScheduleStatus, PaymentType


def get_rent_payments(doc):
    clean_custom_rent_repayment(doc)
    emp = doc.employee
    date = get_last_day(doc.posting_date)
    company = doc.company
    rent_salary_component = get_rent_salary_component(company)
    if not rent_salary_component:
        frappe.msgprint(
            "Rent Module Will not be implemented,\
            Since thre is no Laon Salary Component for this company")
        return

    # Get Rent Applications
    rent_apps = frappe.db.get_list(
        "Rent Application KA",
        filters={
            "company": company,
            "emp": emp,
            "start_date": ["<=", date],
            "docstatus": 1,
            "pay_status": PaymentScheduleStatus.UNPAYED.value,
        },
    )
    if len(rent_apps) == 0:
        doc.add_comment("Comment", "Employee has no Unpaid Rent Application")
        return

    rent_apps_list = [la.name for la in rent_apps]
    pss = frappe.get_all(
        "Rent Payment Schedule KA",
        filters={
            "company": company,
            "renter": emp,
            "payment_due_date": ["<=", date],
            "rent_app": ["in", rent_apps_list],
            "status": PaymentScheduleStatus.UNPAYED.value,
        },
        fields=["*"],
    )
    total_amount = 0
    for ps in pss:
        salary_slip_ps = frappe.get_doc(
            {
                "doctype": "Salary Slip Rent Payment Schedule KA",
                "parent": doc.name,
                "parenttype": "Salary Slip",
                "parentfield": "custom_rent_repayment",
                "rent_app": ps.rent_app,
                "rent_payemnt_schedule": ps.name,
                "salary_slip": doc.name,
                "start_date": ps.start_date,
                "end_date": ps.end_date,
                "pay_per_month": ps.pay_per_month,
                "pay_per_day": ps.pay_per_day,
                "amount": ps.amount,
            }
        )
        salary_slip_ps.insert()
        doc.append("custom_rent_repayment", salary_slip_ps)
        total_amount += ps.amount

    if total_amount > 0:
        for sd in doc.earnings + doc.deductions:
            if sd.salary_component == rent_salary_component.salary_component:
                sd.custom_component_base = total_amount
                sd.custom_component_base_rate = 1


def get_rent_salary_component(company):
    return frappe.get_doc("Rent Salary Component KA", company)


def clean_custom_rent_repayment(doc):
    for ps in doc.custom_rent_repayment:
        payment_schedule = frappe.get_doc(
            "Salary Slip Rent Payment Schedule KA", ps.name)
        payment_schedule.delete()
    doc.custom_rent_repayment = []


def delete_custom_rent_repayment(doc):
    for ps in doc.custom_rent_repayment:
        frappe.delete_doc(
            "Salary Slip Rent Payment Schedule KA", ps.name, force=True)
    doc.custom_rent_repayment = []


def update_rent_payment_schedules_unpaid(doc):
    for ps in doc.custom_rent_repayment:
        ps.rent_app = ""
        rent_payment_schedule = frappe.get_doc(
            "Rent Payment Schedule KA", ps.rent_payemnt_schedule)
        rent_payment_schedule.status = PaymentScheduleStatus.UNPAYED.value
        rent_payment_schedule.payment_type = PaymentType.SALARY.value
        rent_payment_schedule.deducted_from = ""
        rent_payment_schedule.paid_at = ""
        rent_payment_schedule.save()
        frappe.db.set_value("Rent Application KA", rent_payment_schedule.parent,
                            "pay_status", PaymentScheduleStatus.UNPAYED.value)


def update_rent_payment_schedules_paid(doc):
    for ps in doc.custom_rent_repayment:
        rent_payment_schedule = frappe.get_doc(
            "Rent Payment Schedule KA", ps.rent_payemnt_schedule)
        rent_payment_schedule.status = PaymentScheduleStatus.PAID.value
        rent_payment_schedule.payment_type = PaymentType.SALARY.value
        rent_payment_schedule.deducted_from = doc.name
        rent_payment_schedule.paid_at = now()
        rent_payment_schedule.save()
        # check all rent payment schedules in rent app if are paid
        rent_app = frappe.get_doc("Rent Application KA", ps.rent_app)
        for rent_app_ps in rent_app.payment_schedules:
            if rent_app_ps.status == PaymentScheduleStatus.UNPAYED.value:
                continue
        frappe.db.set_value("Rent Application KA", ps.rent_app,
                            "pay_status", PaymentScheduleStatus.PAID.value)
