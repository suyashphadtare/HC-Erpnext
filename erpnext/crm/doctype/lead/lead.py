# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, validate_email_add, cint, comma_and
from frappe import session
from frappe.model.mapper import get_mapped_doc

from erpnext.controllers.selling_controller import SellingController
from erpnext.utilities.address_and_contact import load_address_and_contact

sender_field = "email_id"

class Lead(SellingController):
	def get_feed(self):
		return '{0}: {1}'.format(_(self.status), self.lead_name)

	def onload(self):
		customer = frappe.db.get_value("Customer", {"lead_name": self.name})
		self.get("__onload").is_customer = customer
		load_address_and_contact(self, "lead")

	def validate(self):
		self._prev = frappe._dict({
			"contact_date": frappe.db.get_value("Lead", self.name, "contact_date") if \
				(not cint(self.get("__islocal"))) else None,
			"contact_by": frappe.db.get_value("Lead", self.name, "contact_by") if \
				(not cint(self.get("__islocal"))) else None,
		})

		self.set_status()
		self.check_email_id_is_unique()

		if self.source == 'Campaign' and not self.campaign_name and session['user'] != 'Guest':
			frappe.throw(_("Campaign Name is required"))

		if self.email_id:
			validate_email_add(self.email_id, True)

			if self.email_id == self.lead_owner:
				# Lead Owner cannot be same as the Lead
				self.lead_owner = None

	def on_update(self):
		self.add_calendar_event()

	def add_calendar_event(self, opts=None, force=False):
		super(Lead, self).add_calendar_event({
			"owner": self.lead_owner,
			"starts_on": self.contact_date,
			"subject": ('Contact ' + cstr(self.lead_name)),
			"description": ('Contact ' + cstr(self.lead_name)) + \
				(self.contact_by and ('. By : ' + cstr(self.contact_by)) or '')
		}, force)

	#Customization Validation for emailid
	def check_email_id_is_unique(self):
		if self.email_id:
			# validate email is unique
			email_list = frappe.db.sql("""select name from tabLead where email_id=%s""",
				self.email_id)
			email_list = [e[0] for e in email_list if e[0]!=self.name]
			if len(email_list) > 0:
				frappe.throw(_("Email id must be unique, already exists for {0}").format(comma_and(email_list)))

	def on_trash(self):
		frappe.db.sql("""update `tabIssue` set lead='' where lead=%s""",
			self.name)

		self.delete_events()

	def has_customer(self):
		return frappe.db.get_value("Customer", {"lead_name": self.name})

	def has_opportunity(self):
		return frappe.db.get_value("Opportunity", {"lead": self.name, "status": ["!=", "Lost"]})

@frappe.whitelist()
def make_customer(source_name, target_doc=None):
	return _make_customer(source_name, target_doc)

def _make_customer(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		if source.company_name:
			target.customer_type = "Company"
			target.customer_name = source.company_name
		else:
			target.customer_type = "Individual"
			target.customer_name = source.lead_name

		target.customer_group = frappe.db.get_default("customer_group")

	doclist = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Customer",
			"field_map": {
				"name": "lead_name",
				"company_name": "customer_name",
				"contact_no": "phone_1",
				"fax": "fax_1"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

@frappe.whitelist()
def make_opportunity(source_name, target_doc=None):
	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Opportunity",
			"field_map": {
				"campaign_name": "campaign",
				"doctype": "enquiry_from",
				"name": "lead",
				"lead_name": "contact_display",
				"company_name": "customer_name",
				"email_id": "contact_email",
				"mobile_no": "contact_mobile"
			}
		}}, target_doc)

	return target_doc

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Quotation",
			"field_map": {
				"name": "lead",
				"lead_name": "customer_name",
			}
		}}, target_doc)
	target_doc.quotation_to = "Lead"

	return target_doc

#Customization for creating enquiry from lead
@frappe.whitelist()
def create_enquiry(source_name, target_doc=None):
	def set_missing_values(source, target):	
		target.enquiry_from = "Lead"
	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Enquiry",
			"field_map": {
				"lead_name": source_name,
			},
		}}, target_doc,set_missing_values)
	target_doc.quotation_to = "Lead"

	return target_doc

@frappe.whitelist()
def get_lead_details(lead):
	if not lead: return {}

	from erpnext.accounts.party import set_address_details
	out = frappe._dict()

	lead_doc = frappe.get_doc("Lead", lead)
	lead = lead_doc

	out.update({
		"territory": lead.territory,
		"customer_name": lead.company_name or lead.lead_name,
		"contact_display": lead.lead_name,
		"contact_email": lead.email_id,
		"contact_mobile": lead.mobile_no,
		"contact_phone": lead.phone,
	})

	set_address_details(out, lead, "Lead")

	return out
