import json

import frappe


CATEGORY_FIELD = {
    "label": "Categories to show",
    "type": "categories",
    "name": "menu_categories",
    "hint": "Choose which categories appear below the main navigation.",
}


def _loads(value, fallback):
    if isinstance(value, type(fallback)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(fallback)) else fallback
    except (TypeError, ValueError):
        return fallback


def _add_model_field(model):
    fields = model.setdefault("fields", [])
    if any((field.get("name") or field.get("key")) == "menu_categories" for field in fields):
        return False
    fields.append(dict(CATEGORY_FIELD))
    return True


def _add_instance_field(fields):
    if any((field.get("name") or field.get("key")) == "menu_categories" for field in fields):
        return False
    fields.append({**CATEGORY_FIELD, "value": []})
    return True


def execute():
    if not frappe.db.exists("Ecommerce Block", "Navbar 2"):
        return

    block = frappe.get_doc("Ecommerce Block", "Navbar 2")
    model = _loads(block.model, {})
    if _add_model_field(model):
        block.model = json.dumps(model)
        block.save(ignore_permissions=True)

    changed_websites = set()
    for page_name in frappe.get_all("Ecommerce Page", pluck="name"):
        page = frappe.get_doc("Ecommerce Page", page_name)
        field_value = _loads(page.field_value, {})
        page_changed = False
        for page_block in field_value.get("header") or []:
            if (page_block.get("block_name") or page_block.get("name")) != "Navbar 2":
                continue
            model = page_block.setdefault("block_details", {}).setdefault("model", {})
            fields = model.setdefault("fields", [])
            if _add_instance_field(fields):
                page_changed = True
        if page_changed:
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)
            if page.website_id:
                changed_websites.add(page.website_id)

    if changed_websites:
        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages

        for website_id in changed_websites:
            _republish_website_pages(website_id)
