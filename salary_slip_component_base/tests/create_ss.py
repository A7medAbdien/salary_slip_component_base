import frappe
from frappe.utils import (
    getdate
)
from time import sleep
import unittest


class TestCreateSS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        frappe.db.savepoint("salary_slip_component_base")

    def setUp(self):
        print("setUpClass")
        self.emp = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "RID-1",
            "gender": "Male",
            "date_of_joining": getdate("01-01-2024"),
            "date_of_birth": getdate("01-01-1990"),
            "status": "Active",
            "custom_balance": -100,
            "department": "Riders - TD",
            "company": "Test (Demo)",
        }).insert()

        self.vehicle = frappe.get_doc({
            "doctype": "Vehicle KA",
            "license_plate": 0,
            "model": "Honda City",
            "year": 2000,
            "pay_per_month": "200",
            "company": "Test (Demo)",
            "current_km": 2000,
        }).insert()

        self.rent = frappe.get_doc({
            "doctype": "Rent Application KA",
            "emp": self.emp,
            "vehicle": self.vehicle,
            "start_date": getdate("01-01-2025"),
        }).insert()

        self.emp_grade = frappe.get_doc({
            "doctype": "Employee Grade",
            "__newname": "Test",
            "company": "Test (Demo)",
        }).insert()

        self.sstruc = frappe.get_doc(SStruct).insert()

    def test_cast_rent(self):
        test_submit_rent(self)
        test_sstruc_assignment(self)
        test_ss(self)
        test_cancel_ss(self)
        test_cancel_assign(self)
        test_cancel_rent(self)

    def tearDown(self):
        print("------------Delete Rent------------")
        frappe.delete_doc("Salary Structure", self.sstruc.name)
        frappe.delete_doc("Rent Application KA", self.rent.name)
        frappe.delete_doc("Vehicle KA", self.vehicle.name)
        frappe.delete_doc("Employee", self.emp.name)

    @classmethod
    def tearDownClass(cls):
        frappe.db.rollback()


def test_ss(test):
    print("------------Create Salary Slip------------")
    ss = frappe.get_doc({
        "doctype": "Salary Slip",
        "employee": test.emp.name,
        "posting_date": getdate("20-02-2025"),
    })
    ss.insert()
    ss = frappe.get_doc("Salary Slip", ss.name)
    test.ss = ss
    for d in ss.deductions + ss.earnings:
        ssd = frappe.get_doc("Salary Detail", d.name)
        if ssd.salary_component == "Rent Deduction":
            test.assertEqual(ssd.amount, 200, "Rent Deduction is not 200")
        if ssd.salary_component == "Previous Balance":
            test.assertEqual(ssd.amount, -100, "Previous Balance is not 100")
            print("Previous Balance {}".format(ssd.amount))

    ss.submit()
    ss = frappe.get_doc("Salary Slip", ss.name)
    test.assertEqual(ss.docstatus, 1, "Salary Slip is not submitted")


def test_cancel_ss(test):
    print("------------Cancel Salary Slip------------")
    ss = frappe.get_doc("Salary Slip", test.ss.name)
    ss.ignore_doctypes_on_cancel_all = ["Rent Application KA", "Employee"]
    ss.save()
    ss = frappe.get_doc("Salary Slip", test.ss.name)
    frappe.delete_doc("Salary Slip", test.ss.name, force=1, for_reload=True)
    try:
        ss = frappe.get_doc("Salary Slip", test.ss.name)
    except frappe.DoesNotExistError:
        ss = None
    test.assertIsNone(ss, "Salary Slip is not deleted")


