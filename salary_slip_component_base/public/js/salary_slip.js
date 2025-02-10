frappe.ui.form.on('Salary Slip', {
	setup: function(frm) {
		$.each(["earnings", "deductions"], function(i, table_fieldname) {
			frm.get_field(table_fieldname).grid.editable_fields = [
				{ fieldname: "salary_component", columns: 2 },
				{ fieldname: "custom_component_base", columns: 2 },
				{ fieldname: "custom_component_base_rate", columns: 2 },
				{ fieldname: "amount", columns: 2 },
			];
		});
	},
	onload: function(frm) {
		frm.ignore_doctypes_on_cancel_all = ["Rent Application KA"];
	},
	refresh: function(frm) {
	}
});

