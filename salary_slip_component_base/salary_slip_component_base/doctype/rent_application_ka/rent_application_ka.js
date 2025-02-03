// Copyright (c) 2025, a and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Application KA", {
    onload(frm) {
        if (frm.doc.payment_schedules)
            reorderChildTable(frm);
    },
});
const reorderChildTable = (frm) => {
    let child_table_data = frm.doc.payment_schedules;
    child_table_data.sort((a, b) =>
        b.start_date.localeCompare(a.start_date)
    );
    child_table_data.forEach((item, index) => {
        item.idx = index + 1;
    });
    frm.refresh_field("payment_schedules");
};

