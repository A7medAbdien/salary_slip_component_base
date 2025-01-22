import frappe
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


def custom_set_time_sheet(self):
    if self.salary_slip_based_on_timesheet:
        self.set("timesheets", [])

        Timesheet = frappe.qb.DocType("Timesheet")
        timesheets = (
            frappe.qb.from_(Timesheet)
            # Include custom_comp
            .select(
                Timesheet.name,
                Timesheet.total_hours,
                Timesheet.custom_salary_component,
                Timesheet.custom_salary_component_base,
            )
            .where(
                (Timesheet.employee == self.employee)
                & (Timesheet.start_date.between(self.start_date, self.end_date))
                & ((Timesheet.status == "Submitted") | (Timesheet.status == "Billed"))
            )
        ).run(as_dict=1)

        for data in timesheets:
            self.append("timesheets", {
                "time_sheet": data.name,
                "working_hours": data.total_hours,
                # this is the custom part
                "custom_salary_component": data.get("custom_salary_component"),
                "custom_salary_component_base": data.get("custom_salary_component_base"),
            })
            print(f"\n\n\n {data.get('custom_salary_component'),
                  data.get('custom_salary_component_base')}\n\n\n")


# TODO: verifi which one is the one that overite, here or in the hook
# Monkey patching: Replace the original function with the custom one
SalarySlip.set_time_sheet = custom_set_time_sheet
