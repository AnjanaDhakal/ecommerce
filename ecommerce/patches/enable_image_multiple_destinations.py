import json

import frappe


MULTI_DESTINATION_FIELD = {
    "label": "Linked Commerce Content",
    "type": "commerce_links",
    "name": "destinations",
}


def _upgrade_image_field(field):
    children = field.get("fields") or []
    upgraded = [
        child for child in children
        if child.get("name") not in {"destination_type", "destination", "destinations"}
    ]
    upgraded.append(MULTI_DESTINATION_FIELD.copy())
    field["fields"] = upgraded


def _upgrade_items(field):
    changed = False
    for item in field.get("value") or []:
        destinations = item.get("destinations")
        if not isinstance(destinations, list):
            destinations = []
        old_type = item.pop("destination_type", None)
        old_value = item.pop("destination", None)
        if old_type and old_value and not any(
            str(link.get("type")) == str(old_type)
            and str(link.get("value")) == str(old_value)
            for link in destinations
            if isinstance(link, dict)
        ):
            destinations.append({"type": old_type, "value": old_value})
        if item.get("destinations") != destinations:
            item["destinations"] = destinations
            changed = True
        if old_type or old_value:
            changed = True
    return changed


def execute():
    if frappe.db.exists("Ecommerce Block", "Image Gallery"):
        block = frappe.get_doc("Ecommerce Block", "Image Gallery")
        model = frappe.parse_json(block.model) if isinstance(block.model, str) else block.model
        for field in model.get("fields") or []:
            if field.get("name") == "image_list":
                _upgrade_image_field(field)
        block.model = json.dumps(model)
        related_links = """
      {% if gallery_image.destination_links %}
      <nav class=\"flex flex-wrap gap-2 px-4 pb-4\" aria-label=\"Related links\">
        {% for related_link in gallery_image.destination_links %}
        <a href=\"{{ related_link.url }}\" class=\"rounded-full bg-white px-3 py-1 text-sm text-gray-700 shadow-sm hover:text-black\">
          {{ related_link.label }}
        </a>
        {% endfor %}
      </nav>
      {% endif %}
"""
        closing = "      {% if target_url %}</a>{% endif %}\n    </article>"
        if "gallery_image.destination_links" not in block.block:
            block.block = block.block.replace(
                closing,
                "      {% if target_url %}</a>{% endif %}\n" + related_links + "    </article>",
            )
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
        for section in ("header", "main", "footer"):
            for block in field_value.get(section) or []:
                if (block.get("block_name") or block.get("name")) != "Image Gallery":
                    continue
                model = block.get("block_details", {}).get("model", {})
                for field in model.get("fields") or []:
                    if field.get("name") != "image_list":
                        continue
                    _upgrade_image_field(field)
                    changed = _upgrade_items(field) or changed
                    changed = True
        if changed:
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)
