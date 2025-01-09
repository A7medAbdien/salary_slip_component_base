import frappe


def on_submit(doc, event):
    on_submit_custom_employee_grade(doc, event)


def on_cancel(doc, event):
    on_cancel_custom_employee_grade(doc, event)


def on_submit_custom_employee_grade(doc, event):
    """
    Validates that the selected Employee Grade does not have a default salary
    structure.

    Steps:
    1. Retrieve the Employee Grade from `doc.custom_employee_grade`.
    2. Check if the Employee Grade has a default salary structure.
    3. If the default salary structure is present, raise an error;
    4. else: set Salary Structure to Employee Grade as default
    """
    # Step 1: Retrieve the Employee Grade
    if not doc.custom_employee_grade:
        frappe.throw("Please select an Employee Grade.")
    employee_grade = frappe.get_doc(
        "Employee Grade", doc.custom_employee_grade)

    # prepare links
    employee_grade_link = frappe.utils.get_url_to_form(
        "Employee Grade", employee_grade.name)
    salary_structure_link = frappe.utils.get_url_to_form(
        "Salary Structure", doc.name)

    # Step 2: Check if the Employee Grade has a default salary structure
    if employee_grade.default_salary_structure:
        # Step 3: Raise an error with a link to the Employee Grade
        frappe.throw(
            msg=f"Employee Grade {employee_grade_link} has a default salary \
            structure {salary_structure_link} and cannot be selected.",
            title="Invalid Employee Grade",
        )
    else:
        # 4: Set the Salary Structure as the default for the Employee Grade
        employee_grade.default_salary_structure = doc.name
        employee_grade.save()
        frappe.msgprint(
            msg=f"The default salary structure of {employee_grade_link} \
            has been changed to Employee Grade: {doc.name}",
            title="Action Completed",
        )


def on_cancel_custom_employee_grade(doc, event):
    """
    Removes a canceled Salary Structure from its associated Employee Grade.

    Steps:
    1. Find the Employee Grade connected to Salary Structure
    2. Remove the default Salary Structure reference
    """
    # 1. Find the Employee Grade connected to Salary Structure
    employee_grade = frappe.db.get_value(
        "Employee Grade",
        {"default_salary_structure": doc.name},
        "name"
    )

    # 2. Remove the default Salary Structure reference
    if employee_grade:
        frappe.db.set_value("Employee Grade", employee_grade,
                            "default_salary_structure", None)
        frappe.msgprint(
            msg=f"The default salary structure of \
            {frappe.utils.get_url_to_form('Employee Grade', employee_grade)} now empty",
            title="Action Completed",
        )
