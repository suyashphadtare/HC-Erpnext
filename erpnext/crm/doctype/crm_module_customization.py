from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, cint, cstr, date_diff, rounded, flt, getdate, nowdate, \
	get_first_day, get_last_day,money_in_words, now, nowtime
from frappe import _
from frappe.model.db_query import DatabaseQuery



# Validation for emailid on lead form
def validate_emaiid(doc,method):
	if frappe.db.sql("""select name from `tabLead` where name!='%s' and email_id='%s'"""%(doc.name,doc.email_id)):
		frappe.msgprint("Email Id '%s' is already assigned for another lead"%doc.email_id,raise_exception=1)