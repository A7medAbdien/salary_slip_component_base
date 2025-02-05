from salary_slip_component_base.overrides.payroll_entry import (
    custom_set_payable_amount_against_payroll_payable_account,
    custom_submit_salary_slips,
    custom_get_salary_slip_details
)
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from salary_slip_component_base.overrides.salary_slip import (
    custom_set_time_sheet,
    custom_on_submit
)
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
app_name = "salary_slip_component_base"
app_title = "Salary Slip Component Base"
app_publisher = "a"
app_description = "An extention for the Payroll Salary Slips to allow a base component wise"
app_email = "ahmed.g.abdien@gmail.com"
app_license = "mit"

# Override standard doctype methods
# ----------------
SalarySlip.set_time_sheet = custom_set_time_sheet
SalarySlip.on_submit = custom_on_submit
PayrollEntry.set_payable_amount_against_payroll_payable_account = \
    custom_set_payable_amount_against_payroll_payable_account
PayrollEntry.submit_salary_slips = custom_submit_salary_slips
PayrollEntry.get_salary_slip_details = custom_get_salary_slip_details

fixtures = [
    {"dt": "Workflow"}
]
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "salary_slip_component_base",
# 		"logo": "/assets/salary_slip_component_base/logo.png",
# 		"title": "Salary Slip Component Base",
# 		"route": "/salary_slip_component_base",
# 		"has_permission": "salary_slip_component_base.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/salary_slip_component_base/css/salary_slip_component_base.css"
# app_include_js = "/assets/salary_slip_component_base/js/salary_slip_component_base.js"

# include js, css files in header of web template
# web_include_css = "/assets/salary_slip_component_base/css/salary_slip_component_base.css"
# web_include_js = "/assets/salary_slip_component_base/js/salary_slip_component_base.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "salary_slip_component_base/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {"Salary Slip": "public/js/salary_slip.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "salary_slip_component_base/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "salary_slip_component_base.utils.jinja_methods",
# 	"filters": "salary_slip_component_base.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "salary_slip_component_base.install.before_install"
# after_install = "salary_slip_component_base.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "salary_slip_component_base.uninstall.before_uninstall"
# after_uninstall = "salary_slip_component_base.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "salary_slip_component_base.utils.before_app_install"
# after_app_install = "salary_slip_component_base.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "salary_slip_component_base.utils.before_app_uninstall"
# after_app_uninstall = "salary_slip_component_base.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "salary_slip_component_base.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes
override_doctype_class = {
    # 	"ToDo": "custom_app.overrides.CustomToDo"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Salary Slip": {
        "on_update": "salary_slip_component_base.events.salary_slip.on_update",
        # "before_save": "salary_slip_component_base.events.salary_slip.before_save",
        "on_submit": "salary_slip_component_base.events.salary_slip.on_submit",
        "before_cancel": "salary_slip_component_base.events.salary_slip.before_cancel",
        "on_trash": "salary_slip_component_base.events.salary_slip.on_trash",
    },
    "Employee": {
        "on_update": "salary_slip_component_base.events.employee.on_update",
    },
    "Salary Structure": {
        "on_submit": "salary_slip_component_base.events.salary_structure.on_submit",
        "on_cancel": "salary_slip_component_base.events.salary_structure.on_cancel",
    },
    "Employee Grade": {
        "on_update": "salary_slip_component_base.events.employee_grade.on_update",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"salary_slip_component_base.tasks.all"
# 	],
# 	"daily": [
# 		"salary_slip_component_base.tasks.daily"
# 	],
# 	"hourly": [
# 		"salary_slip_component_base.tasks.hourly"
# 	],
# 	"weekly": [
# 		"salary_slip_component_base.tasks.weekly"
# 	],
# 	"monthly": [
# 		"salary_slip_component_base.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "salary_slip_component_base.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "salary_slip_component_base.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "salary_slip_component_base.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["salary_slip_component_base.utils.before_request"]
# after_request = ["salary_slip_component_base.utils.after_request"]

# Job Events
# ----------
# before_job = ["salary_slip_component_base.utils.before_job"]
# after_job = ["salary_slip_component_base.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"salary_slip_component_base.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
