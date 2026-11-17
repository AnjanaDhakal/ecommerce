# Copyright (c) 2025, Ecommerce contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from ecommerce.storefront_domains import set_storefront_identity


class EcommerceVendorWebsite(Document):
	def validate(self):
		self.website_link = " ".join(str(self.website_link or "").split())
		self._validate_vendor_website_name()
		set_storefront_identity(self)

	def _validate_vendor_website_name(self):
		"""Keep display names unique for one vendor, not across all vendors."""
		if not self.vendor_id or not self.website_link:
			return

		website_name = self.website_link.casefold()
		for website in frappe.get_all(
			"Ecommerce Vendor Website",
			filters={"vendor_id": self.vendor_id},
			fields=["name", "website_link"],
		):
			if str(website.name) == str(self.name or ""):
				continue
			existing_name = " ".join(str(website.website_link or "").split()).casefold()
			if existing_name == website_name:
				frappe.throw(
					_('You already have a website named "{0}".').format(
						self.website_link
					)
				)
