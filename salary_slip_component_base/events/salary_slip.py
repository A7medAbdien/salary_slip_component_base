import frappe
from frappe.utils import flt


def on_update(doc, event):
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True

    # print(doc.as_dict())
    for sd in doc.earnings + doc.deductions:
        salary_component = frappe.get_doc(
            "Salary Component", sd.salary_component)
        sd.custom_is_calculated_on_salary_slip = salary_component.custom_is_calculated_on_salary_slip
        # skip if not custom
        if not salary_component.custom_is_calculated_on_salary_slip:
            continue

        if not sd.custom_component_base_rate:
            sd.custom_component_base_rate = salary_component.custom_component_base_rate
        if not sd.custom_component_base:
            sd.custom_component_base = salary_component.custom_component_base

        for ts in doc.timesheets:
            # print(f"\n\n\n ts:{ts.custom_salary_component} sd:{sd.salary_component}\n\n\n")
            if ts.custom_salary_component == sd.salary_component:
                #  print(f"\n\n\n in --------------------------------------------- \n\n\n")
                sd.custom_component_base = ts.custom_salary_component_base

        sd.amount = flt(sd.custom_component_base_rate *
                        sd.custom_component_base, precision=3)

    doc.set_totals()
    doc.save()
    # print(doc.as_dict())
    # print("\n\n\nI ran MF\n\n\n")
