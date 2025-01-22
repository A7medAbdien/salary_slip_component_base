import json
import frappe
from frappe import _
from frappe.utils import (
    get_link_to_form,
)


def custom_submit_salary_slips_for_employees(payroll_entry, salary_slips, publish_progress=True):
    try:
        submitted = []
        unsubmitted = []
        frappe.flags.via_payroll_entry = True
        count = 0

        for entry in salary_slips:
            salary_slip = frappe.get_doc("Salary Slip", entry[0])
            # if salary_slip.net_pay < 0:
            #     unsubmitted.append(entry[0])
            # else:
            try:
                salary_slip.submit()
                submitted.append(salary_slip)
            except frappe.ValidationError:
                unsubmitted.append(entry[0])

            count += 1
            if publish_progress:
                frappe.publish_progress(
                    count * 100 / len(salary_slips), title=_("Submitting Salary Slips...")
                )

        if submitted:
            payroll_entry.make_accrual_jv_entry(submitted)
            payroll_entry.email_salary_slip(submitted)
            payroll_entry.db_set(
                {"salary_slips_submitted": 1, "status": "Submitted", "error_message": ""})

        show_payroll_submission_status(submitted, unsubmitted, payroll_entry)

    except Exception as e:
        frappe.db.rollback()
        log_payroll_failure("submission", payroll_entry, e)

    finally:
        frappe.db.commit()  # nosemgrep
        frappe.publish_realtime(
            "completed_salary_slip_submission", user=frappe.session.user)

    frappe.flags.via_payroll_entry = False


def show_payroll_submission_status(submitted, unsubmitted, payroll_entry):
    if not submitted and not unsubmitted:
        frappe.msgprint(
            _(
                "No salary slip found to submit for the above selected criteria OR salary slip already submitted"
            )
        )
    elif submitted and not unsubmitted:
        frappe.msgprint(
            _("Salary Slips submitted for period from {0} to {1}").format(
                payroll_entry.start_date, payroll_entry.end_date
            ),
            title=_("Success"),
            indicator="green",
        )
    elif unsubmitted:
        frappe.msgprint(
            _("Could not submit some Salary Slips: {}").format(
                ", ".join(get_link_to_form("Salary Slip", entry)
                          for entry in unsubmitted)
            ),
            title=_("Failure"),
            indicator="red",
        )


def log_payroll_failure(process, payroll_entry, error):
    error_log = frappe.log_error(
        title=_("Salary Slip {0} failed for Payroll Entry {1}").format(
            process, payroll_entry.name)
    )
    message_log = frappe.message_log.pop() if frappe.message_log else str(error)

    try:
        if isinstance(message_log, str):
            error_message = json.loads(message_log).get("message")
        else:
            error_message = message_log.get("message")
    except Exception:
        error_message = message_log

    error_message += "\n" + _("Check Error Log {0} for more details.").format(
        get_link_to_form("Error Log", error_log.name)
    )

    payroll_entry.db_set({"error_message": error_message, "status": "Failed"})


def custom_set_payable_amount_against_payroll_payable_account(
    self,
    accounts,
    currencies,
    company_currency,
    accounting_dimensions,
    precision,
    payable_amount,
    payroll_payable_account,
    employee_wise_accounting_enabled,
):
    # Payable amount
    if employee_wise_accounting_enabled:
        """
        employee_based_payroll_payable_entries = {
                        'HREMP00004': {
                                        'earnings': 83332.0,
                                        'deductions': 2000.0
                        },
                        'HREMP00005': {
                                        'earnings': 50000.0,
                                        'deductions': 2000.0
                        }
        }
        """
        for employee, employee_details in self.employee_based_payroll_payable_entries.items():
            payable_amount = employee_details.get(
                "earnings", 0) - employee_details.get("deductions", 0)
            print(f"\n\n\n set_payable_amount_against_payroll_payable_account - employee {
                  employee} - payable_amount {payable_amount}")
            if payable_amount < 0:
                payable_amount = self.get_accounting_entries_and_payable_amount(
                    "Payroll Negative Payable - KEY - KEY",
                    self.cost_center,
                    payable_amount,
                    currencies,
                    company_currency,
                    0,
                    accounting_dimensions,
                    precision,
                    entry_type="payable",
                    party=employee,
                    accounts=accounts,
                )
                print(f" payroll_payable_account {
                      payroll_payable_account}")
            else:
                payable_amount = self.get_accounting_entries_and_payable_amount(
                    payroll_payable_account,
                    self.cost_center,
                    payable_amount,
                    currencies,
                    company_currency,
                    0,
                    accounting_dimensions,
                    precision,
                    entry_type="payable",
                    party=employee,
                    accounts=accounts,
                )
    else:
        payable_amount = self.get_accounting_entries_and_payable_amount(
            payroll_payable_account,
            self.cost_center,
            payable_amount,
            currencies,
            company_currency,
            0,
            accounting_dimensions,
            precision,
            entry_type="payable",
            accounts=accounts,
        )
