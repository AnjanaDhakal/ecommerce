# Copyright (c) 2025, Ecommerce contributors
# For license information, please see license.txt

import frappe
import json
import re

from frappe.model.document import Document


class EcommerceProduct(Document):
	def before_validate(self):
		if self.product_name:
			base_slug = self.slug or self.product_name
			self.slug = _unique_product_slug(self, base_slug)

		if not self.categories and self.catagories:
			self.append("categories", {"category": self.catagories})

		if not self.variants and self.varient:
			try:
				variants = json.loads(self.varient) if isinstance(self.varient, str) else self.varient
			except (TypeError, ValueError):
				variants = []
			for variant in variants or []:
				if isinstance(variant, dict):
					self.append("variants", _variant_row(variant))

		if self.categories:
			self.catagories = self.categories[0].category
		if self.variants:
			self.varient = json.dumps([_legacy_variant(row) for row in self.variants])


def _slugify(value):
	return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-") or "product"


def _unique_product_slug(product, value):
	"""Keep storefront product paths unique inside a vendor website."""
	base_slug = _slugify(value)
	filters = {"website": product.website, "slug": base_slug}
	if product.name and not product.is_new():
		filters["name"] = ["!=", product.name]
	if not frappe.db.exists("Ecommerce Product", filters):
		return base_slug

	preferred_suffix = str(product.name or "").strip()
	if preferred_suffix and not preferred_suffix.startswith("new-"):
		candidate = f"{base_slug}-{_slugify(preferred_suffix)}"
		filters = {"website": product.website, "slug": candidate}
		if product.name and not product.is_new():
			filters["name"] = ["!=", product.name]
		if not frappe.db.exists("Ecommerce Product", filters):
			return candidate

	suffix = 2
	while frappe.db.exists(
		"Ecommerce Product",
		{"website": product.website, "slug": f"{base_slug}-{suffix}"},
	):
		suffix += 1
	return f"{base_slug}-{suffix}"


def _variant_row(value):
	return {
		"variant_name": value.get("variant_name") or value.get("name"),
		"variant_image": value.get("variant_image") or value.get("image"),
		"discounted_price": value.get("discounted_price"),
		"selling_price": value.get("selling_price"),
		"cost_price": value.get("cost_price"),
		"weight": value.get("weight"),
		"volume": value.get("volume") or value.get("volumne"),
		"quantity": value.get("quantity"),
		"sku": value.get("sku"),
	}


def _legacy_variant(row):
	return {
		"name": row.variant_name,
		"image": row.variant_image,
		"variant_image": row.variant_image,
		"discounted_price": row.discounted_price,
		"selling_price": row.selling_price,
		"cost_price": row.cost_price,
		"weight": row.weight,
		"volumne": row.volume,
		"quantity": row.quantity,
		"sku": row.sku,
	}
