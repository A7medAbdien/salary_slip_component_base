import frappe


def on_update(doc, event):
    if getattr(doc, "_on_update_handled", False):
        return
    doc._on_update_handled = True
    validate_default_salary_structure(doc, event)
    update_employee_salary_structure_assignemnt(doc, event)


def validate_default_salary_structure(doc, event):
    """
    Validates Default Salary Structure.

    - Ensures the Salary Structure is not canceled.
    - Ensures it is not already assigned to another Employee Grade.
    """
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

        # # Step 2: Check if it is assigned to another Employee Grade
        # assigned_employee_grade = frappe.db.get_value(
        #     "Salary Structure",
        #     doc.default_salary_structure,
        #     "custom_employee_grade"
        # )
        # # if not assigned_employee_grade:
        # #    frappe.throw(f"The Default Salary Structure {
        # #                salary_structure_link} is not assigned to any Employee Grade.")
        # employee_grade_link = "<a target='_blank' href='{0}'>{1}</a>".format(
        #     frappe.utils.get_link_to_form(
        #         "Employee Grade", assigned_employee_grade),
        #     assigned_employee_grade
        # )
        # if assigned_employee_grade and assigned_employee_grade != doc.name:
        #     frappe.throw(
        #         f"The Default Salary Structure {
        #             salary_structure_link} is already assigned to Employee Grade {employee_grade_link}."
        #     )


def update_employee_salary_structure_assignemnt(doc, event):
    """
    Updates Employee "Salary Structure Assignment" on changing
    the "Default Salary Structure" to the new "Default Salary Structure".
    - Step 1: get the previous version of the doc, to get the previous Structure
    Case A: for some reason got assigned to a different Structure
        - Step 3: get all employee with this grade
        - Step 4: create a new Assignment with the new Structure
    Case B: different
        - Step 5: Get all Assignment with the previous Structure
        - Step 6: if the Assignment not equal to the current Structure,
        cancel and create a new Assignment with the new Structure
    """
    # Step 1: get the previous version of the doc
    previous_doc = doc.get_doc_before_save()
    # Step 2: Check if the previous Structure different from the current
    if previous_doc.default_salary_structure != doc.default_salary_structure:
        # Step 3: Get all Assignment with the previous Structure
        ssas = frappe.db.get_list(
            "Salary Structure Assignment",
            filters={
                "salary_structure": previous_doc.default_salary_structure,
                "grade": doc.name
            })
        print(f"\n\n\n ssas: {ssas} \n\n\n")

        if len(ssas) == 0:
            #Step 3: get all employee with this grade
            emps = frappe.db.get_list(
                "Employee",
                filters={"grade": doc.name}
            )
            for emp in emps:
                # Step 4: create a new Assignment with the new Structure
                ssa = frappe.get_doc({
                    "doctype": "Salary Structure Assignment",
                    "employee": emp.name,
                    "salary_structure": doc.default_salary_structure,
                    "from_date": frappe.utils.nowdate(),
                    "company": emp.company,
                })
                ssa.insert()
                ssa.submit()

        for ssa in ssas:
            ssa = frappe.get_doc("Salary Structure Assignment", ssa.name)
            if ssa.salary_structure == doc.default_salary_structure:
                continue
            ssa.cancel()
            print(f"\n\n\n ssa: {ssa.as_dict()} \n\n\n")
            # Step 4: Create a new Assignment with the new Structure
            new_assignment = frappe.get_doc({
                "doctype": "Salary Structure Assignment",
                "employee": ssa.employee,
                "salary_structure": doc.default_salary_structure,
                "from_date": frappe.utils.nowdate(),
                "company": ssa.company,
            })
            new_assignment.insert()
            new_assignment.submit()
