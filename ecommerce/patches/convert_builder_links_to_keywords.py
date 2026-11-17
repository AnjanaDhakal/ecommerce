import json
import re
from urllib.parse import urlparse

import frappe


def _is_public_url(value):
    try:
        parsed = urlparse(str(value or "").strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def _keyword(value):
    value = str(value or "").strip()
    if not _is_public_url(value):
        return value
    parsed = urlparse(value)
    path_parts = [part for part in parsed.path.split("/") if part]
    source = path_parts[-1] if path_parts else parsed.netloc.split(":", 1)[0]
    source = re.sub(r"^www\.", "", source, flags=re.IGNORECASE)
    if not path_parts:
        source = source.split(".", 1)[0]
    return re.sub(r"[-_]+", " ", source).strip().title() or "Website"


def execute():
    _update_block_definitions()

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
        canonical_candidate = None
        for section in ("header", "main", "footer"):
            for block in field_value.get(section) or []:
                block_name = block.get("block_name") or block.get("name")
                model = block.get("block_details", {}).get("model", {})
                if block_name == "Navbar 2":
                    for field in model.get("fields") or []:
                        if field.get("name") != "all_products":
                            continue
                        field["label"] = "SEO Navigation Keywords"
                        values = field.get("value") or []
                        if not isinstance(values, list):
                            values = [values]
                        for value in values:
                            if not canonical_candidate and _is_public_url(value):
                                canonical_candidate = value
                        keywords = [_keyword(value) for value in values if _keyword(value)]
                        if keywords != values:
                            field["value"] = keywords
                            changed = True

                if block_name == "Image Gallery":
                    for field in model.get("fields") or []:
                        if field.get("name") != "image_list":
                            continue
                        for child in field.get("fields") or []:
                            if child.get("name") == "link":
                                child.update({
                                    "name": "seo_keyword",
                                    "label": "SEO Link Keyword",
                                    "type": "text",
                                })
                                changed = True
                        for item in field.get("value") or []:
                            old_link = item.pop("link", None)
                            if old_link and not canonical_candidate and _is_public_url(old_link):
                                canonical_candidate = old_link
                            if old_link and not item.get("seo_keyword"):
                                item["seo_keyword"] = _keyword(old_link)
                                changed = True

        if canonical_candidate:
            website = frappe.get_doc("Ecommerce Vendor Website", page.website_id)
            if not website.canonical_url:
                website.canonical_url = canonical_candidate
                website.save(ignore_permissions=True)
        if changed:
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)


def _update_block_definitions():
    if frappe.db.exists("Ecommerce Block", "Navbar 2"):
        block = frappe.get_doc("Ecommerce Block", "Navbar 2")
        model = frappe.parse_json(block.model) if isinstance(block.model, str) else block.model
        for field in model.get("fields") or []:
            if field.get("name") == "all_products":
                field["label"] = "SEO Navigation Keywords"
        block.model = json.dumps(model)
        block.block = block.block.replace(
            '<a href="{{ link }}"',
            '<a href="{{ vendor_website_url }}" title="{{ link }}"',
        )
        block.save(ignore_permissions=True)

    if frappe.db.exists("Ecommerce Block", "Image Gallery"):
        block = frappe.get_doc("Ecommerce Block", "Image Gallery")
        model = frappe.parse_json(block.model) if isinstance(block.model, str) else block.model
        for field in model.get("fields") or []:
            if field.get("name") != "image_list":
                continue
            for child in field.get("fields") or []:
                if child.get("name") == "link":
                    child.update({
                        "name": "seo_keyword",
                        "label": "SEO Link Keyword",
                        "type": "text",
                    })
        block.model = json.dumps(model)
        block.block = block.block.replace(
            "gallery_image.destination_url or gallery_image.link",
            "gallery_image.destination_url or (vendor_website_url if gallery_image.seo_keyword else none)",
        ).replace(
            'class="block">',
            'class="block" title="{{ gallery_image.seo_keyword or gallery_image.title }}">',
        ).replace(
            "gallery_image.title %}<h3",
            "(gallery_image.title or gallery_image.seo_keyword) %}<h3",
        ).replace(
            "{{ gallery_image.title }}</h3>",
            "{{ gallery_image.title or gallery_image.seo_keyword }}</h3>",
        )
        block.save(ignore_permissions=True)
