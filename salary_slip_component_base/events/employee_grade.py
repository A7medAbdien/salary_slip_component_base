import frappe


def on_update(doc, event):
    """
    Validates Default Salary Structure.

    - Ensures the Salary Structure is not canceled.
    - Ensures it is not already assigned to another Employee Grade.
    """
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True

    salary_structure_link = "<a target='_blank' href='{0}'>{1}</a>".format(
        frappe.utils.get_link_to_form(
            "Salary Structure", doc.default_salary_structure),
        doc.default_salary_structure
    )
    # Step 1: Check if the Default Salary Structure is canceled
    if doc.default_salary_structure:
        is_canceled = frappe.db.get_value(
            "Salary Structure",
            doc.default_salary_structure,
            "docstatus"
        )
        if is_canceled == 2:
            frappe.throw(msg="The Default Salary Structure {0} is \
            canceled and cannot be assigned.".format(salary_structure_link))

        # Step 2: Check if it is assigned to another Employee Grade
        assigned_employee_grade = frappe.db.get_value(
            "Salary Structure",
            doc.default_salary_structure,
            "custom_employee_grade"
        )
        # if not assigned_employee_grade:
        #    frappe.throw(f"The Default Salary Structure {
        #                salary_structure_link} is not assigned to any Employee Grade.")
        employee_grade_link = "<a target='_blank' href='{0}'>{1}</a>".format(
            frappe.utils.get_link_to_form(
                "Employee Grade", assigned_employee_grade),
            assigned_employee_grade
        )
        if assigned_employee_grade and assigned_employee_grade != doc.name:
            frappe.throw(
                f"The Default Salary Structure {
                    salary_structure_link} is already assigned to Employee Grade {employee_grade_link}."
            )
