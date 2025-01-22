import frappe
from frappe import _


def custom_on_submit(self):
    if self.net_pay < 0:
        frappe.msgprint(_("Net Pay cannot be less than 0"))
    self.set_status()
    self.update_status(self.name)


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
