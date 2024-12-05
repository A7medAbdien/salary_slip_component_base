import frappe

def on_update(doc, event):
    print("\n\n\n Salary Slip Updated")
    print(f"\n\n\n SS earnings: {doc.name}")
    salary_details = frappe.db.get_all(
        "Salary Detail",
        filters={"parent": doc.name},
        fields="*"
    )
    for sd in salary_details:
        # get salary component
        salary_component = frappe.get_doc(
            "Salary Component", sd.salary_component)

        # set is calucalted on salary slip
        frappe.db.set_value("Salary Detail", sd.name, "custom_is_calculated_on_salary_slip",
                            salary_component.custom_is_calculated_on_salary_slip)
        if not salary_component.custom_is_calculated_on_salary_slip:
            continue

        # set defoults if there is
        if not sd.custom_component_base_rate:
            sd.custom_component_base_rate = salary_component.custom_component_base_rate
        if not sd.custom_component_base:
            sd.custom_component_base = salary_component.custom_component_base

        amount = sd.custom_component_base_rate * sd.custom_component_base
        print(f"\n\n amount {amount}")
        frappe.db.set_value("Salary Detail", sd.name,
                            "custom_component_base_rate", sd.custom_component_base_rate)
        frappe.db.set_value("Salary Detail", sd.name,
                            "custom_component_base", sd.custom_component_base)
        frappe.db.set_value("Salary Detail", sd.name, "amount", amount)
        doc.reload()