def test_sstruc_assignment(test):
    print("------------Assign Salary Structure------------")
    sstruct = frappe.get_doc("Salary Structure", test.sstruc.name)
    test.assertEqual(sstruct.name, "Template",
                     "Salary Structure Template is not created")

    sstruct.custom_employee_grade = test.emp_grade.name
    sstruct.save()
    sstruct = frappe.get_doc("Salary Structure", test.sstruc.name)
    test.assertEqual(sstruct.custom_employee_grade, test.emp_grade.name,
                     "Salary Structure Template does not have Test as Employee Grade")

    sstruct.submit()
    sstruct = frappe.get_doc("Salary Structure", test.sstruc.name)
    test.assertEqual(sstruct.docstatus, 1,
                     "Salary Structure Template is not Submitted")

    grade = frappe.get_doc("Employee Grade", test.emp_grade.name)
    test.assertEqual(grade.default_salary_structure, test.sstruc.name,
                     "Salary Structure Template is not assigned to grade")

    emp = frappe.get_doc("Employee", test.emp.name)
    emp.grade = test.emp_grade.name
    emp.save()
    emp = frappe.get_doc("Employee", test.emp.name)
    test.assertEqual(emp.grade, "Test",
                     "Employee is not assigned to Test grade")

    salary_struct_assign = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee": test.emp.name},
    )
    print("salary_struct_assign", salary_struct_assign[0])
    test.assertIsNotNone(
        salary_struct_assign[0], "Salary Structure Assignment is not created")
    test.sstruc_ass = salary_struct_assign[0]


def test_cancel_assign(test):
    print("---------Cancel Assign Salary Structure---------")
    sstruct_ass = frappe.get_doc(
        "Salary Structure Assignment", test.sstruc_ass.name)
    sstruct_ass.cancel()
    sstruct_ass = frappe.get_doc(
        "Salary Structure Assignment", test.sstruc_ass.name)
    test.assertEqual(sstruct_ass.docstatus, 2,
                     "Salary Structure Assignment is not cancelled")
    frappe.delete_doc("Salary Structure Assignment", test.sstruc_ass.name)
    try:
        sstruct_ass = frappe.get_doc(
            "Salary Structure Assignment", test.sstruc_ass.name)
    except frappe.DoesNotExistError:
        sstruct_ass = None
    test.assertIsNone(
        sstruct_ass, "Salary Structure Assignment is not deleted")

    sstruct = frappe.get_doc("Salary Structure", test.sstruc.name)
    sstruct.cancel()
    sstruct = frappe.get_doc("Salary Structure", test.sstruc.name)
    test.assertEqual(sstruct.docstatus, 2,
                     "Salary Structure Template is not cancelled")


def test_submit_rent(test):
    print("------------Submit Rent------------")
    test.rent.submit()
    test.assertEqual(test.rent.docstatus, 1, "Rent is not submitted")
    emp = frappe.get_doc("Employee", test.emp.name)
    test.assertEqual(emp.custom_vehicle,
                     test.vehicle.name, "Vehicle is not assigned")
    vehicle = frappe.get_doc("Vehicle KA", test.vehicle.name)
    test.assertEqual(vehicle.rider, test.emp.name,
                     "Employee is not assigned")


def test_cancel_rent(test):
    print("------------Cancel Rent------------")
    rent = frappe.get_doc("Rent Application KA", test.rent.name)
    rent.cancel()
    test.assertEqual(rent.docstatus, 2, "Rent is not cancelled")
    sleep(3)
    rent = frappe.get_doc("Rent Application KA", test.rent.name)
    test.assertEqual(rent.is_active, 0,
                     "Rent still active after cancel")
    test.assertIsNotNone(rent.end_date, "End date is not set")

    emp = frappe.get_doc("Employee", test.emp.name)
    test.assertIn(emp.custom_vehicle, ['', None],
                  "Vehicle is not removed from Employee")
    vehicle = frappe.get_doc("Vehicle KA", test.vehicle.name)
    test.assertIn(vehicle.rider, [None, ''],
                  "Employee is not removed from Vehicle")


