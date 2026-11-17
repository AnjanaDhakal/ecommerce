"""Give URL-based builder links an internal commerce destination picker."""

import copy
import json

import frappe

from ecommerce.patches.add_premium_commerce_blocks import BLOCKS as PREMIUM_BLOCKS
from ecommerce.patches.add_retail_template_collection import BLOCKS as RETAIL_BLOCKS


TARGET_BLOCKS = {
    "Commerce Promo Hero",
    "Commerce Editorial Banner",
    "Commerce Article Grid",
    "Commerce Rich Footer",
    "Retail Studio Navigation",
    "Retail Newsletter Footer",
}


def _json_object(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _merge_saved_values(fresh_model, saved_model, block):
    merged = copy.deepcopy(fresh_model)
    saved_fields = {
        field.get("name"): field
        for field in saved_model.get("fields") or []
        if isinstance(field, dict) and field.get("name")
    }
    for field in merged.get("fields") or []:
        if not isinstance(field, dict):
            continue
        name = field.get("name")
        saved = saved_fields.get(name) or {}
        if "value" in saved:
            field["value"] = copy.deepcopy(saved["value"])
        elif name in block:
            field["value"] = copy.deepcopy(block[name])
    return merged


def _upgrade_blocks(container, definitions):
    changed = False
    for section in ("header", "main", "footer"):
        for block in container.get(section) or []:
            if not isinstance(block, dict):
                continue
            block_name = block.get("block_name") or block.get("name")
            definition = definitions.get(block_name)
            if not definition:
                continue
            details = block.setdefault("block_details", {})
            saved_model = _json_object(details.get("model") or block.get("model"))
            details["model"] = _merge_saved_values(
                definition["model"],
                saved_model,
                block,
            )
            changed = True
    return changed


def execute():
    definitions = {
        definition["name"]: definition
        for definition in [*PREMIUM_BLOCKS, *RETAIL_BLOCKS]
        if definition["name"] in TARGET_BLOCKS
    }
    for block_name, definition in definitions.items():
        if not frappe.db.exists("Ecommerce Block", block_name):
            continue
        block = frappe.get_doc("Ecommerce Block", block_name)
        block.model = json.dumps(definition["model"])
        block.block = definition["html"]
        block.style = definition["style"]
        block.save(ignore_permissions=True)

    for page_name in frappe.get_all("Ecommerce Page", pluck="name"):
        page = frappe.get_doc("Ecommerce Page", page_name)
        field_value = _json_object(page.field_value)
        if _upgrade_blocks(field_value, definitions):
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)

    for template_name in frappe.get_all("Ecommerce Template", pluck="name"):
        template = frappe.get_doc("Ecommerce Template", template_name)
        data_json = _json_object(template.data_json)
        starter_content = data_json.get("starter_content")
        if isinstance(starter_content, dict) and _upgrade_blocks(
            starter_content,
            definitions,
        ):
            template.data_json = json.dumps(data_json)
            template.save(ignore_permissions=True)
