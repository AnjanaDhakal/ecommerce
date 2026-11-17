from collections import defaultdict

import frappe
from frappe.model.rename_doc import rename_doc


DOCTYPE = "Ecommerce Template"
WEBSITE_DOCTYPE = "Ecommerce Vendor Website"


def execute():
	"""Give builder templates stable names and merge legacy duplicates.

	Fixtures are matched by ``name``. Historically this DocType used random
	names, while application patches matched on ``page_name``. On migrate that
	allowed a patch-created record and a fixture-created record to coexist.
	"""
	if not frappe.db.table_exists(DOCTYPE):
		return

	groups = defaultdict(list)
	for row in frappe.get_all(
		DOCTYPE,
		fields=["name", "page_name", "modified"],
		order_by="modified desc",
	):
		page_name = (row.page_name or "").strip() or row.name
		if page_name != row.page_name:
			frappe.db.set_value(
				DOCTYPE, row.name, "page_name", page_name, update_modified=False
			)
		groups[page_name].append(row.name)

	for page_name, names in groups.items():
		# A name belonging to a different logical template is unsafe to merge.
		if frappe.db.exists(DOCTYPE, page_name) and page_name not in names:
			frappe.throw(
				f"Cannot normalize builder template {page_name!r}: "
				"that document name is already used by another template."
			)

		# Website.template is intentionally a Data field, so Frappe's rename
		# machinery cannot discover and update it like a Link field.
		if frappe.db.table_exists(WEBSITE_DOCTYPE):
			for old_name in names:
				frappe.db.set_value(
					WEBSITE_DOCTYPE,
					{"template": old_name},
					"template",
					page_name,
					update_modified=False,
				)

		if not frappe.db.exists(DOCTYPE, page_name):
			rename_doc(
				DOCTYPE,
				names[0],
				page_name,
				force=True,
				ignore_permissions=True,
				show_alert=False,
				rebuild_search=False,
			)

		# Merge updates every Link field (including Builder Page.template)
		# before deleting the redundant record.
		for duplicate_name in names:
			if duplicate_name == page_name or not frappe.db.exists(
				DOCTYPE, duplicate_name
			):
				continue
			rename_doc(
				DOCTYPE,
				duplicate_name,
				page_name,
				force=True,
				merge=True,
				ignore_permissions=True,
				show_alert=False,
				rebuild_search=False,
			)

	# Repair any stale Data-field reference whose old template record was
	# already removed before this patch ran. The root page uses a real Link and
	# therefore contains the canonical value after the merges above.
	if frappe.db.table_exists(WEBSITE_DOCTYPE):
		for website in frappe.get_all(
			WEBSITE_DOCTYPE, fields=["name", "template"]
		):
			if not website.template or frappe.db.exists(DOCTYPE, website.template):
				continue
			pages = frappe.get_all(
				"Ecommerce Page",
				filters={"website_id": website.name},
				fields=["name", "page", "parent1", "template"],
				order_by="creation asc",
			)
			root_pages = [page for page in pages if not page.parent1]
			root_page = next(
				(page for page in root_pages if page.page == "Home"),
				root_pages[0] if root_pages else None,
			)
			if root_page and root_page.template and frappe.db.exists(
				DOCTYPE, root_page.template
			):
				frappe.db.set_value(
					WEBSITE_DOCTYPE,
					website.name,
					"template",
					root_page.template,
					update_modified=False,
				)