SStruct = {
    "amended_from": None,
    "company": "Test (Demo)",
    "currency": "BHD",
    "custom_employee_grade": "Template",
    "deductions": [
        {
            "abbr": "RD",
            "additional_amount": 0.0,
            "additional_salary": None,
            "amount": 0.0,
            "amount_based_on_formula": 0,
            "condition": "",
            "custom_component_base": 0.0,
            "custom_component_base_rate": 0.0,
            "custom_is_calculated_on_salary_slip": 0,
            "deduct_full_tax_on_selected_payroll_date": 0,
            "default_amount": 0.0,
            "depends_on_payment_days": 0,
            "do_not_include_in_total": 0,
            "exempted_from_income_tax": 0,
            "formula": "",
            "is_flexible_benefit": 0,
            "is_recurring_additional_salary": 0,
            "is_tax_applicable": 0,
            "parent": "Template",
            "parentfield": "deductions",
            "parenttype": "Salary Structure",
            "salary_component": "Rent Deduction",
            "statistical_component": 0,
            "tax_on_additional_salary": 0.0,
            "tax_on_flexible_benefit": 0.0,
            "variable_based_on_taxable_salary": 0,
            "year_to_date": 0.0
        },
        {
            "abbr": "LD",
            "additional_amount": 0.0,
            "additional_salary": None,
            "amount": 0.0,
            "amount_based_on_formula": 0,
            "condition": "",
            "custom_component_base": 0.0,
            "custom_component_base_rate": 0.0,
            "custom_is_calculated_on_salary_slip": 0,
            "deduct_full_tax_on_selected_payroll_date": 0,
            "default_amount": 0.0,
            "depends_on_payment_days": 0,
            "do_not_include_in_total": 0,
            "exempted_from_income_tax": 0,
            "formula": "",
            "is_flexible_benefit": 0,
            "is_recurring_additional_salary": 0,
            "is_tax_applicable": 0,
            "parent": "Template",
            "parentfield": "deductions",
            "parenttype": "Salary Structure",
            "salary_component": "Loan Deduction",
            "statistical_component": 0,
            "tax_on_additional_salary": 0.0,
            "tax_on_flexible_benefit": 0.0,
            "variable_based_on_taxable_salary": 0,
            "year_to_date": 0.0
        }
    ],
    "docstatus": 0,
    "doctype": "Salary Structure",
    "earnings": [
        {
            "abbr": "PB",
            "additional_amount": 0.0,
            "additional_salary": None,
            "amount": 0.0,
            "amount_based_on_formula": 0,
            "condition": "",
            "custom_component_base": 0.0,
            "custom_component_base_rate": 0.0,
            "custom_is_calculated_on_salary_slip": 0,
            "deduct_full_tax_on_selected_payroll_date": 0,
            "default_amount": 0.0,
            "depends_on_payment_days": 0,
            "do_not_include_in_total": 0,
            "exempted_from_income_tax": 0,
            "formula": "",
            "is_flexible_benefit": 0,
            "is_recurring_additional_salary": 0,
            "is_tax_applicable": 0,
            "parent": "Template",
            "parentfield": "earnings",
            "parenttype": "Salary Structure",
            "salary_component": "Previous Balance",
            "statistical_component": 0,
            "tax_on_additional_salary": 0.0,
            "tax_on_flexible_benefit": 0.0,
            "variable_based_on_taxable_salary": 0,
            "year_to_date": 0.0
        }
    ],
    "hour_rate": 0.0,
    "is_active": "Yes",
    "is_default": "No",
    "leave_encashment_amount_per_day": 0.0,
    "letter_head": None,
    "max_benefits": 0.0,
    "mode_of_payment": None,
    "modified": "2025-02-06 19:18:30.224485",
    "name": "Template",
    "net_pay": 0.0,
    "payment_account": None,
    "payroll_frequency": "",
    "salary_component": "_",
    "salary_slip_based_on_timesheet": 1,
    "total_deduction": 0.0,
    "total_earning": 0.0
}
