import copy
import json

import frappe

from ecommerce.default_ecommerce_catalogue import ensure_default_ecommerce_catalogue
from ecommerce.patches.add_retail_template_collection import BLOCKS
from ecommerce.api import update_publish_data


GENERIC_LABELS = ["New", "Shop", "Collections", "About"]


def _category_links(categories):
    return [
        {
            "label": category.categories_name,
            "destinations": [{
                "type": "category",
                "value": category.name,
                "label": category.categories_name,
            }],
            "url": "",
        }
        for category in categories[:3]
    ]


def _refresh_navigation_block_definition():
    definition = next(
        item for item in BLOCKS if item["name"] == "Retail Studio Navigation"
    )
    if not frappe.db.exists("Ecommerce Block", definition["name"]):
        return
    block = frappe.get_doc("Ecommerce Block", definition["name"])
    block.model = json.dumps(definition["model"])
    block.block = definition["html"]
    block.style = definition["style"]
    block.save(ignore_permissions=True)


def _replace_generic_links(values, links):
    changed = False
    for block in values.get("header") or []:
        if not isinstance(block, dict):
            continue
        details = block.get("block_details") or {}
        model = details.get("model") or block.get("model") or {}
        if isinstance(model, str):
            try:
                model = json.loads(model)
            except (TypeError, ValueError):
                continue
        if str(model.get("block_name") or "").strip().lower() != "retail_navigation":
            continue
        for field in model.get("fields") or []:
            if (field.get("name") or field.get("key")) != "links":
                continue
            current = field.get("value", field.get("default", [])) or []
            labels = [
                str(item.get("label") or "")
                for item in current
                if isinstance(item, dict)
            ]
            if current and labels != GENERIC_LABELS:
                continue
            field["value"] = copy.deepcopy(links)
            changed = True
    return changed


def _refresh_category_images(value, images_by_category):
    changed = False
    if isinstance(value, list):
        for item in value:
            changed = _refresh_category_images(item, images_by_category) or changed
        return changed
    if not isinstance(value, dict):
        return False

    destinations = value.get("destinations")
    if "image" in value and isinstance(destinations, list):
        for destination in destinations:
            if not isinstance(destination, dict):
                continue
            if str(destination.get("type") or "").lower() != "category":
                continue
            image = images_by_category.get(str(destination.get("value") or ""))
            if image and value.get("image") != image:
                value["image"] = image
                changed = True
                break

    for item in value.values():
        changed = _refresh_category_images(item, images_by_category) or changed
    return changed


def execute():
    _refresh_navigation_block_definition()
    for website_id in frappe.get_all(
        "Ecommerce Vendor Website",
        filters={"type": "Ecommerce"},
        pluck="name",
    ):
        catalogue = ensure_default_ecommerce_catalogue(
            website_id,
            refresh_existing=True,
        )
        categories = catalogue.get("categories") or []
        links = _category_links(categories)
        images_by_category = {
            str(category.name): category.categories_logo
            for category in categories
            if category.categories_logo
        }
        if not links:
            continue
        for page in frappe.get_all(
            "Ecommerce Page",
            filters={"website_id": website_id},
            fields=["name", "page", "field_value"],
        ):
            values = json.loads(page.field_value or "{}")
            changed = _replace_generic_links(values, links)
            changed = _refresh_category_images(
                values,
                images_by_category,
            ) or changed
            if not changed:
                continue
            result = update_publish_data(
                _page_name=page.name,
                _title=page.page,
                _field_value=values,
                _commit=False,
            )
            if not isinstance(result, dict) or result.get("status") != "success":
                frappe.throw(
                    (result or {}).get("message")
                    or f"Unable to refresh navigation for {page.name}"
                )
