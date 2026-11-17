# Copyright (c) 2025, Ecommerce contributors
# For license information, please see license.txt

# import frappe
import re

from frappe.model.document import Document


class EcommerceBrand(Document):
	def before_validate(self):
		if self.brand_name and not self.slug:
			self.slug = re.sub(r"[^a-z0-9]+", "-", self.brand_name.lower()).strip("-")
