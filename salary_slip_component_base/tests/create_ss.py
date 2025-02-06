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
            "start_date": getdate("26-01-2025"),
        }).insert()

    def test_cast_rent(self):
        test_submit_rent(self)
        test_cancel_rent(self)

    def tearDown(self):
        print("------------Delete Rent------------")
        frappe.delete_doc("Rent Application KA", self.rent.name)
        frappe.delete_doc("Vehicle KA", self.vehicle.name)
        frappe.delete_doc("Employee", self.emp.name)

    @classmethod
    def tearDownClass(cls):
        frappe.db.rollback()


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
