// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext");
cur_frm.email_field = "email_id";

cur_frm.add_fetch('location', 'area', 'location_name');

erpnext.LeadController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.customer.get_query = function(doc, cdt, cdn) {
				return { query: "erpnext.controllers.queries.customer_query" } }
	},

	onload: function() {
		if(cur_frm.fields_dict.lead_owner.df.options.match(/^User/)) {
			cur_frm.fields_dict.lead_owner.get_query = function(doc, cdt, cdn) {
				return { query:"frappe.core.doctype.user.user.user_query" } }
		}

		if(cur_frm.fields_dict.contact_by.df.options.match(/^User/)) {
			cur_frm.fields_dict.contact_by.get_query = function(doc, cdt, cdn) {
				return { query:"frappe.core.doctype.user.user.user_query" } }
		}
	},

	refresh: function() {
		var doc = this.frm.doc;
		erpnext.toggle_naming_series();

		if(!this.frm.doc.__islocal && this.frm.doc.__onload && !this.frm.doc.__onload.is_customer) {
			this.frm.add_custom_button(__("Create Customer"), this.create_customer,
				frappe.boot.doctype_icons["Customer"], "btn-default");
			// this.frm.add_custom_button(__("Create Opportunity"), this.create_opportunity,
			// 	frappe.boot.doctype_icons["Opportunity"], "btn-default");
			// this.frm.add_custom_button(__("Make Quotation"), this.make_quotation,
			// 	frappe.boot.doctype_icons["Quotation"], "btn-default");
		}

		// if(!this.frm.doc.__islocal){
		// 	this.frm.add_custom_button(__("Create Enquiry"), this.create_enquiry,
		// 		frappe.boot.doctype_icons["Enquiry"], "btn-default");
		// }

		if(!this.frm.doc.__islocal) {
			erpnext.utils.render_address_and_contact(cur_frm);
		}
	},

	create_customer: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.lead.lead.make_customer",
			frm: cur_frm
		})
	},

	create_opportunity: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.lead.lead.make_opportunity",
			frm: cur_frm
		})
	},
	
	make_quotation: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.lead.lead.make_quotation",
			frm: cur_frm
		})
	},

	create_enquiry: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.lead.lead.create_enquiry",
			frm: cur_frm
		})
	}
});

$.extend(cur_frm.cscript, new erpnext.LeadController({frm: cur_frm}));



cur_frm.fields_dict['enquiry_sub_source'].get_query = function(doc) {
	return {
		filters: {
			
			"enquiry_source": doc.source
		}
	}
}