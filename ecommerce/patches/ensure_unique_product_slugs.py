import re

import frappe


def _slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-") or "product"


def execute():
    """Give duplicate legacy products deterministic, website-unique paths."""
    products = frappe.get_all(
        "Ecommerce Product",
        fields=["name", "website", "product_name", "slug", "creation"],
        order_by="website asc, creation asc, name asc",
    )
    used_by_website = {}
    changed_websites = set()

    for product in products:
        website_key = str(product.website or "")
        used = used_by_website.setdefault(website_key, set())
        base_slug = _slugify(product.slug or product.product_name or product.name)
        candidate = base_slug

        if candidate in used:
            candidate = f"{base_slug}-{_slugify(product.name)}"
            suffix = 2
            while candidate in used:
                candidate = f"{base_slug}-{suffix}"
                suffix += 1

        used.add(candidate)
        if product.slug != candidate:
            frappe.db.set_value(
                "Ecommerce Product",
                product.name,
                "slug",
                candidate,
                update_modified=False,
            )
            changed_websites.add(product.website)

    for website in changed_websites:
        _republish_website_pages(website)


def _republish_website_pages(website):
    """Refresh generated HTML so repaired product paths take effect immediately."""
    from ecommerce.api import update_publish_data

    pages = frappe.get_all(
        "Ecommerce Page",
        filters={"website_id": website},
        fields=["name", "page", "field_value"],
    )
    for page in pages:
        field_value = page.field_value
        if isinstance(field_value, str):
            field_value = frappe.parse_json(field_value) or {}
        result = update_publish_data(
            _page_name=page.name,
            _title=page.page,
            _field_value=field_value or {},
            _commit=False,
        )
        if not isinstance(result, dict) or result.get("status") != "success":
            message = result.get("message") if isinstance(result, dict) else None
            frappe.throw(
                f"Unable to republish Builder Page {page.name}: "
                f"{message or 'Unknown rendering error'}"
            )
