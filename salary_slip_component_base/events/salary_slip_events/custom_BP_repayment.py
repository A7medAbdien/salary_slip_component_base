import frappe


def get_pb_salary_component(company):
    return frappe.get_doc("PB Salary Component KA", company)


def get_pb(doc):
    emp = frappe.get_doc("Employee", doc.employee)
    if emp.custom_balance is None:
        emp.custom_balance = 0
    if emp.custom_balance > 0:
        frappe.msgprint(
            "Previous Balance is positive for rider {0}".format(emp.name))
    return emp.custom_balance


def set_pb_on_salary_slip(doc):
    pb_salary_component = get_pb_salary_component(doc.company)
    previous_balance = get_pb(doc)
    for sd in doc.earnings + doc.deductions:
        if sd.salary_component == pb_salary_component.salary_component:
            sd.custom_component_base = previous_balance
            sd.custom_component_base_rate = 1
