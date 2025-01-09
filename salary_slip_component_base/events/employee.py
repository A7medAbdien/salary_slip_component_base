import frappe


def on_update(doc, event):
    """
    Update the salary structure assignment on grade update.

    Steps:
    - Get salary structure based on employee grade.
    - Get current salary structure assignment.
    - Check if salary structure is different.
    - If different, then cancel the previous salary structure assignment.
    - Create a new salary structure assignment with the new salary structure.
    """

    # this is to prevent the infinit loop on update
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True

    # Step 1: Get salary structure based on employee grade
    employee_grade = frappe.get_doc("Employee Grade", doc.grade)
    if not employee_grade:
        frappe.throw(
            "No Employee grade found consider crateing an Employee Grade")
    new_salary_structure = employee_grade.default_salary_structure
    if not new_salary_structure:
        frappe.throw(msg=f"No defaulr salary structure found for grade {doc.grade}")
    print(f"\n\n\n new_salary_structure: {new_salary_structure} \n\n\n")

    # Step 2: Get current salary structure assignment
    current_assignment = frappe.get_doc("Salary Structure Assignment", {
                                        "employee": doc.name, "docstatus": 1})
    print(f"\n\n\n current_assignment: {current_assignment} \n\n\n")

    # Step 3: Check if salary structure is different
    if current_assignment.salary_structure != new_salary_structure:

        # Step 4: Cancel the previous salary structure assignment
        current_assignment.cancel()

        # Step 5: Create a new salary structure assignment with the new salary structure
        new_assignment = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": doc.name,
            "salary_structure": new_salary_structure,
            "from_date": frappe.utils.nowdate(),
            "company": doc.company,
        })
        new_assignment.insert()
        new_assignment.submit()
