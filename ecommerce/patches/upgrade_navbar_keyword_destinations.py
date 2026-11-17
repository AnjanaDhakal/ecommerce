import json

import frappe


NAVIGATION_FIELD = {
    "label": "SEO Navigation Links",
    "type": "repeater",
    "name": "all_products",
    "fields": [
        {"label": "SEO Keyword", "type": "text", "name": "keyword"},
        {
            "label": "Linked Commerce Content",
            "type": "commerce_links",
            "name": "destinations",
        },
    ],
}


def _navigation_items(values):
    if not isinstance(values, list):
        values = [values] if values else []
    items = []
    for value in values:
        if isinstance(value, dict):
            item = value.copy()
            item["keyword"] = item.get("keyword") or item.get("label") or ""
            if not isinstance(item.get("destinations"), list):
                item["destinations"] = []
            items.append(item)
        elif value:
            items.append({"keyword": str(value), "destinations": []})
    return items


def execute():
    if frappe.db.exists("Ecommerce Block", "Navbar 2"):
        block = frappe.get_doc("Ecommerce Block", "Navbar 2")
        model = frappe.parse_json(block.model) if isinstance(block.model, str) else block.model
        fields = model.get("fields") or []
        model["fields"] = [
            NAVIGATION_FIELD.copy() if field.get("name") == "all_products" else field
            for field in fields
        ]
        block.model = json.dumps(model)
        old_navigation = """{% for link in all_products %}
      <a href=\"{{ vendor_website_url }}\" title=\"{{ link }}\" class=\"hover:text-[#991b60] transition-colors text-sm text-[#3d3d3d]\">
        {{ link }}
      </a>
      {% endfor %}"""
        new_navigation = """{% for link in all_products %}
      {% if link.keyword and link.destination_url %}
      <a href=\"{{ link.destination_url }}\" title=\"{{ link.keyword }}\" class=\"hover:text-[#991b60] transition-colors text-sm text-[#3d3d3d]\">
        {{ link.keyword }}
      </a>
      {% elif link.keyword %}
      <span class=\"text-sm text-[#3d3d3d]\">{{ link.keyword }}</span>
      {% endif %}
      {% endfor %}"""
        block.block = block.block.replace(old_navigation, new_navigation)
        block.save(ignore_permissions=True)

    for page_name in frappe.get_all("Ecommerce Page", pluck="name"):
        page = frappe.get_doc("Ecommerce Page", page_name)
        field_value = page.field_value
        if isinstance(field_value, str):
            try:
                field_value = frappe.parse_json(field_value)
            except (TypeError, ValueError):
                continue
        if not isinstance(field_value, dict):
            continue
        changed = False
        for block in field_value.get("header") or []:
            if (block.get("block_name") or block.get("name")) != "Navbar 2":
                continue
            model = block.get("block_details", {}).get("model", {})
            fields = model.get("fields") or []
            upgraded_fields = []
            for field in fields:
                if field.get("name") != "all_products":
                    upgraded_fields.append(field)
                    continue
                upgraded = NAVIGATION_FIELD.copy()
                upgraded["fields"] = [child.copy() for child in NAVIGATION_FIELD["fields"]]
                upgraded["value"] = _navigation_items(field.get("value"))
                upgraded_fields.append(upgraded)
                changed = True
            model["fields"] = upgraded_fields
        if changed:
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)
