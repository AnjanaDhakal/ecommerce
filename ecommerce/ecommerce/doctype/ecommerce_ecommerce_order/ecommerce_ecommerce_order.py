# Copyright (c) 2026, Ecommerce contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils import cint, now_datetime


class EcommerceEcommerceOrder(Document):
	def autoname(self):
		vendor_id = str(self.vendor_id or "").strip()
		vendor_token = re.sub(
			r"[^A-Za-z0-9-]+", "-", vendor_id
		).strip("-")
		if not vendor_token:
			frappe.throw(_("Vendor is required before creating an ecommerce order."))

		date_token = now_datetime().strftime("%y%m%d")
		prefix = f"E-{vendor_token}-{date_token}"
		sequence = cint(getseries(f"{prefix}-", 1))
		self.name = prefix if sequence == 1 else f"{prefix}-{sequence}"
