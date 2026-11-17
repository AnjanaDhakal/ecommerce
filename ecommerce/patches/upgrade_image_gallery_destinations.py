import json

import frappe

from ecommerce.patches.migrate_builder_commerce_relations import _update_image_gallery_block


DESTINATION_FIELDS = [
    {
        "label": "Destination Type",
        "type": "select",
        "name": "destination_type",
        "options": [
            {"label": "Brand", "value": "brand"},
            {"label": "Category", "value": "category"},
            {"label": "Product", "value": "product"},
            {"label": "Builder Page", "value": "page"},
        ],
    },
    {
        "label": "Destination",
        "type": "commerce_link",
        "name": "destination",
        "destination_type_field": "destination_type",
    },
]


def execute():
    _update_image_gallery_block()
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
        for section in ("header", "main", "footer"):
            for block in field_value.get(section) or []:
                if (block.get("block_name") or block.get("name")) != "Image Gallery":
                    continue
                model = block.get("block_details", {}).get("model", {})
                for field in model.get("fields") or []:
                    if field.get("name") != "image_list":
                        continue
                    existing_names = {child.get("name") for child in field.get("fields") or []}
                    for destination_field in DESTINATION_FIELDS:
                        if destination_field["name"] not in existing_names:
                            field.setdefault("fields", []).append(destination_field.copy())
                            changed = True
        if changed:
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)
