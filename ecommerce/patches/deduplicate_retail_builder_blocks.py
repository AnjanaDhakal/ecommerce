import json

import frappe


MODEL_BASE_BLOCKS = {
    "retail_announcement": "Retail Announcement Bar",
    "retail_navigation": "Retail Studio Navigation",
    "retail_campaign_hero": "Retail Campaign Hero",
    "retail_collection_mosaic": "Retail Collection Mosaic",
    "retail_story_split": "Retail Story Split",
    "retail_value_icons": "Retail Value Icons",
    "retail_quote_wall": "Retail Quote Wall",
    "retail_newsletter_footer": "Retail Newsletter Footer",
    "commerce_product_shelf": "Commerce Product Shelf",
}


def _json_object(value):
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "{}")
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _model_name(instance, block_models):
    details = instance.get("block_details") or {}
    model = details.get("model") or {}
    model_name = model.get("block_name") if isinstance(model, dict) else None
    if model_name:
        return str(model_name)
    current_name = instance.get("name") or instance.get("block_name")
    return block_models.get(str(current_name or ""), "")


def _normalize_instance(instance, block_models):
    if not isinstance(instance, dict):
        return False
    base_name = MODEL_BASE_BLOCKS.get(_model_name(instance, block_models))
    if not base_name or not frappe.db.exists("Ecommerce Block", base_name):
        return False

    changed = False
    for key in ("name", "block_name"):
        if instance.get(key) != base_name:
            instance[key] = base_name
            changed = True

    details = instance.setdefault("block_details", {})
    if details.get("name") != base_name:
        details["name"] = base_name
        changed = True
    return changed


def _normalize_sections(values, block_models):
    changed = False
    for area in ("header", "main", "footer"):
        for instance in values.get(area) or []:
            if _normalize_instance(instance, block_models):
                changed = True
    return changed


def execute():
    blocks = frappe.get_all(
        "Ecommerce Block",
        fields=["name", "model"],
    )
    block_models = {
        block.name: str(_json_object(block.model).get("block_name") or "")
        for block in blocks
    }

    # Rewrite template starter instances first, preserving their configured
    # field values while pointing them at the shared implementation.
    for template in frappe.get_all(
        "Ecommerce Template", fields=["name", "data_json"]
    ):
        config = _json_object(template.data_json)
        starter = config.get("starter_content") or {}
        if _normalize_sections(starter, block_models):
            frappe.db.set_value(
                "Ecommerce Template",
                template.name,
                "data_json",
                json.dumps(config, indent=2),
                update_modified=False,
            )

    # Existing pages may contain edited copies of the same instances. Change
    # only their block reference; their local field values remain untouched.
    for page in frappe.get_all(
        "Ecommerce Page", fields=["name", "field_value"]
    ):
        values = _json_object(page.field_value)
        if _normalize_sections(values, block_models):
            frappe.db.set_value(
                "Ecommerce Page",
                page.name,
                "field_value",
                json.dumps(values),
                update_modified=False,
            )

    # References are now normalized, so the renamed copies are redundant.
    for block in blocks:
        base_name = MODEL_BASE_BLOCKS.get(block_models.get(block.name))
        if base_name and block.name != base_name:
            frappe.delete_doc(
                "Ecommerce Block",
                block.name,
                ignore_permissions=True,
                force=True,
            )
