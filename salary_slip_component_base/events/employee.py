import frappe


def on_update(doc, event):
    """
    Update the salary structure assignment when an employee's grade is updated.

    Steps:
    1. Get the salary structure based on the employee grade.
    2. Check if there is a current salary structure assignment:
       Case A: If there is a current assignment:
           A.1. Retrieve the current salary structure assignment.
           A.2. If different, cancel the previous salary structure assignment.
    3. Create a new salary structure assignment with the updated salary structure.
    """
    # Prevent infinite loop on update
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True
    if doc.grade and doc.get_doc_before_save().grade != doc.grade:
        # Step 1: Get salary structure based on employee grade
        employee_grade = frappe.get_doc("Employee Grade", doc.grade)
        if not employee_grade:
            frappe.throw(
                "No Employee Grade found. Please create an Employee Grade.")
        new_salary_structure = employee_grade.default_salary_structure
        if not new_salary_structure:
            frappe.msgprint(
                title="Warning",
                msg="No default salary structure found for grade {0}. Please set a default salary structure.".format(
                    doc.grade)
            )
        print(f"New salary structure: {new_salary_structure}")
        # Step 2: Get current salary structure assignment
        current_assignments = frappe.db.get_list(
            "Salary Structure Assignment",
            filters={"employee": doc.name, "docstatus": 1}
        )
        print(f"Current assignment: {current_assignments}")
        if len(current_assignments) > 0:
            current_assignment = current_assignments[0]
            current_assignment = frappe.get_doc(
                "Salary Structure Assignment", current_assignment)
            # Step 3: Check if salary structure is different
            if current_assignment and current_assignment.salary_structure != new_salary_structure:
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
