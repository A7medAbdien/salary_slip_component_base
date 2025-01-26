import frappe


def delete_all():
    las = frappe.get_all("Loan Application KA", fields=["name"])
    for la in las:
        la = frappe.get_doc("Loan Application KA", la.name)
        if la.docstatus == 1:
            la.cancel()
        la.delete()
